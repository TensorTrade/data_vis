#!/usr/bin/env python3
import json
import os
import random
import requests
from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream
# Maybe we can utilize 'RT to win' stuff by this same script.

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

def main():
    """This is the function for main listener loop."""
    # Listen to bad people.
    listener = ts.statuses.filter(follow=','.join([str(bad) for bad in bads]))
    while True:
        tweet = next(listener)
        """
        Check if the tweet is original - workaroud for now. listener also gets
        unwanted retweets, replies and so on.
        """
        if tweet['user']['id'] not in bads:
            continue
        # If they tweet, send them a kinda slappy reply.
        try:
            reply(
                tweet['id'],
                tweet['user']['screen_name'],
                random.choice(messages)
            )
        except Exception as e:  # So that loop doesn't stop if error occurs.
            print(e)
        # Print tweet for logging.
        print_tweet(tweet)
        """You yourself are an embodiment of fake news. <some random link>"""

# Execute the main() function only if script is executed directly.
if __name__ == "__main__":
    main()
