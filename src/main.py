import time
import random
from os import environ as env 

import tweepy
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

load_dotenv()

class GetPoetry:
    def __init__(self) -> None:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument(f"--window-size=1920,1080")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(options=options)
        self.driver.get("https://poet.so")

    def get_poem(self, link, savepath="tweet.png"):
        input_box = self.driver.find_element(by= "tag name", value="input")
        input_box.send_keys(link + u'\ue007')
        element = self.driver.find_element("xpath","//*[@data-export-hide]")

        # Waiting for the image to load
        time.sleep(10)
        element.screenshot(savepath)

    def close(self):
        self.driver.quit()


class Twitter:
    def __init__(self) -> None:
        auth = tweepy.OAuth1UserHandler(access_token=env["TWITTER_ACCESS_TOKEN"],
                                access_token_secret=env["TWITTER_ACCESS_TOKEN_SECRET"],
                                consumer_key=env["CONSUMER_KEY"],
                                consumer_secret=env["CONSUMER_SECRET"])
        self.api = tweepy.API(auth)
        self.poetry = GetPoetry()
        self.start_time = time.time()

    def tweet(self, og_tweet_url, mention_id, mention_name):
        savepath= f"images/{random.randint(1, 10)}.png"
        self.poetry.get_poem(og_tweet_url, savepath=savepath)

        self.api.update_status_with_media(f"@{mention_name} Here's your beautiful screenshot of the tweet", filename=savepath ,in_reply_to_status_id=mention_id)
        time.sleep(5)

    def start_listening_for_mentions(self, since_id):
        new_since_id = since_id

        for mention in tweepy.Cursor(self.api.mentions_timeline, since_id=since_id, tweet_mode="extended").items():
            # If the tweet was made before start_time, skip it
            if mention.created_at.timestamp() < self.start_time:
                continue

            if not mention.in_reply_to_status_id:
                continue

            # If its a reply to my tweet, skip
            if mention.in_reply_to_screen_name == "poet_this":
                continue

            new_since_id = max(mention.id, new_since_id)

            og_tweet = self.api.get_status(mention.in_reply_to_status_id)
            print(og_tweet.text) 

            og_tweet_url = og_tweet.source_url

            self.tweet(og_tweet_url, mention.id, mention.user.screen_name)
        
        return new_since_id

if __name__ == "__main__":
    twitter = Twitter()
    print("Running...")
    since_id = 1
    while True:
        since_id = twitter.start_listening_for_mentions(since_id)
        time.sleep(90)
