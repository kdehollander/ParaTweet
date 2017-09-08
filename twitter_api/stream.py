import twitter 
import json 
import time 
import urllib.parse
import atexit
import sys
import re
import enchant
api = twitter.Api(consumer_key='aCxaOUuI8nVh2Qqp4zy0qakfz',
      consumer_secret='JS9wfzmkwgKGxuRIT6eGGhLVVaAq3qHBBHKwZELFHIp6pfk54o',
      access_token_key='365288422-1WHmtCRrQZaFsS3U3kxqVAWhf2zBukMrgClY5BD1',
      access_token_secret='taf9r7T8LJw8kXlSNvT7trWcvstJ8uRP89sw528hQtx8w')
tweets_w_responses = {}
def main():
   num_tweets = 1000
   results = api.GetStreamFilter(track='-filter:links OR retweets', delimited=500)
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
      txt = clean_up_text(txt)
      # if for some reason, you can't get the tweet's text, or txt is not nothing,skip it
      if txt == '':
         continue 
      #print_error(txt)
      # if the tweet has not already been input, add
      if str(tweet.get('in_reply_to_status_id', '')) not in tweets_w_responses:
         try:
            post = api.GetStatus(tweet.get('in_reply_to_status_id', ''))
         except twitter.error.TwitterError as e:
            continue
         else:
            pos_txt = post.text
            pos_txt = clean_up_text(pos_txt)
            # remove the username in the beginning
            if pos_txt == '':
               continue 
            print(pos_txt)
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

def print_error(s):
   print(s, file=sys.stderr)

def clean_up_text(txt):
   print(txt)
   #remove any special chars, emojis, and numbers
   txt = re.sub('[^A-Za-z0-9\' ]+', '', txt)
   d = enchant.Dict('en_US')
   for word in txt.split():
      is_wrd = d.check(word) 
      if is_wrd == False:
         txt = txt.replace(word + ' ', '') 
   # if it is a retweet, remove 'RT ' so it will not mess up calculations later
   if "RT" in txt:
      txt = txt.replace('RT ', '')
   #remove any links in the text
   if "http" in txt:
      txt = re.sub('https[A-Za-z0-9./A-Za-z0-9]+', '', txt)
   print(txt)
   print('\n')
   return txt

#@atexit.register
#def exit():
   #print(tweets_w_responses)

def get_limit():
   api_init()
   rate = api.rate_limit.get_limit('/search/tweets')
   rem = rate.remaining - 25
   if rem <= 0:
      rem - rate.remaining
   return rem

def get_reset():
   api_init()
   rate = api.rate_limit.get_limit('/search/tweets')
   return rate.reset + 5

def api_init():
   while True:
      try:
         api.InitializeRateLimit()
      except:
         print_error("Init Sleeping")
         time.sleep(60) 
         continue
      else:
         break

if __name__ == "__main__":
   api_init()
   print_error("limit: " + str(get_limit()))
   t_n = time.time()
   print_error("reset: " + str(get_reset()/60))
   main()
