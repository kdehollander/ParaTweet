import twitter 
import json 
import urllib.parse
import atexit
import sys
import re
import csv

api = twitter.Api(consumer_key='enter_key',
      consumer_secret='enter_secret',
      access_token_key='enter_token_key',
      access_token_secret='enter_secret',
      sleep_on_rate_limit=True)

tweets_w_responses = {}
posts = []
replies = []
def main():
   num_tweets = 500000
   total_tweets = num_tweets
   results = api.GetStreamFilter(track='-filter:links OR retweets')
   for tweet in results:
      if tweet.get('in_reply_to_status_id', None) == None:
         continue 
      if num_tweets <= 0:
         break
      if str(tweet.get('lang', '')) != "en":
         continue
      txt = tweet.get('text', '')
      if not txt or txt.isspace():
         continue 
      if str(tweet.get('in_reply_to_status_id', '')) not in tweets_w_responses:
         tweets_w_responses[str(tweet.get('in_reply_to_status_id', ''))] = {
            'text': '',
            'replies': []
         }
         tweets_w_responses[str(tweet.get('in_reply_to_status_id', ''))]['replies'].append({
               'id': tweet.get('id', ''),
               'text': tweet.get('text', '')
            })
      else:
         tweets_w_responses[str(tweet.get('in_reply_to_status_id', ''))]['replies'].append({
               'id': tweet.get('id', ''),
               'text': tweet.get('text', '')
            })
      num_tweets = num_tweets - 1
      if num_tweets % 100 == 0:
         print(num_tweets)

@atexit.register
def exit():
   #print(posts)
   #with open('tweets.txt', 'w') as t:
      #json.dump(tweets_w_responses, t, ensure_ascii=False)

   #with open('/Volumes/Twitter Data/tweets.txt', mode='w') as p:
      #json.dump(tweets_w_responses, p, ensure_ascii=False)

   with open('tweets.txt', 'w') as r:
      json.dump(tweets_w_responses, r, ensure_ascii=False)

   #t.close()
   #p.close()
   r.close()

if __name__ == "__main__":
   #api_init()
   api.InitializeRateLimit()
   rate = api.rate_limit.get_limit('/search/tweets')
   #print_error("limit: " + str(rate.remaining - 10))
   #print_error("reset: " + str((rate.reset+5)/60))
   main()
