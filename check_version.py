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
        for variant in variants:
            title = variant.text.strip()
            title_lower = title.lower()
            
            # 严格过滤掉测试版、车机版、手表版、电视版
            if "beta" in title_lower or "automotive" in title_lower or "wear os" in title_lower or "android tv" in title_lower:
                continue
                
            if "google play store" in title:
                # 提取出纯粹的版本号，例如把 "Google Play Store 51.6.23-31 [0] [PR] ..." 变成 "51.6.23-31"
                raw_version = title.replace("Google Play Store", "").strip()
                # 截取到空格为止，去掉后面多余的 [0] [PR] 等系统后缀，只保留干净的版本号
                clean_version = raw_version.split(" ")[0] if " " in raw_version else raw_version
                
                download_link = "https://www.apkmirror.com" + variant['href']
                return clean_version, download_link
    except Exception as e:
        print(f"解析失败: {e}")
    return None, None

def send_tg_message(text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def main():
    current_version, dl_link = get_latest_play_store_version()
    if not current_version:
        print("未获取到新版本。")
        return

    last_version = ""
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r") as f:
            last_version = f.read().strip()

    # 只要当前抓取到的手机稳定版和上次记录的不同，就触发推送
    if current_version != last_version:
        message = (
            f"🚀 *发现 Google Play 商店「手机正式版」更新！*\n\n"
            f"📊 *最新版本号:* `{current_version}`\n\n"
            f"🔗 [点击前往 APKMirror 下载此版本]({dl_link})\n\n"
            f"💡 *提示:* 下载后请使用 APKMirror Installer 配合安装。安装时请记得断开手机的代理隧道。"
        )
        send_tg_message(message)
        
        # 将最新的正确版本号写入记录文件
        with open(VERSION_FILE, "w") as f:
            f.write(current_version)
        print(f"新版本 {current_version} 推送成功！")
    else:
        print("当前已是最新版，无需推送。")

if __name__ == "__main__":
    main()
