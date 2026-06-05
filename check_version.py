import os
import requests
from bs4 import BeautifulSoup
import re

# 配置信息
TG_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
VERSION_FILE = "last_version.txt"

def get_s25_ultra_specific_link(variant_page_url):
    """第二层解析：深入变体列表，为 S25 Ultra 寻找最完美的专属 `-31` 下载链接"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(variant_page_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 寻找表格中所有的行
        rows = soup.find_all('div', class_='table-row')
        best_url = None
        
        for row in rows:
            text_content = row.text.lower()
            # 锁定针对 S25 Ultra 的硬性条件：
            # 1. 包含正统的 -31 后缀（或者是完全适配顶级旗舰的特定包）
            # 2. 必须是现代系统 Android 12+ 或 12L+ 
            if "-31" in text_content and ("android 12" in text_content or "12l" in text_content):
                a_tag = row.find('a', class_='accent_color')
                if a_tag and 'href' in a_tag.attrs:
                    best_url = "https://www.apkmirror.com" + a_tag['href']
                    print(f"🎯 成功在内层帮 S25 Ultra 锁定了最佳变体链接: {best_url}")
                    return best_url
                    
        # 兜底策略：如果没有正好找到-31，就抓取列表里的第一个通用(universal)现代版本
        if not best_url:
            for row in rows:
                text_content = row.text.lower()
                if "universal" in text_content and ("android 12" in text_content or "12l" in text_content):
                    a_tag = row.find('a', class_='accent_color')
                    if a_tag and 'href' in a_tag.attrs:
                        return "https://www.apkmirror.com" + a_tag['href']
    except Exception as e:
        print(f"⚠️ 内层变体解析失败: {e}")
    return variant_page_url

def get_latest_play_store_version():
    """第一层解析：抓取主页，获取版本号和过滤车机测试版"""
    url = "https://www.apkmirror.com/apk/google-inc/google-play-store/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        variants = soup.find_all('a', class_='fontBlack')
        
        for variant in variants:
            title = variant.text.strip()
            title_lower = title.lower()
            
            if "automotive" in title_lower or "wear os" in title_lower or "android tv" in title_lower or "beta" in title_lower:
                continue
                
            if "google play store" in title_lower:
                raw_version = title.replace("Google Play Store", "").replace("google play store", "").strip()
                clean_version = raw_version.split(" ")[0] if " " in raw_version else raw_version
                
                # 拿到总列表页链接后，直接派遣爬虫进入第二层去抓取 S25U 的专属包
                base_variant_url = "https://www.apkmirror.com" + variant['href']
                final_download_link = get_s25_ultra_specific_link(base_variant_url)
                
                return clean_version, final_download_link
    except Exception as e:
        print(f"💥 外层解析发生错误: {e}")
    return None, None

def send_tg_message(text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": False}
    requests.post(url, json=payload)

def main():
    current_version, dl_link = get_latest_play_store_version()
    if not current_version:
        return

    last_version = ""
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r") as f:
            last_version = f.read().strip()

    if current_version != last_version:
        message = (
            f"📱 *发现 Google Play 商店「S25 Ultra 专属正式版」更新！*\n\n"
            f"📊 *最新版本:* `{current_version}-31` (Android 12+)\n\n"
            f"🔥 *[点击直达 S25U 最佳变体下载页]*({dl_link})\n\n"
            f"💡 *提示:* 进网页后直接点那个绿色的 `DOWNLOAD APK` 即可。安装时记得断开手机代理隧道。"
        )
        send_tg_message(message)
        
        with open(VERSION_FILE, "w") as f:
            f.write(current_version)
        print(f"新版本 {current_version} 推送成功！")
    else:
        print("当前已是最新版，无需推送。")

if __name__ == "__main__":
    main()
