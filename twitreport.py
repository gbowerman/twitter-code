# twitreport - basic command line Twitter reporting app
# initially, borrows heavily from Tweepy example code:
#    http://pythonhosted.org/tweepy/getting_started.html#hello-tweepy

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

public_tweets = api.home_timeline()
for tweet in public_tweets:
    print(tweet.text)