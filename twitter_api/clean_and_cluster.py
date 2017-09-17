import twitter 
import json 
import time 
import urllib.parse
import atexit
import sys
import os
import re
import enchant
from stemming.porter2 import stem
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.decomposition import PCA
from sklearn import metrics
import emoji
import numpy as np
import plotly.plotly as py
#import matplotlib.pyplot as plt

def bag_of_words(lst):
   vectorizer = CountVectorizer()
   return vectorizer.fit_transform(lst).todense()
   #print(vectorizer.vocabulary_)

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
      if word == ' ':
         txt = txt.replace(word, '')
      for char in word:
         if char == '\n':
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
   r = open('replies.txt', 'r+')
   p = open('posts.txt', 'r+')

   tweets = t.read()

   replies = r.read().split('", "')
   replies[0] = replies[0].replace('[', '')
   replies[len(replies) - 1] = replies[len(replies) - 1].replace(']', '')

   posts = p.read().split('", "')
   posts[0] = posts[0].replace('[', '')
   posts[len(posts) - 1] = posts[len(posts) - 1].replace(']', '')

   deleted_tweets = 0

   need_to_be_deleted_posts = []
   for i in range((len(posts) - 1)):
      posts[i] = clean_up_text(posts[i], 1)
      if not posts[i] or posts[i].isspace() or len(posts[i].split(' ')) <= 1:
         deleted_tweets = deleted_tweets + 1
   for inx in need_to_be_deleted_posts:
      del posts[inx]


   need_to_be_deleted_replies = []
   for i in range((len(replies) - 1)):
      replies[i] = clean_up_text(replies[i], 0)
      if not replies[i] or replies[i].isspace() or len(replies[i].split(' ')) <= 1:
         deleted_tweets = deleted_tweets + 1
         need_to_be_deleted_replies.append(i)
   for inx in need_to_be_deleted_replies:
      del replies[inx]

   print("deleted tweets = " + str(deleted_tweets))

   bow = bag_of_words(posts)
   reduced_data = PCA(n_components=2).fit_transform(bow)
   num_clusters = int(len(posts) / 15)
   km = KMeans(n_clusters=num_clusters, init='k-means++', max_iter=num_clusters*1000, n_init=num_clusters*100)
   ret = km.fit(reduced_data)

   print(km.labels_)
   print(km.cluster_centers_)
   print(km.inertia_)
   for i in range(num_clusters):
      print(i)
      index = 0
      for l in km.labels_:
         if l == i:
            print('"'+posts[index]+'"')
         index = index + 1

if __name__ == "__main__":
   main()
