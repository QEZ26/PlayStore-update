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
        
        variants = soup.find_all('a', class_='fontBlack')
        for variant in variants:
            title = variant.text.strip()
            if "Google Play Store" in title and "beta" not in title.lower() and "wear os" not in title.lower():
                version = title.replace("Google Play Store", "").strip()
                download_link = "https://www.apkmirror.com" + variant['href']
                return version, download_link
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

    if current_version != last_version:
        message = (
            f"🔔 *发现 Google Play 商店新稳定版！*\n\n"
            f"📦 *最新版本:* `{current_version}`\n"
            f"🔗 [点击前往 APKMirror 下载最新版]({dl_link})\n\n"
            f"💡 *提示:* 请使用 APKMirror Installer 配合安装此 APKS 文件，安装时请记得断开代理。"
        )
        send_tg_message(message)
        
        with open(VERSION_FILE, "w") as f:
            f.write(current_version)
        print(f"新版本 {current_version} 推送成功！")
    else:
        print("当前已是最新版，无需推送。")

if __name__ == "__main__":
    main()
