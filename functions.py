"This script contains useful functions for building the Twitter bot."

import json
import requests
from lxml.html import fromstring
from trouble_script import SHORTE_ST_TOKEN
from twitter import TwitterHTTPError
# Here 't' is account handler defined in the main script.

def reply(account_handler, tweet_id, user_name, msg):
    """
    Sends msg as reply to the tweet whose id is passed.
    user_name of the tweet's author is required as per Twitter API docs.
    """

    account_handler.statuses.update(
        status='@%s %s' % (user_name, msg),
        in_reply_to_status_id=tweet_id
        )


def print_tweet(tweet):
    """Displays the primary contents of a tweet, maybe except links."""

    print(tweet["user"]["name"])
    print(tweet["user"]["screen_name"])
    print(tweet["created_at"])
    print(tweet["text"])
    hashtags_list = []
    hashtags = tweet["entities"]["hashtags"]
    for tag in hashtags:
        hashtags_list.append(tag["text"])
    print(hashtags_list)


def fav_tweet(account_handler, tweet):
    """Favorites a passed tweet and returns a success status - 0 if successful
    otherwise 1.
    """
    try:
        account_handler.favorites.create(_id=tweet['id'])
        return 0
    except TwitterHTTPError:
        return 1


def retweet(account_handler, tweet):
    """Retweets a passed tweet and returns a success status - 0 if successful
    otherwise 1.
    """

    try:
        account_handler.statuses.retweet._id(_id=tweet["id"])
        return 0

    except TwitterHTTPError:
        return 1


def quote_tweet(account_handler, tweet, text):
    """Quotes a passed tweet with a passed text and then tweets it."""

    # May not work for long links because of 140-limit. Can be improved.
    tweet_id = tweet["id"]
    screen_name = tweet["user"]["screen_name"]
    link = "https://twitter.com/%s/status/%s" % (screen_name, tweet_id)
    try:
        string = text + " " + link
        account_handler.statuses.update(status=string)
        return 0
    except TwitterHTTPError:
        return 1


def unfollow(account_handler, iden):
    """Unfollows the person identified by 'iden', returns 0 if successful,
    otherwise 0."""
    try:
        account_handler.friendships.destroy(_id=iden)
        return 0
    except TwitterHTTPError:
        return 1


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
    """Gets top headline for a query from Google News.
    Returns in format (headline, link)."""

    # Following assumes that query doesn't contain special characters.
    url_encoded_query = '%20'.join(query.split())
    req = "https://news.google.com/news/search/section/q/" + url_encoded_query

    tree = fromstring(requests.get(req).content)
    news_item = tree.find(".//main/div/c-wiz/div/c-wiz")
    headline = news_item.xpath('.//a/text()')[0].strip()
    link = news_item.xpath('.//a/@href')[0].strip()

    return (headline, link)
