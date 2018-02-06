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
import requests
import time

api = twitter.Api(consumer_key='enter_key',
      consumer_secret='enter_secret',
      access_token_key='enter_token_key',
      access_token_secret='enter_secret',
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
   num_deleted = 0
   tweets_to_be_deleted = []
   for tweet in tweets:
      while True:
         try:
            post = api.GetStatus(tweet)
            time.sleep(1)
            if rep % 200 == 0:
               print("Getting tweet:" + tweet)
         except twitter.error.TwitterError as e:
            num_deleted = num_deleted + 1
            if num_deleted % 50 == 0:
               print("Deleted tweets= " + str(num_deleted))
            tweets_to_be_deleted.append(tweet)
            break
         except requests.exceptions.ConnectionError:
            continue
         txt = clean_up_text(post.text, 1)
         if not txt or txt.isspace() or len(txt.split(' ')) <= 1:
            tweets_to_be_deleted.append(tweet)
         tweets[tweet]['text'] = txt
         if rep % 1000 == 0:
            print(rep)
         rep = rep + 1
         break
   print("Deleting posts")
   for t in tweets_to_be_deleted:
      del tweets[t]
   print("Opening file")
   with open('posts.txt', 'w') as r:
      json.dump(tweets, r, ensure_ascii=False)

if __name__ == "__main__":
   #api_init()
   api.InitializeRateLimit()
   rate = api.rate_limit.get_limit('/search/tweets')
   #print_error("limit: " + str(rate.remaining - 10))
   #print_error("reset: " + str((rate.reset+5)/60))
   main()
