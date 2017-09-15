import twitter 
import json 
import urllib.parse
import atexit
import sys
import re
from nltk.stem import RegexpStemmer as RS
from stemming.porter2 import stem
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn import metrics
import emoji

api = twitter.Api(consumer_key='aCxaOUuI8nVh2Qqp4zy0qakfz',
      consumer_secret='JS9wfzmkwgKGxuRIT6eGGhLVVaAq3qHBBHKwZELFHIp6pfk54o',
      access_token_key='365288422-1WHmtCRrQZaFsS3U3kxqVAWhf2zBukMrgClY5BD1',
      access_token_secret='taf9r7T8LJw8kXlSNvT7trWcvstJ8uRP89sw528hQtx8w')
tweets_w_responses = {}
posts = []
replies = []
def main():
   num_tweets = 500
   total_tweets = num_tweets
   results = api.GetStreamFilter(track='-filter:links OR retweets')
   for tweet in results:
      if tweet.get('in_reply_to_status_id', None) == None:
         continue 
      #t_id = tweet.get('id', '')
      #print_error(api.status_activity(t_id))
      #print_error(num_tweets)
      if num_tweets <= 0:
         break
      if str(tweet.get('lang', '')) != "en":
         continue
      txt = tweet.get('text', '')
      # if for some reason, you can't get the tweet's text, or txt is not nothing,skip it
      if not txt or txt.isspace():
         continue 
      #print_error(txt)
      replies.append(txt)
      # if the tweet has not already been input, add
      if str(tweet.get('in_reply_to_status_id', '')) not in tweets_w_responses:
         try:
            post = api.GetStatus(tweet.get('in_reply_to_status_id', ''))
         except twitter.error.TwitterError as e:
            continue
         else:
            pos_txt = post.text
            # remove the username in the beginning
            if not pos_txt or pos_txt.isspace() or len(pos_txt.split(' ')) <= 1:
               #print("failed")
               #print(pos_txt)
               continue 
            posts.append(pos_txt)
            tweets_w_responses[str(tweet.get('in_reply_to_status_id', ''))] = {
               'text': pos_txt,
               'user': post.user.screen_name,
               'replies': [] 
            }
      if str(tweet.get('id', '')) not in tweets_w_responses[str(tweet.get('in_reply_to_status_id', ''))]['replies']:
         tweets_w_responses[str(tweet.get('in_reply_to_status_id', ''))]['replies'].append({
            'id': tweet.get('id', ''),
            'text': txt
         })
      num_tweets = num_tweets - 1

@atexit.register
def exit():
   print(posts)
   with open('tweets.txt', 'w') as t:
      json.dump(tweets_w_responses, t, ensure_ascii=False)

   with open('posts.txt', 'w') as p:
      json.dump(posts, p, ensure_ascii=False)

   with open('replies.txt', 'w') as r:
      json.dump(replies, r, ensure_ascii=False)

   t.close()
   p.close()
   r.close()

if __name__ == "__main__":
   #api_init()
   api.InitializeRateLimit()
   rate = api.rate_limit.get_limit('/search/tweets')
   #print_error("limit: " + str(rate.remaining - 10))
   #print_error("reset: " + str((rate.reset+5)/60))
   main()
