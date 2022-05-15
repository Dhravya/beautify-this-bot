import time
import urllib3
from os import environ as env 

import tweepy
from dotenv import load_dotenv

load_dotenv()

class GetPoetry:

    def get_poem(self, id_, savepath="tweet.png"):
        poem_link = "https://beautify.dhravya.dev/tweet/" + str(id_)

        http = urllib3.PoolManager()
        r = http.request('GET', poem_link)
        with open(savepath, 'wb') as f:
            f.write(r.data)
        return savepath

class Twitter:
    def __init__(self) -> None:
        auth = tweepy.OAuth1UserHandler(access_token=env["TWITTER_ACCESS_TOKEN"],
                                access_token_secret=env["TWITTER_ACCESS_TOKEN_SECRET"],
                                consumer_key=env["CONSUMER_KEY"],
                                consumer_secret=env["CONSUMER_SECRET"])
        self.api = tweepy.API(auth, wait_on_rate_limit=True)
        self.poetry = GetPoetry()
        self.start_time = time.time()

    def tweet(self, og_tweet_id, mention_id, mention_name):
        self.poetry.get_poem(og_tweet_id)

        self.api.update_status_with_media(f"@{mention_name} Here's your beautiful screenshot of the tweet", filename="tweet.png" ,in_reply_to_status_id=mention_id)

    def start_listening_for_mentions(self, since_id):
        new_since_id = since_id

        for mention in tweepy.Cursor(self.api.mentions_timeline, 
                                    since_id=since_id, 
                                    tweet_mode="extended").items():
            # If the tweet was made before start_time, skip it
            if mention.created_at.timestamp() < self.start_time:
                continue

            if not mention.in_reply_to_status_id:
                continue

            # If its a reply to my tweet, skip
            if mention.in_reply_to_user_id == 1518643742894608390:
                continue
            
            if ("screenshot" in mention.full_text.lower() 
                or "beautify" in mention.full_text.lower()):
                
                new_since_id = max(mention.id, new_since_id)

                og_tweet = self.api.get_status(mention.in_reply_to_status_id)
                self.tweet(og_tweet.id, mention.id, mention.user.screen_name)
        
        return new_since_id

if __name__ == "__main__":
    twitter = Twitter()
    print("Running...")
    since_id = 1
    while True:
        since_id = twitter.start_listening_for_mentions(since_id)
        time.sleep(10)
