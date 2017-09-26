from functions import *  # Useful functions for Twitter and scraping stuff.
import json
# For identifying offensive tweets.
from offensive import offensive as offensive
import random
import requests
import time
import threading


class StreamThread(threading.Thread):
    def __init__(self, handler):
        threading.Thread.__init__(self)
        self.ts = handler

    def run(self):
        """This is the function for main listener loop."""
        # TBD: Add periodic data checks to get updated data for messages, bads.
        # Listen to bad people.
        print("Streamer started.")
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
                    continue

                # Gets messages to tweet.
                with requests.get(links['messages']) as messages_file:
                    messages = messages_file.text.split('\n')[:-1]
                # If they tweet, send them a kinda slappy reply.
                """
                reply(
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
                rep_tweet = t.search.tweets(
                    q=tweet["user"]["name"],
                    count=1, lang="en"
                    )["statuses"][0]

                tweet_link = \
                    "https://twitter.com/"\
                    + rep_tweet["user"]["screen_name"]\
                    + "/status/"+rep_tweet["id_str"]
                """
                short_url = shorten_url(news_content[1])
                message = random.choice(messages) + " " + short_url
                reply(
                    tweet['id'],
                    tweet['user']['screen_name'],
                    message
                )

                # Print tweet for logging.
                print("Tweet:")
                print_tweet(tweet)
                print('*'*33+ "\nReply:")
                print_tweet(news_content)
                print()
            except Exception as e:
                # Loop shouldn't stop if error occurs, and exception should be
                # logged.
                print(json.dumps(tweet, indent=4))
                print(e)
            print('-*-'*33)


class AccountThread(threading.Thread):
    """
    Account thread manages favoriting, retweeting and following people who
    tweet interesting stuff.
    """
    def __init__(self, handler):
        threading.Thread.__init__(self)
        self.t = handler

    def run(self):
        """Main loop to handle account retweets, follows, and likes."""
        print("Account Manager started.")
        while 1:
            with requests.get(links['keywords']) as keywords_file:
                words = keywords_file.text.split('\n')
            word = random.choice(words)
            # Add '-from:TheRealEqualizer' in the following line.
            tweets = self.t.search.tweets(
                q=word, count=199,
                lang="en"
                )["statuses"]  # Understand OR operator.

            with requests.get(links['screen_name']) as screen_name_file:
                screen_name = screen_name_file.text.strip()

            fr = t.friends.ids(screen_name=screen_name)["ids"]
            if len(fr) > 4000:
                """
                To unfollow old follows because Twitter doesn't allow a large
                following / followers ratio for people with less followers.
                Using 4000 instead of 5000 for 'safety', so that I'm able to
                follow some interesting people manually even after a bot
                crash.
                """

                """
                Perhaps 1000 is the upper limit of mass unfollow in one go.
                """
                for i in range(1000):
                    unfollow(fr.pop())

            for tweet in tweets:
                try:
                    if re.search(offensive, tweet["text"]) is None:
                        #print("Search tag:", word)
                        #print_tweet(tweet)
                        #print()
                        #print("Heart =", fav_tweet(tweet))
                        #print("Retweet =", retweet(tweet))
                        self.t.friendships.create(_id=tweet["user"]["id"])
                        if "retweeted_status" in tweet:
                            op = tweet["retweeted_status"]["user"]
                            self.t.friendships.create(_id=op["id"])
                        #print()
                except Exception as e:
                    print(e)
                time.sleep(61)