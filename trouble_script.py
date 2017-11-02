#!/usr/bin/env python3
"""
This script gives people what they deserve on Twitter, and tries luck in 'RT
to win' competititons.
"""
import os

import managers  # Useful classes for streaming and account handling.
from twitter import Twitter, OAuth, TwitterStream

# A different idea - use cookies to visit shortened links via visitors' devices.
# Maybe we can utilize 'RT to win' stuff by this same script.
# Use the below link for image search.
# https://www.google.co.in/search?site=imghp&tbm=isch&source=hp&biw=1280&bih=647&q=trump+funny+meme
# Also post images in replies.

try:
    OAUTH= OAuth(
        os.environ['TW_ACCESS_TOKEN'],
        os.environ['TW_ACCESS_SECRET'],
        os.environ['TW_CONSUMER_KEY'],
        os.environ['TW_CONSUMER_SECRET']
    )
    SHORTE_ST_TOKEN = os.environ['SHORTE_ST_TOKEN']
except KeyError:  # For local runs.
    with open('.env', 'r') as secret:
        exec(secret.read())
        OAUTH = OAuth(
            ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET
        )

ACCOUNT_HANDLER = Twitter(auth=OAUTH)
STREAM_HANDLER = TwitterStream(auth=OAUTH)


def main():
    """Main function to handle different activites of the account."""

    streamer = managers.StreamThread(STREAM_HANDLER, ACCOUNT_HANDLER)  # For the troubling part.
    account_manager = managers.AccountThread(ACCOUNT_HANDLER)  # For retweets, likes, follows.
    streamer.start()
    account_manager.run()


# Execute the main() function only if script is executed directly.
if __name__ == "__main__":
    main()
