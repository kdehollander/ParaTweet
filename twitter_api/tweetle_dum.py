import json
import string 
import time 
import urllib.parse
import atexit
import sys
import os
import re
import math
import twitter
from stemming.porter2 import stem
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.neighbors import NearestNeighbors
from sklearn import metrics
from scipy.optimize import differential_evolution
from nltk.corpus import words
from nltk import CFG
from nltk import pos_tag
import emoji
import numpy as np
import plotly.plotly as py
from gtts import gTTS

api = twitter.Api(consumer_key='BwkjH0M6yYOSMqFX9yqqK0hhv',
      consumer_secret='14Mq93PKPDlb7P000ByEcOPS9dfyuM87QjOP207Az92wj8M1uU',
      access_token_key='935212367704612864-gdsJje14gEkWEQ1qlujYc16avlm3YMD',
      access_token_secret='PRZkH4iu7Lu0If3a3zNvCTTz5Bar5XNCsv7zWMUU9F49S',
      sleep_on_rate_limit=True)

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
         if is_emoji == True:
            txt = txt.replace(word, '') 
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
   return txt

def main():
   vectorizer = joblib.load('vectorizer.pkl')
   bow = joblib.load('bow.pkl')
   tweets = joblib.load('tweets.pkl')
   pcfg = joblib.load('pcfg.pkl')
   while(1):
      time.sleep(30)
      mentions = joblib.load('mentions.pkl')
      for s in api.GetMentions():
         if s.id in mentions:
            continue
         sc = clean_up_text(s.text, 1)
         sl = [sc]
         sb = vectorizer.transform(sl)
         nzs = sb.nonzero()
         neigh = NearestNeighbors()
         neigh.fit(bow)
         neighbors = neigh.kneighbors(sb, n_neighbors=3, return_distance=True)
         replies = []
         for n in neighbors[1]:
            for idx in n:
               i = 0 
               for key in tweets:
                  if i == idx:
                     for r in range(0, len(tweets[key]['replies'])):
                        txt = clean_up_text(tweets[key]['replies'][r]['text'], 0)
                        for c in txt:
                           if c == '.' or c == '!' or c == '?':
                              txt = txt.replace(c, ' <END> <START> ')
                        txt = "<START> " + txt + " <END>"
                        replies.append(txt)
                  i = i + 1
         bigram = CountVectorizer(ngram_range=(2,2), stop_words=None, analyzer='word', binary=True,token_pattern='[^ ]+');
         bigram.fit_transform(replies)
         vocab = []
         for bg in bigram.vocabulary_:
            vocab.append(bg)
         graph = {}
         graph = create_trie(graph, vocab, "<start>")
         paths = create_sentences("<start>", "<end>", graph, [])
         path_pos = []
         for p in paths:
            path_pos.append(pos_tag(p)) 
         pos_sents = []
         for p in path_pos:
            pos = ""
            for t in p:
               pos = pos + " " + t[1]
            pos = pos.replace('$', '')
            pos_sents.append(pos)
         huer = []
         for p in pos_sents:
            h = 0
            p_sp = p.split()
            if len(p_sp) <= 4 or len(p_sp) > 10:
               h = -1
               huer.append(h)
               continue
            for i in range(0, len(p_sp) - 1):
               first = p_sp[i]
               second = p_sp[i + 1]
               if first in pcfg :
                  if second in pcfg[first]:
                     if h == 0:
                        h = 1 / pcfg[first][second]
                     else:
                        h = h * (1 / pcfg[first][second])
                  else:
                     h = h / (len(p_sp))
               else:
                  h = h / (len(p_sp))
            h = h * len(p_sp)
            huer.append(h)
         best_sent = paths[huer.index(max(huer))]
         bs_str = ""
         for w in best_sent:
            bs_str = bs_str + " " + w 
         print("Replying to status " + str(s.id) + ": " + s.text)
         print(bs_str)
         api.PostUpdate(status=bs_str, in_reply_to_status_id=s.id, auto_populate_reply_metadata=True)
         mentions.append(s.id)
         joblib.dump(mentions, 'mentions.pkl')
      #print(bs_str)
      #tts = gTTS(text=bs_str, lang='en')
      #tts.save("txt.mp3")
      #os.system("afplay txt.mp3")

def create_sentences(start, end, graph, path=[]):
   if start != "<start>" and start != "<end>":
      path = path + [start]
   if start == end:
      return [path]
   if start not in graph:
      return []
   paths = []
   for node in graph[start]:
      if node not in path:
         newpaths = create_sentences(node, end, graph, path)
         for newpath in newpaths:
            paths.append(newpath)
   return paths

def create_trie(graph, vocab, word):
   if word not in graph:
      graph[word] = []
      for bg in vocab:
         if bg.split()[0] == word:
            graph[word].append(bg.split()[1])
      for val in graph[word]:
         if val == '<end>':
            continue
         create_trie(graph, vocab, val)
   return graph

if __name__ == "__main__":
   main()
