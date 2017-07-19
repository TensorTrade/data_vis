#!/usr/bin/env python3
from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream
# Maybe we can utilize 'RT to win' stuff by this same script.

oauth = OAuth(
    os.environ['ACCESS_TOKEN'],
    os.environ['ACCESS_SECRET'],
    os.environ['CONSUMER_KEY'],
    os.environ['CONSUMER_SECRET']
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


t = Twitter(auth=oauth)
ts = TwitterStream(auth=oauth)
bads = [25073877, 72931184]  # IDs of bad people

# Listen to bad people.
# If they tweet, send them a kinda slappy reply.
"""You are an embodiment of fake news. <some random link>"""
# Maybe we can utilize 'RT to win' stuff by this same script.
