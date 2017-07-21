#!/usr/bin/env python3
"""
This script gives people what they deserve on Twitter, and tries luck in 'RT
to win' competititons.
"""
import json
import os
import random
import re
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

offensive = re.compile(
    r"\b(deaths?|dead(ly)?|die(s|d)?|hurts?|(sex(ual(ly)?)?|child)[ -]?(abused?|trafficking|"
    r"assault(ed|s)?)|injur(e|i?es|ed|y)|kill(ing|ed|er|s)?s?|wound(ing|ed|s)?|fatal(ly|ity)?|"
    r"shoo?t(s|ing|er)?s?|crash(es|ed|ing)?|attack(s|ers?|ing|ed)?|murder(s|er|ed|ing)?s?|"
    r"hostages?|(gang)?rap(e|es|ed|ist|ists|ing)|assault(s|ed)?|pile-?ups?|massacre(s|d)?|"
    r"assassinate(d|s)?|sla(y|in|yed|ys|ying|yings)|victims?|tortur(e|ed|ing|es)|"
    r"execut(e|ion|ed|ioner)s?|gun(man|men|ned)|suicid(e|al|es)|bomb(s|ed|ing|ings|er|ers)?|"
    r"mass[- ]?graves?|bloodshed|state[- ]?of[- ]?emergency|al[- ]?Qaeda|blasts?|violen(t|ce)|"
    r"lethal|cancer(ous)?|stab(bed|bing|ber)?s?|casualt(y|ies)|sla(y|ying|yer|in)|"
    r"drown(s|ing|ed|ings)?|bod(y|ies)|kidnap(s|ped|per|pers|ping|pings)?|rampage|beat(ings?|en)|"
    r"terminal(ly)?|abduct(s|ed|ion)?s?|missing|behead(s|ed|ings?)?|homicid(e|es|al)|"
    r"burn(s|ed|ing)? alive|decapitated?s?|jihadi?s?t?|hang(ed|ing|s)?|funerals?|traged(y|ies)|"
    r"autops(y|ies)|child sex|sob(s|bing|bed)?|pa?edophil(e|es|ia)|9(/|-)11|Sept(ember|\.)? 11|"
    r"genocide)\W?\b",
    flags=re.IGNORECASE) #Copyright (c) 2013-2016 Molly White
    #Above offensive compilation is not my stuff

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


def unfollow(iden):
    success = 0
    try:
        t.friendships.destroy(_id=iden)
        success += 1
    except Exception as e:
        print(e)
    #print "Unfollowed %i people." % success

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
                print('-*-'*33)
                print_tweet(tweet)
            except Exception as e:  # So that loop doesn't stop if error occurs.
                print(json.dumps(tweet, indent=4))
                print(e)
            print('-*-'*33)
            """You yourself are an embodiment of fake news. <some random link>"""


class AccountThread(threading.Thread):
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
            tweets = self.t.search.tweets(q=word, count=199, lang="en")["statuses"] #understand OR operator
            '''
            fr = t.friends.ids(screen_name="screen_name_here")["ids"]
            if len(fr) > 4990: #To unfollow old follows because Twitter doesn't allow a large following / followers ratio for people with less followers.
                               #Using 5990 instead of 5000 for 'safety', so that I'm able to follow some interesting people
                               #manually even after a bot crash.
                for i in range(2500): #probably this is the upper limit of mass unfollow in one go
                    unfollow(fr.pop())
            '''
            for tweet in tweets:
                try:
                    if re.search(offensive, tweet["text"]) is None:
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
                except Exception as e:
                    print(e)
                time.sleep(61)


def main():
    """Main function to handle different activites of the account."""
    streamer = StreamThread(ts)  # For the troubling part.
    account_manager = AccountThread(t)  # For retweets, likes, follows.
    streamer.start()
    account_manager.run()

# Execute the main() function only if script is executed directly.
if __name__ == "__main__":
    main()
