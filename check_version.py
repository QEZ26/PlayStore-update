import os
import requests
from bs4 import BeautifulSoup

# 配置信息
TG_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
VERSION_FILE = "last_version.txt"

def get_latest_play_store_version():
    url = "https://www.apkmirror.com/apk/google-inc/google-play-store/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 寻找列表中所有的版本条目
        variants = soup.find_all('a', class_='fontBlack')
        print(f"📡 网页请求成功，共找到 {len(variants)} 个版本链接。开始过滤...")
        
        for variant in variants:
            title = variant.text.strip()
            title_lower = title.lower()
            
            print(f"🔍 正在检查条目: {title}")
            
            # 排除车机版、手表版、电视版、测试版
            if "automotive" in title_lower or "wear os" in title_lower or "android tv" in title_lower or "beta" in title_lower:
                print("❌ 属于非手机版或测试版，跳过。")
                continue
                
            if "google play store" in title_lower:
                # 提取纯版本号
                raw_version = title.replace("Google Play Store", "").replace("google play store", "").strip()
                # 截取到空格为止
                clean_version = raw_version.split(" ")[0] if " " in raw_version else raw_version
                
                download_link = "https://www.apkmirror.com" + variant['href']
                print(f"✅ 成功锁定手机正式版！版本号: {clean_version}")
                return clean_version, download_link
    except Exception as e:
        print(f"💥 解析发生严重错误: {e}")
    return None, None

def send_tg_message(text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    r = requests.post(url, json=payload)
    print(f"📤 TG 发送状态码: {r.status_code}, 响应内容: {r.text}")

def main():
    current_version, dl_link = get_latest_play_store_version()
    if not current_version:
        print("🛑 最终结论: 未能成功从网页匹配到任何有效的手机正式版。")
        return

    last_version = ""
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r") as f:
            last_version = f.read().strip()
    print(f"💾 历史记录版本: '{last_version}' | 当前抓取版本: '{current_version}'")

    if current_version != last_version:
        message = (
            f"🚀 *发现 Google Play 商店「手机正式版」更新！*\n\n"
            f"📊 *最新版本号:* `{current_version}`\n\n"
            f"🔗 [点击前往 APKMirror 下载此版本]({dl_link})\n\n"
            f"💡 *提示:* 下载后请使用 APKMirror Installer 配合安装。安装时请记得断开手机的代理隧道。"
        )
        send_tg_message(message)
        
        with open(VERSION_FILE, "w") as f:
            f.write(current_version)
        print(f"✨ 新版本 {current_version} 处理完毕，文件已记录。")
    else:
        print("😴 两个版本号一致，当前已是最新版，无需推送。")

if __name__ == "__main__":
    main()
