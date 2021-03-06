import datetime
import logging
import json
import os
import requests
import sys
import tweepy

import azure.functions as func

from azure.cognitiveservices.language.textanalytics import TextAnalyticsClient
from msrest.authentication import CognitiveServicesCredentials

# set maximum number of tweets
TWEET_COUNT = 100

def channel_post(webhook, body):
    '''generic function to post to slack or Microsoft Team'''
    headers = {"content-type": "application/json"}
    response = requests.post(webhook, data=body, headers=headers)
    logging.info('Channel post response: ' +
          str(response.status_code) + ': ' + response.text)


def get_sentiment(text_analytics, documents):
    '''Add sentiment to a list of strings, return a string'''
    response = text_analytics.sentiment(documents=documents)
    sentiment_text = ""
    for doc in response.documents:
        if doc.score < 0.2 or doc.score > 0.8:
            doc_record = documents[int(doc.id) -1]
            new_text = f"<br/><b>Sentiment {round(doc.score, 2)}</b>: {doc_record['text']}"
            sentiment_text += new_text + "<br/>"
    return sentiment_text


def twitter_query(api, querystr, count):
    '''Query the Twitter APi'''
    tweet_count = 0
    tweet_list = []
    try:
        for tweet in tweepy.Cursor(api.search, q=querystr, tweet_mode='extended').items(count):
            # add each tweet to a list to be analyzed
            tweet_count += 1
            tweet_text = f'{tweet.user.name} at {tweet.created_at} <br/>{tweet.full_text}'
            tweet_rec = {"id": tweet_count, "language": "en", "text": tweet_text}
            tweet_list.append(tweet_rec)
    except tweepy.TweepError as e:
        print('Error: ' + e.reason)
    return tweet_list


def main(mytimer: func.TimerRequest) -> None:
    '''load twitter auth, configuration info, and trigger search'''
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    # get application settings from environment
    search_strings = json.loads(os.environ['searchStrings'])
    consumer_key = os.environ['consumerKey']
    consumer_secret = os.environ['consumerSecret']
    access_token = os.environ['accessToken']
    access_token_secret = os.environ['accessTokenSecret']
    teams_webhook = os.environ['teamsWebhook']
    teams_msg_title = os.environ['teamsMsgTitle']

    # get Azure text analytics data from environment
    subscription_key = os.environ["TEXT_ANALYTICS_SUBSCRIPTION_KEY"]
    endpoint = os.environ["TEXT_ANALYTICS_ENDPOINT"]

    # set query date for last 24 hours
    date = datetime.datetime.now()
    date -= datetime.timedelta(hours=24)
    datestr = date.strftime("%Y-%m-%d")

    # authenticate to Twitter
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    # instantiate a Text analytics client
    credentials = CognitiveServicesCredentials(subscription_key)
    analytics_client = TextAnalyticsClient(endpoint=endpoint, credentials=credentials)

    user = api.me()
    logging.info('Name: ' + user.name)
    logging.info('Location: ' + user.location)

    # kick off a search for each string in the search string array
    for search_str in search_strings:
        query = search_str + ' since:' + datestr + ' -filter:retweets'
        #print("Query=" + query)
        twitter_list = twitter_query(api, query, TWEET_COUNT)
        if twitter_list is not None:
            sentiment_text = get_sentiment(analytics_client, twitter_list)        
            querystr_plain = query.replace('%22', '"').replace('+', ' ')
            final_post = 'Tweets on ' + query + '<br/>' + sentiment_text
            teams_data = {'title': teams_msg_title, 'text': final_post}
            channel_post(teams_webhook, json.dumps(teams_data))

    logging.info('Twitter report function ran at %s', utc_timestamp)