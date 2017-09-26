import twitter 
import json 
import urllib.parse
import atexit
import sys
import re
import csv

api = twitter.Api(consumer_key='aCxaOUuI8nVh2Qqp4zy0qakfz',
      consumer_secret='JS9wfzmkwgKGxuRIT6eGGhLVVaAq3qHBBHKwZELFHIp6pfk54o',
      access_token_key='365288422-1WHmtCRrQZaFsS3U3kxqVAWhf2zBukMrgClY5BD1',
      access_token_secret='taf9r7T8LJw8kXlSNvT7trWcvstJ8uRP89sw528hQtx8w',
      sleep_on_rate_limit=True)
tweets_w_responses = {}
posts = []
replies = []
def main():
   num_tweets = 100
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
      # if for some reason, you can't get the tweet's text, or txt is not nothing,skip it
      if not txt or txt.isspace():
         continue 
      #print_error(txt)
      #replies.append(txt)
      # if the tweet has not already been input, add
      if str(tweet.get('in_reply_to_status_id', '')) not in tweets_w_responses:
         try:
            post = api.GetStatus(tweet.get('in_reply_to_status_id', ''))
         except twitter.error.TwitterError as e:
            print("There was a problem")
            continue
         else:
            pos_txt = post.text
            if not pos_txt or pos_txt.isspace() or len(pos_txt.split(' ')) <= 1:
               continue 
            posts.append(pos_txt)
            tweets_w_responses[str(tweet.get('in_reply_to_status_id', ''))] = {
               'text': pos_txt,
               'replies': [] 
            }
      if str(tweet.get('id', '')) not in tweets_w_responses[str(tweet.get('in_reply_to_status_id', ''))]['replies']:
         tweets_w_responses[str(tweet.get('in_reply_to_status_id', ''))]['replies'].append({
            'text': txt
         })
      num_tweets = num_tweets - 1
      if num_tweets % 500 == 0:
         print(num_tweets)

@atexit.register
def exit():
   #print(posts)
   #with open('tweets.txt', 'w') as t:
      #json.dump(tweets_w_responses, t, ensure_ascii=False)

   #with open('/Volumes/Twitter Data/tweets.txt', mode='w') as p:
      #json.dump(tweets_w_responses, p, ensure_ascii=False)

   with open('posts.txt', 'w') as r:
      json.dump(posts, r, ensure_ascii=False)

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
