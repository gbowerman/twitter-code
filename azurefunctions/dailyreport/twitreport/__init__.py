import datetime
import logging
import json
import os
import requests
import sys
import tweepy

import azure.functions as func


def channel_post(webhook, body):
    '''generic function to post to slack or Microsoft Team'''
    headers = {"content-type": "application/json"}
    response = requests.post(webhook, data=body, headers=headers)
    logging.info('Channel post response: ' +
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
        logging.info('Error: ' + e.reason)
    logging.info(str(tweet_count) + ' tweets on ' + querystr_plain)
    if tweet_count == 0:
        return None
    return text


def main(mytimer: func.TimerRequest) -> None:
    '''load twitter auth and configuration info and trigger search'''
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    search_strings = json.loads(os.environ['searchStrings'])
    consumer_key = os.environ['consumerKey']
    consumer_secret = os.environ['consumerSecret']
    access_token = os.environ['accessToken']
    access_token_secret = os.environ['accessTokenSecret']
    teams_webhook = os.environ['teamsWebhook']
    teams_msg_title = os.environ['teamsMsgTitle']

    # set query date for last 24 hours
    date = datetime.datetime.now()
    date -= datetime.timedelta(hours=24)
    datestr = date.strftime("%Y-%m-%d")
    count = 30

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    user = api.me()
    logging.info('Name: ' + user.name)
    logging.info('Location: ' + user.location)

    # kick off a search for each string in the search string array
    for search_str in search_strings:
        query = search_str + ' since:' + datestr + ' -filter:retweets'
        logging.info("Query=" + query)
        twitter_text = twitter_query(api, count, query)
        if twitter_text is not None:
            teams_data = {'title': teams_msg_title, 'text': twitter_text}
            # logging.info(twitter_text)
            channel_post(teams_webhook, json.dumps(teams_data))
    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Twitter report function ran at %s', utc_timestamp)
