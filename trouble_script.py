#!/usr/bin/env python3
"""
This script gives people what they deserve on Twitter, and tries luck in 'RT
to win' competititons.
"""
import os
import requests
import threading
from functions import *  # Useful functions for Twitter and scraping stuff.
from managers import *  # Useful classes for streaming and account handling. 
from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream

# Maybe we can utilize 'RT to win' stuff by this same script.
# Use the below link for image search.
# https://www.google.co.in/search?site=imghp&tbm=isch&source=hp&biw=1280&bih=647&q=trump+funny+meme
# Also post images in replies.

try:
    oauth = OAuth(
        os.environ['TW_ACCESS_TOKEN'],
        os.environ['TW_ACCESS_SECRET'],
        os.environ['TW_CONSUMER_KEY'],
        os.environ['TW_CONSUMER_SECRET']
    )
    SHORTE_ST_TOKEN = os.environ['SHORTE_ST_TOKEN']
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
with open('links.json', 'r') as links_file:
    links = json.loads(links_file.read())
# Gets IDs of bad people.
with requests.get(links['bads']) as bads_file:
    bads = [int(user_id) for user_id in bads_file.text.split('\n')]
# Gets messages to tweet.
with requests.get(links['messages']) as messages_file:
    messages = messages_file.text.split('\n')


def main():
    """Main function to handle different activites of the account."""

    streamer = StreamThread(ts)  # For the troubling part.
    account_manager = AccountThread(t)  # For retweets, likes, follows.
    streamer.start()
    account_manager.run()


# Execute the main() function only if script is executed directly.
if __name__ == "__main__":
    main()
