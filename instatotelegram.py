import os
import instaloader
import requests
import datetime
import pytz

# 🔹 Telegram Bot Credentials
TELEGRAM_BOT_TOKEN = os.getenv("7625788120:AAETLQM6wUKQmz0emaK1ua6ktkW0wp51oGk")
TELEGRAM_CHAT_ID = os.getenv("3510991")

# 🔹 Instagram Users to Track
INSTAGRAM_USERS = ["sashaux", "margo.pho"]

# 🔹 Timezone Setup
TIMEZONE = pytz.utc  # Change if needed (e.g., pytz.timezone("Europe/Berlin"))
YESTERDAY = datetime.datetime.now(TIMEZONE) - datetime.timedelta(days=1)

# 🔹 Instaloader Initialization
L = instaloader.Instaloader(download_pictures=True, download_videos=True, filename_pattern="{target}_{date_utc}")

def send_media_to_telegram(file_path):
    """Send images and videos to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    with open(file_path, "rb") as file:
        response = requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID}, files={"document": file})
    return response.json()

def download_and_send_stories():
    """Download and send Instagram Stories"""
    for username in INSTAGRAM_USERS:
        print(f"📥 Downloading stories for {username}...")
        try:
            L.download_stories(userids=[username], filename_target=f"{username}_stories")
            for file in os.listdir():
                if file.startswith(username) and file.endswith((".jpg", ".mp4")):
                    print(f"📤 Sending {file} to Telegram...")
                    send_media_to_telegram(file)
                    os.remove(file)  # Delete after sending
        except Exception as e:
            print(f"❌ Error downloading stories for {username}: {e}")

def download_and_send_posts():
    """Download and send Instagram posts from yesterday onward"""
    for username in INSTAGRAM_USERS:
        print(f"📥 Downloading posts for {username}...")
        try:
            profile = instaloader.Profile.from_username(L.context, username)
            for post in profile.get_posts():
                post_date = post.date.replace(tzinfo=pytz.utc)  # Convert to UTC
                if post_date >= YESTERDAY:
                    print(f"✅ Found new post from {username} at {post_date}")
                    L.download_post(post, target=username)
                    for file in os.listdir(username):
                        if file.endswith((".jpg", ".mp4")):
                            print(f"📤 Sending {file} to Telegram...")
                            send_media_to_telegram(os.path.join(username, file))
                            os.remove(os.path.join(username, file))
        except Exception as e:
            print(f"❌ Error downloading posts for {username}: {e}")

if __name__ == "__main__":
    download_and_send_stories()
    download_and_send_posts()
