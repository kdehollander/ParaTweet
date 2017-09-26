import twitter 
import json 
import urllib
import atexit
import sys
import re
import csv
import os
from stemming.porter2 import stem
import emoji

api = twitter.Api(consumer_key='aCxaOUuI8nVh2Qqp4zy0qakfz',
      consumer_secret='JS9wfzmkwgKGxuRIT6eGGhLVVaAq3qHBBHKwZELFHIp6pfk54o',
      access_token_key='365288422-1WHmtCRrQZaFsS3U3kxqVAWhf2zBukMrgClY5BD1',
      access_token_secret='taf9r7T8LJw8kXlSNvT7trWcvstJ8uRP89sw528hQtx8w',
      sleep_on_rate_limit=True)

tweets = {}

def isEmoji(word):
   for char in word:
      if char in emoji.UNICODE_EMOJI:
         return True
   return False

def clean_up_text(txt, post):
   txt = txt.replace('\\n', '')
   txt = txt.replace('\\"', '')
   txt = txt.replace('\\n\\n', '')
   txt = re.sub(r'^\x0020+', '', txt)
   txt.strip()
   for word in txt.split():
      for char in word:
         if char == '\n' or char == ' ':
            txt = txt.replace(char, '')
         
      if post == 1:
         new_word=stem(word)
         txt = txt.replace(word, new_word)
      is_emoji=isEmoji(word)
      #if is_emoji == True:
         #txt = txt.replace(word, '') 
   if "#" in txt:
      txt = re.sub('#[a-zA-Z0-9]+', '', txt)
   if "&" in txt:
      txt = re.sub('&[a-z]+;', '', txt)
   if "@" in txt:
      txt = re.sub('@[^ ]+', '', txt)
   # if it is a retweet, remove 'RT ' so it will not mess up calculations later
   if "RT" in txt:
      txt = txt.replace('RT ', '')
   #make token for link
   if "http" in txt:
      txt = re.sub('http[^ ]+', '', txt)
   #print(txt)
   #print('\n')
   return txt

def main():
   t = open('tweets.txt', 'r+')
   tweets = json.load(t)
   print(len(tweets))
   rep = 0
   tweets_to_be_deleted = []
   for tweet in tweets:
      while True:
         try:
            print("Getting tweet:" + tweet)
            post = api.GetStatus(tweet)
            break
         except twitter.error.TwitterError as e:
            print("Twitter error. Adding this tweet to be deleted later")
            tweets_to_be_deleted.append(tweet)
            break
         except requests.exceptions.ConnectionError:
            print("connection error. Going to sleep for a little")
            sleep(60)
      print("Foudn tweet")
      txt = clean_up_text(post.text, 1)
      if not txt or txt.isspace() or len(txt.split(' ')) <= 1:
         tweets_to_be_deleted.append(tweet)
      tweets[tweet]['text'] = txt
      if rep % 500 == 0:
         print(rep)
      rep = rep + 1
   print("Deleting posts")
   for t in tweets_to_be_deleted:
      del tweets[t]
   print("Opening file")
   with open('tweets.txt', 'w') as r:
      json.dump(tweets, r, ensure_ascii=False)

if __name__ == "__main__":
   #api_init()
   api.InitializeRateLimit()
   rate = api.rate_limit.get_limit('/search/tweets')
   #print_error("limit: " + str(rate.remaining - 10))
   #print_error("reset: " + str((rate.reset+5)/60))
   main()
