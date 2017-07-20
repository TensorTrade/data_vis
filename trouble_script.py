#!/usr/bin/env python3
"""
This script gives people what they deserve on Twitter, and tries luck in 'RT
to win' competititons.
"""
import json
import os
import random
import requests
import time
import threading
from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream
# Maybe we can utilize 'RT to win' stuff by this same script.

# TBD: Use multithreading to make the bot better.

try:
    oauth = OAuth(
        os.environ['TW_ACCESS_TOKEN'],
        os.environ['TW_ACCESS_SECRET'],
        os.environ['TW_CONSUMER_KEY'],
        os.environ['TW_CONSUMER_SECRET']
    )
except KeyError:  # For local tests.
    with open('.env', 'r') as secret:
        exec(secret.read())
        oauth = OAuth(
            ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET
        )

t = Twitter(auth=oauth)
ts = TwitterStream(auth=oauth)

# Perhaps using a database would be better if frequent updation is needed.

# This gets links to files containing relevant data.
with open('links.txt', 'r') as links_file:
    links = json.loads(links_file.read())
# Gets IDs of bad people.
with requests.get(links['bads']) as bads_file:
    bads = [int(user_id) for user_id in bads_file.text.split('\n')[:-1]]
# Gets messages to tweet.
with requests.get(links['messages']) as messages_file:
    messages = messages_file.text.split('\n')[:-1]

def reply(tweet_id, user_name, msg):
    """
    Sends msg as reply to the tweet whose id is passed.
    user_name of the tweet's author is required as per Twitter API docs.
    """

    t.statuses.update(
        status='@%s %s' % (user_name, msg),
        in_reply_to_status_id=tweet_id
        )


def print_tweet(tweet):
    print(tweet["user"]["name"])
    print(tweet["user"]["screen_name"])
    print(tweet["created_at"])
    print(tweet["text"])
    hashtags = []
    hs = tweet["entities"]["hashtags"]
    for h in hs:
        hashtags.append(h["text"])
    print(hashtags)


def fav_tweet(tweet):
     try:
             result = t.favorites.create(_id=tweet['id'])
             return 1
     except TwitterHTTPError:
             return 0


def retweet(tweet):
     try:
             t.statuses.retweet._id(_id=tweet["id"])
             return 1
     except TwitterHTTPError:
             return 0


def quote_tweet(tweet, text): #may not work for long links because of 140-limit. Can be improved.
     id = tweet["id"]
     sn = tweet["user"]["screen_name"]
     link = "https://twitter.com/%s/status/%s" %(sn, id)
     try:
             string = text + " " + link
             t.statuses.update(status=string)
             return 1
     except TwitterHTTPError:
             return 0

class StreamThread(threading.Thread):
    def __init__(self, handler):
        threading.Thread.__init__(self)
        self.ts = handler

    def run(self):
        """This is the function for main listener loop."""
        # TBD: Add periodic data checks to get updated data for messages, bads.
        # Listen to bad people.
        listener = self.ts.statuses.filter(
            follow=','.join(
                [str(bad) for bad in bads]
            )
        )
        while True:
            try:
                tweet = next(listener)
                """
                Check if the tweet is original - workaroud for now. listener
                also gets unwanted retweets, replies and so on.
                """
                if tweet['user']['id'] not in bads:
                    print("Ignored from:", tweet['user']['screen_name'])
                    continue
                # Gets messages to tweet.
                with requests.get(links['messages']) as messages_file:
                    messages = messages_file.text.split('\n')[:-1]
                # If they tweet, send them a kinda slappy reply.
                reply(
                    tweet['id'],
                    tweet['user']['screen_name'],
                    random.choice(messages)
                )
                # Print tweet for logging.
                print()
                print_tweet(tweet)
            except Exception as e:  # So that loop doesn't stop if error occurs.
                print(json.dumps(tweet, indent=4))
                print(e)
            print()
            """You yourself are an embodiment of fake news. <some random link>"""


class AccountThread(threading.Thread):
    def __init__(self, handler):
        threading.Thread.__init__(self)
        self.t = handler

    def run(self):
        """Main loop to handle account retweets, follows, and likes."""
        while 1:
            with requests.get(links['keywords']) as keywords_file:
                keywords = keywords_file.text.split('\n')[:-1]
            word = random.choice(words)
            tweets = self.t.search.tweets(q=word+' -from:arichduvet', count=199, lang="en")["statuses"] #understand OR operator
            fr = self.t.friends.ids(screen_name="arichduvet")["ids"]
            if len(fr) > 4990: #To unfollow old follows because Twitter doesn't allow a large following / followers ratio for people with less followers.
                               #Using 5990 instead of 5000 for 'safety', so that I'm able to follow some interesting people
                               #manually even after a bot crash.
                for i in xrange(2500): #probably this is the upper limit of mass unfollow in one go
                    unfollow(fr.pop())

            for tweet in tweets:
                try:
                    if re.search(offensive, tweet["text"]) == None:
                        print("Search tag:", word)
                        print_tweet(tweet)
                        print()
                        print("Heart =", fav_tweet(tweet))
                        print("Retweet =", retweet(tweet))
                        self.t.friendships.create(_id=tweet["user"]["id"])
                        if "retweeted_status" in tweet:
                            op = tweet["retweeted_status"]["user"]
                            self.t.friendships.create(_id=op["id"])
                        print()
                except:
                    pass
                time.sleep(61)

# Execute the main() function only if script is executed directly.
if __name__ == "__main__":
    pass
