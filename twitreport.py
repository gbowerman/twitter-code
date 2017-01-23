# twitreport - basic command line Twitter reporting app
# initially, borrows from Tweepy example code:
#    http://pythonhosted.org/tweepy/getting_started.html#hello-tweepy
# For Twitter tweet structure: https://dev.twitter.com/overview/api/tweets

import json
import tweepy
import sys

# load twitter auth info
try:
    with open('twitconfig.json') as configFile:
        configData = json.load(configFile)
except FileNotFoundError:
    print("Error: Expecting twitconfig.json in current folder")
    sys.exit()

consumer_key = configData['consumerKey']
consumer_secret = configData['consumerSecret']
access_token = configData['accessToken']
access_token_secret = configData['accessTokenSecret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

api = tweepy.API(auth)

query = '%22scale+sets%22'
count = 10
for tweet in tweepy.Cursor(api.search,
        q=query,
        result_type="recent",
        include_entities=True,
        lang="en").items(count):
    print("User: " + tweet.user.name)
    print("Created at: " + str(tweet.created_at))
    print(tweet.text)