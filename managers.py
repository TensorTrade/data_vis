"""
This script contains classes for account management as well as listening
and responding to Twitter info.
"""

import json
import random
import time
import threading
import requests
from functions import *  # Useful functions for Twitter and scraping stuff.
# For identifying offensive tweets.
from offensive import offensive as offensive


# Perhaps using a database would be better if frequent updation is needed.

# This gets links to files containing relevant data.
with open('links.json', 'r') as links_file:
    LINKS = json.loads(links_file.read())
# Gets IDs of bad people.
with requests.get(LINKS['bads']) as bads_file:
    BADS = [int(user_id) for user_id in bads_file.text.split('\n')]


class StreamThread(threading.Thread):
    """
    This class is to be used for listening specific people on Twitter and
    respond to them as soon as they tweet.
    """

    def __init__(self, stream_handler, account_handler):
        threading.Thread.__init__(self)
        self.ts = stream_handler
        self.t = account_handler

    def run(self):
        """This is the function for main listener loop."""
        # TBD: Add periodic data checks to get updated data for messages, bads.
        # Listen to bad people.
        print("Streamer started.")
        listener = self.ts.statuses.filter(
            follow=','.join(
                [str(bad) for bad in BADS]
            )
        )
        while True:
            try:
                tweet = next(listener)
                # Check if the tweet is original - workaroud for now.
                # Listener also gets unwanted retweets, replies and so on."""
                if tweet['user']['id'] not in BADS:
                    continue

                # Gets messages to tweet.
                with requests.get(LINKS['messages']) as messages_file:
                    MESSAGES = messages_file.text.split('\n')[:-1]
                # If they tweet, send them a kinda slappy reply.
                """
                reply(self.t, 
                    tweet['id'],
                    tweet['user']['screen_name'],
                    random.choice(messages)
                )
                max_length = 0
                for word in tweet["text"].split():  # Finds the largest word.
                    if len(word) > max_length:
                        max_length = len(word)
                        max_word = word
                        """

                # Searches for a related news, later add images.
                news_content = get_top_headline(tweet["user"]["name"])

                """
                rep_tweet = self.t.search.tweets(
                    q=tweet["user"]["name"],
                    count=1, lang="en"
                    )["statuses"][0]

                tweet_link = \
                    "https://twitter.com/"\
                    + rep_tweet["user"]["screen_name"]\
                    + "/status/"+rep_tweet["id_str"]
                """
                short_url = shorten_url(news_content[1])
                message = random.choice(MESSAGES) + " " + short_url
                reply(
                    self.t,
                    tweet['id'],
                    tweet['user']['screen_name'],
                    message
                )

                # Print tweet for logging.
                print("Tweet:")
                print_tweet(tweet)
                print('*'*33+ "\nReply:")
                print(message)
                print()
            except Exception as e:
                # Loop shouldn't stop if error occurs, and exception should be
                # logged.
                print(json.dumps(tweet, indent=4))
                print(e)
                print('-*-'*33)


class AccountThread(threading.Thread):
    """Account thread manages favoriting, retweeting and following people who
    tweet interesting stuff."""
    def __init__(self, handler):
        threading.Thread.__init__(self)
        self.t = handler

    def run(self):
        """Main loop to handle account retweets, follows, and likes."""

        print("Account Manager started.")
        while 1:
            with requests.get(LINKS['keywords']) as keywords_file:
                words = keywords_file.text.split('\n')
            word = random.choice(words)
            # Add '-from:TheRealEqualizer' in the following line.
            tweets = self.t.search.tweets(
                q=word, count=199,
                lang="en"
                )["statuses"]  # Understand OR operator.

            with requests.get(LINKS['screen_name']) as screen_name_file:
                screen_name = screen_name_file.text.strip()

            friends_ids = self.t.friends.ids(screen_name=screen_name)["ids"]
            if len(friends_ids) > 4000:
                
                # To unfollow old follows because Twitter doesn't allow a large
                # following / followers ratio for people with less followers.
                # Using 4000 instead of 5000 for 'safety', so that I'm able to
                # follow some interesting people manually even after a bot
                # crash.

                # Perhaps 1000 is the upper limit of mass unfollow in one go.
                
                for _ in range(1000):
                    unfollow(self.t, friends_ids.pop())

            for tweet in tweets:
                try:
                    if re.search(offensive, tweet["text"]) is None:
                        #print("Search tag:", word)
                        #print_tweet(tweet)
                        #print()
                        fav_tweet(self.t, tweet)
                        retweet(self.t, tweet)
                        #self.t.friendships.create(_id=tweet["user"]["id"])
                        #if "retweeted_status" in tweet:
                        #    op = tweet["retweeted_status"]["user"]
                        #    self.t.friendships.create(_id=op["id"])
                        #print()
                except Exception as e:
                    print(e)
                time.sleep(61)
