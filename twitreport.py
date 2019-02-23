'''twitreport - basic command line Twitter reporting app for Teams endpoint
   Borrows from Tweepy example code:
   http://pythonhosted.org/tweepy/getting_started.html#hello-tweepy
   For Twitter tweet structure: https://dev.twitter.com/overview/api/tweets'''

import datetime
import json
import sys

import requests
import tweepy


def channel_post(webhook, body):
    '''generic function to post to slack or Microsoft Team'''
    headers = {"content-type": "application/json"}
    response = requests.post(webhook, data=body, headers=headers)
    print('Channel post response: ' +
          str(response.status_code) + ': ' + response.text)


def twitter_query(api, count, querystr):
    '''Query the Twitter APi'''
    querystr_plain = querystr.replace('%22', '"').replace('+', ' ')
    text = 'Tweets on ' + querystr_plain + '\n'
    tweet_count = 0
    try:
        for tweet in tweepy.Cursor(api.search, q=querystr, tweet_mode='extended').items(count):
            tweet_count += 1
            text += '\n' + tweet.user.name + \
                ' at: ' + str(tweet.created_at) + '\n'
            text += tweet.full_text + '\n'
    except tweepy.TweepError as e:
        print("Error: " + e.reason)
    print(str(tweet_count) + ' tweets on ' + querystr_plain)
    if tweet_count == 0:
        return None
    return text


def main():
    '''load twitter and Slack auth info (think about a separate auth class for this)'''
    try:
        with open('twitconfig.json') as configFile:
            configData = json.load(configFile)
    except FileNotFoundError:
        sys.exit("Error: Expecting twitconfig.json in current folder")

    search_strings = configData['searchStrings']
    consumer_key = configData['consumerKey']
    consumer_secret = configData['consumerSecret']
    access_token = configData['accessToken']
    access_token_secret = configData['accessTokenSecret']
    teams_webhook = configData['teamsWebhook']
    teams_msg_title = configData['teamsMsgTitle']

    # set query date for last 24 hours
    date = datetime.datetime.now()
    date -= datetime.timedelta(hours=24)
    datestr = date.strftime("%Y-%m-%d")
    count = 30

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    user = api.me()
    print('Name: ' + user.name)
    print('Location: ' + user.location)

    # kick off a search for each search string in the config file
    for search_str in search_strings:
        query = search_str + ' since:' + datestr + ' -filter:retweets'
        print("Query=" + query)
        twitter_text = twitter_query(api, count, query)
        if twitter_text is not None:
            teams_data = {'title': teams_msg_title, 'text': twitter_text}
            # print(twitter_text)
            channel_post(teams_webhook, json.dumps(teams_data))


if __name__ == "__main__":
    main()