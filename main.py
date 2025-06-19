import tweepy
import openai
import os
import time
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# === ENVIRONMENT VARIABLES ===
# Use Render/Secrets Manager or .env to set these
api_key = os.getenv("TWITTER_API_KEY")
api_secret = os.getenv("TWITTER_API_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_secret = os.getenv("TWITTER_ACCESS_SECRET")
openai.api_key = os.getenv("OPENAI_API_KEY")
google_sheet_name = os.getenv("GOOGLE_SHEET_NAME")

# === TWITTER AUTH ===
auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_secret)
twitter = tweepy.API(auth)

# === GOOGLE SHEETS AUTH ===
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open(google_sheet_name).sheet1

# === KAITO PROJECTS TO RANDOMIZE ===
kaito_projects = [
    "Mira", "Noya", "Kaito Core", "Kaito Alpha", "Kaito Hub"
]

# === GENERATE GPT PROMPT ===
def generate_prompt(project):
    return (
        f"Generate a short, hype-style tweet about the Kaito project '{project}'. "
        f"Keep it under 280 characters. Include hashtags like #KaitoAI, #Web3, and #CryptoAI."
    )

# === CALL OPENAI TO GENERATE A POST ===
def get_ai_post(project):
    try:
        prompt = generate_prompt(project)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a Twitter strategist for a Web3 AI project."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"❌ OpenAI Error: {e}")
        return None

# === POST TO TWITTER ===
def post_to_twitter(text):
    try:
        twitter.update_status(text)
        print(f"✅ Posted to Twitter: {text}")
    except Exception as e:
        print(f"❌ Twitter Post Error: {e}")

# === LOG TO GOOGLE SHEETS ===
def log_to_sheets(project, tweet):
    try:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([timestamp, project, tweet])
        print("📄 Logged to Google Sheets")
    except Exception as e:
        print(f"❌ Logging Error: {e}")

# === MAIN FUNCTION ===
def main():
    project = random.choice(kaito_projects)
    print(f"🧠 Generating tweet for project: {project}")
    tweet = get_ai_post(project)
    if tweet:
        post_to_twitter(tweet)
        log_to_sheets(project, tweet)

# === OPTIONAL: AUTOMATED SCHEDULING LOOP ===
# Uncomment below if running as a worker (not cron job)
# while True:
#     main()
#     time.sleep(3600)

# === RUN SCRIPT ONCE ===
if __name__=="__main__":
  main()
