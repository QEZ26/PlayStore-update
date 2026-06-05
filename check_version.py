import os
import requests
from bs4 import BeautifulSoup

TG_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
VERSION_FILE = "last_version.txt"

def get_s25_ultra_specific_link(variant_page_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(variant_page_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('div', class_='table-row')
        
        for row in rows:
            text_content = row.text.lower()
            if "-31" in text_content and ("android 12" in text_content or "12l" in text_content):
                a_tag = row.find('a', class_='accent_color')
                if a_tag and 'href' in a_tag.attrs:
                    return "https://www.apkmirror.com" + a_tag['href']
                    
        for row in rows:
            text_content = row.text.lower()
            if "universal" in text_content and ("android 12" in text_content or "12l" in text_content):
                a_tag = row.find('a', class_='accent_color')
                if a_tag and 'href' in a_tag.attrs:
                    return "https://www.apkmirror.com" + a_tag['href']
    except:
        pass
    return variant_page_url

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
            title_lower = title.lower()
            
            if "automotive" in title_lower or "wear os" in title_lower or "android tv" in title_lower or "beta" in title_lower:
                continue
                
            if "google play store" in title_lower:
                raw_version = title.replace("Google Play Store", "").replace("google play store", "").strip()
                clean_version = raw_version.split(" ")[0] if " " in raw_version else raw_version
                
                base_variant_url = "https://www.apkmirror.com" + variant['href']
                final_download_link = get_s25_ultra_specific_link(base_variant_url)
                
                return clean_version, final_download_link
    except:
        pass
    return None, None

def send_tg_message(text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def main():
    current_version, dl_link = get_latest_play_store_version()
    if not current_version:
        return

    last_version = ""
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r") as f:
            last_version = f.read().strip()

    print(f"DEBUG: 缓存中的版本是 [{last_version}], 抓到的新版本是 [{current_version}]")

    if current_version != last_version:
        message = (
            f"📱 *发现 Google Play 商店更新！*\n\n"
            f"📊 *最新版本:* [{current_version}-31 (Android 12+)]({dl_link})"
        )
        send_tg_message(message)
        
        # 本地生成文件，交由外部的 GitHub Action 统一进行官方云缓存
        with open(VERSION_FILE, "w") as f:
            f.write(current_version)
    else:
        print("版本一致，跳过发送。")

if __name__ == "__main__":
    main()
