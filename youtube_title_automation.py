import os
import re
import json
import subprocess
from datetime import date
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

VIDEO_ID = "9MyMovWe6Ag"
TITLE_FORMAT = "هو الفيديو ده عنده ({views})مشاهده؟"
SAFE_DAILY_LIMIT = 180
STATE_FILE = "state.json"

today = str(date.today())
if os.path.exists(STATE_FILE):
    with open(STATE_FILE) as f:
        state = json.load(f)
else:
    state = {}

if state.get("date") != today:
    state = {"date": today, "updates_today": 0}

creds = Credentials(None, refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"],
    client_id=os.environ["GOOGLE_CLIENT_ID"], client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
    token_uri="https://oauth2.googleapis.com/token")
youtube = build("youtube", "v3", credentials=creds)

video_response = youtube.videos().list(part="snippet,statistics", id=VIDEO_ID).execute()
video = video_response["items"][0]
snippet = video["snippet"]
current_views = video["statistics"]["viewCount"]

old_number = re.search(r"\d+", snippet["title"].replace(",", ""))
old_number = old_number.group() if old_number else None

if old_number == current_views:
    print(f"مفيش تغيير، {current_views} مشاهدة.")
elif state["updates_today"] >= SAFE_DAILY_LIMIT:
    print(f"وصلنا للحد الآمن اليومي ({SAFE_DAILY_LIMIT} تحديث). هنستنى رجوع الكوته بالليل.")
else:
    snippet["title"] = TITLE_FORMAT.format(views=current_views)
    youtube.videos().update(part="snippet", body={"id": VIDEO_ID, "snippet": snippet}).execute()
    state["updates_today"] += 1
    print(f"اتحدث لـ: {snippet['title']} (تحديث رقم {state['updates_today']} النهاردة)")

with open(STATE_FILE, "w") as f:
    json.dump(state, f)

subprocess.run(["git", "config", "user.email", "bot@github.com"])
subprocess.run(["git", "config", "user.name", "Auto Bot"])
subprocess.run(["git", "add", STATE_FILE])
subprocess.run(["git", "commit", "-m", "update state", "--allow-empty"])
subprocess.run(["git", "push"])
