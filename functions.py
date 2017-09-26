import json
import re
import requests
import threading
from lxml.html import fromstring
"This script contains useful functions for Twitter handling."
# Here 't' is account handler defined in the main script.

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
    """Displays the primary contents of a tweet, maybe except links."""

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
    """Favorites a passed tweet and returns a success status - 1 if successful
    otherwise 0.
    """
    try:
        result = t.favorites.create(_id=tweet['id'])
        return 1
    except TwitterHTTPError:
        return 0


def retweet(tweet):
    """Retweets a passed tweet and returns a success status - 1 if successful
    otherwise 0.
    """

    try:
        t.statuses.retweet._id(_id=tweet["id"])
        return 1

    except TwitterHTTPError:
        return 0


def quote_tweet(tweet, text):
    """Quotes a passed tweet with a passed text and then tweets it."""

    # May not work for long links because of 140-limit. Can be improved.
    id = tweet["id"]
    sn = tweet["user"]["screen_name"]
    link = "https://twitter.com/%s/status/%s" % (sn, id)
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


def shorten_url(url):
    """Shortens the passed url using shorte.st's API."""

    response = requests.put(
        "https://api.shorte.st/v1/data/url",
        {"urlToShorten": url}, headers={"public-api-token": SHORTE_ST_TOKEN}
        )
    info = json.loads(response.content.decode())
    if info["status"] == "ok":
        return info["shortenedUrl"]
    return url  # If shortening fails, the original url is returned.


def get_top_headline(query):
    """
    Gets top headline for a query from Google News.
    Returns in format (headline, link)
    """

    # Following assumes that query doesn't contain special characters.
    url_encoded_query = '%20'.join(query.split())
    req = "https://news.google.com/news/search/section/q/" + query

    tree = fromstring(requests.get(req).content)
    news_item = tree.find(".//main/div/c-wiz/div/c-wiz")
    headline = news_item.xpath('.//a/text()')[0].strip()
    link = news_item.xpath('.//a/@href')[0].strip()

    return (headline, link)