"""
This script contains classes for account management as well as listening
and responding to Twitter info.
"""

import json
import random
import re
import time
import threading
# import nlp_sent
import requests
from twilio.rest import Client
import datetime
import time
import functions  # Useful functions for Twitter and scraping stuff.
# For identifying offensive tweets.
from offensive import OFFENSIVE
import sqlite3

TWILIO_PHONE_NUMBER = "+17652337030"
client = Client("AC80194c1e64a8c61119cf671b9f727e2b", "9b76cdb656f6f723200279daec2575a4")
DIAL_NUMBERS=['+919660923531']

def message_numbers(numbers_list, body):
    for number in numbers_list:
        client.messages.create(to=number, from_=TWILIO_PHONE_NUMBER, body="body", method="GET")
# Perhaps using a database would be better if frequent updation is needed.
# This gets links to files containing relevant data.
# Add hashtabgs to tweets - they generate more views.
with open('links.json', 'r') as links_file:
    LINKS = json.loads(links_file.read())
# Gets IDs of bad people.
with requests.get(LINKS['bads']) as bads_file:
    BADS = [int(user_id) for user_id in bads_file.text.split('\n')]

sentiments = list()

class StreamThread(threading.Thread):
    """
    This class is to be used for listening specific people on Twitter and
    respond to them as soon as they tweet.
    """

    def __init__(self, stream_handler, account_handler):
        threading.Thread.__init__(self)
        self.stream_handler = stream_handler
        self.handler = account_handler
        self.start_time=time.time()
        self.duration = 30

    def run(self):
        """This is the function for main listener loop."""
        # TBD: Add periodic data checks to get updated data for messages, bads.
        # Listen to bad people.
        print("Streamer started.")
        listener = self.stream_handler.statuses.filter(track='Google')
        
        while True:
            try:
                tweet = next(listener)
                curr_time = time.time()
                if (curr_time - self.start_time) > self.duration:
                    #Add code here to send sms
                    self.start_time=time.time()
                    message_numbers(DIAL_NUMBERS, tweet['text'])
                    if sum(sentiments)>0:
                        pass
                    else:
                        pass

                # Check if the tweet is original - workaroud for now.
                # Listener also gets unwanted retweets, replies and so on."""
                if tweet['user']['id'] not in BADS:
                    continue
                # Gets messages to tweet.
                with requests.get(LINKS['messages']) as messages_file:
                    messages = messages_file.text.split('\n')[:-1]
                self.mynlp = nlp() 
                sentiments.append(mynlp.get_tweet_sentiment(messages))
                # If they tweet, send them a kinda slappy reply.

                # reply(self.handler,
                #     tweet['id'],
                #     tweet['user']['screen_name'],
                #     random.choice(messages)
                # )
                # max_length = 0
                # for word in tweet["text"].split():  # Finds the largest word.
                #     if len(word) > max_length:
                #         max_length = len(word)
                #         max_word = word

                # Searches for a related news, later add images.
                news_content = functions.get_top_headline(tweet["user"]["name"])

                # rep_tweet = self.handler.search.tweets(
                #     q=tweet["user"]["name"],
                #     count=1, lang="en"
                #     )["statuses"][0]

                # tweet_link = \
                #     "https://twitter.com/"\
                #     + rep_tweet["user"]["screen_name"]\
                #     + "/status/"+rep_tweet["id_str"]

                short_url = functions.shorten_url(news_content[1])
                # message = random.choice(messages) + " " + short_url
                # Instead of a catchy but unrelated text, tweet the headline
                # itself with the short link.
                with open("messages.txt") as f:
                    message = random.choice(
                        f.read().split()
                        ) + " " + short_url
                functions.reply(
                    self.handler,
                    tweet['id'],
                    tweet['user']['screen_name'],
                    message
                )

                # Print tweet for logging.
                print("Tweet:")
                functions.print_tweet(tweet)
                print('*'*33+ "\nReply:")
                print(message)
                print()
            except Exception as exception:
                # Loop shouldn't stop if error occurs, and exception should be
                # logged.
                print(json.dumps(tweet, indent=4))
                print(exception)
                print('-*-'*33)


class AccountThread(threading.Thread):
    """Account thread manages favoriting, retweeting and following people who
    tweet interesting stuff."""
    def __init__(self, handler):
        threading.Thread.__init__(self)
        self.handler = handler

    def run(self):
        """Main loop to handle account retweets, follows, and likes."""

        print("Account Manager started.")
        while 1:
            with requests.get(LINKS['keywords']) as keywords_file:
                words = keywords_file.text.split('\n')
            word = random.choice(words)
            # Add '-from:TheRealEqualizer' in the following line.
            tweets = self.handler.search.tweets(
                q=word, count=199,
                lang="en"
                )["statuses"]  # Understand OR operator.

            with requests.get(LINKS['screen_name']) as screen_name_file:
                screen_name = screen_name_file.text.strip()

            friends_ids = self.handler.friends.ids(screen_name=screen_name)["ids"]
            if len(friends_ids) > 4000:

                # To unfollow old follows because Twitter doesn't allow a large
                # following / followers ratio for people with less followers.
                # Using 4000 instead of 5000 for 'safety', so that I'm able to
                # follow some interesting people manually even after a bot
                # crash.

                # Perhaps 1000 is the upper limit of mass unfollow in one go.

                for _ in range(1000):
                    functions.unfollow(self.handler, friends_ids.pop())

            for tweet in tweets:
                try:
                    if re.search(OFFENSIVE, tweet["text"]) is None:
                        #print("Search tag:", word)
                        #print_tweet(tweet)
                        #print()
                        functions.fav_tweet(self.handler, tweet)
                        functions.retweet(self.handler, tweet)
                        #self.handler.friendships.create(_id=tweet["user"]["id"])
                        #if "retweeted_status" in tweet:
                        #    op = tweet["retweeted_status"]["user"]
                        #    self.handler.friendships.create(_id=op["id"])
                        #print()
                except Exception as exception:
                    print(exception)
                time.sleep(61)
