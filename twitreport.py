# twitreport - basic command line Twitter reporting app
# initially, borrows from Tweepy example code:
#    http://pythonhosted.org/tweepy/getting_started.html#hello-tweepy
# For Twitter tweet structure: https://dev.twitter.com/overview/api/tweets
# Slack: https://github.com/os/slacker

import datetime
import json
import requests
import sys
import tweepy

# generic function to post to slack or Microsoft team
# set webhook and body accordingly
def channel_post(webhook, body):
    headers = {"content-type": "application/json"}
    response = requests.post(webhook, data=body, headers=headers)
    print(str(response.status_code) + ': ' + response.text)


def twitter_query(api, count, querystr):
    text = 'Tweets on ' + querystr.replace('%22', '"').replace('+', ' ') + '\n'
    tweet_count = 0
    for tweet in tweepy.Cursor(api.search,
            q=querystr,
            result_type="recent",
            include_entities=False, # set this True to resolve URLs etc.
            lang="en").items(count):
        tweet_count += 1
        text += '\n' + tweet.user.name + ' at: ' + str(tweet.created_at) + '\n'
        text += tweet.text
    if tweet_count == 0:
        return None
    return text


# load twitter and Slack auth info (think about a separate auth class for this)
try:
    with open('twitconfig.json') as configFile:
        configData = json.load(configFile)
except FileNotFoundError:
    print("Error: Expecting twitconfig.json in current folder")
    sys.exit()
search_strings = configData['searchStrings']
consumer_key = configData['consumerKey']
consumer_secret = configData['consumerSecret']
access_token = configData['accessToken']
access_token_secret = configData['accessTokenSecret']
# slack_webhook = configData['slackWebhook']
# slack_username = configData['slackUserName']
teams_webhook = configData['teamsWebhook']
teams_msg_title = configData['teamsMsgTitle']
slack_emoji = configData['slackIconEmoji']

# set query date for last 24 hours
date = datetime.datetime.now()
date -= datetime.timedelta(hours=24)
datestr = date.strftime("%Y-%m-%d")
count = 20

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# kick off a search for each search string in the config file
for search_str in search_strings:
    query = search_str + ' since:' + datestr
    twitter_text = twitter_query(api, count, query)
    if twitter_text is not None:
        teams_data = {'title': teams_msg_title,'text': twitter_text}
        channel_post(teams_webhook, json.dumps(teams_data))
        #slack_data = {'username': slack_username, 'icon_emoji': slack_emoji, 'text': twitter_text}
        #channel_post(slack_webhook, json.dumps(slack_data))


