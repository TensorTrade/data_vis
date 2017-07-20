#!/usr/bin/env python3
import os
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

t = Twitter(auth=oauth)
ts = TwitterStream(auth=oauth)
bads = [25073877, 72931184]  # IDs of bad people

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
    reply(
        tweet['id'],
        tweet['user']['screen_name'],
        "You yourself are an embodiment of fake news."
    )
    # Print tweet for logging.
    print_tweet(tweet)
    """You yourself are an embodiment of fake news. <some random link>"""

# Maybe we can utilize 'RT to win' stuff by this same script.
