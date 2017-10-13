import json 
import time 
import urllib.parse
import atexit
import sys
import os
import re
from stemming.porter2 import stem
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.neighbors import NearestNeighbors
from sklearn import metrics
from scipy.optimize import differential_evolution
from nltk.corpus import words
import emoji
import numpy as np
import plotly.plotly as py
#import matplotlib.pyplot as plt

def decision_tree(first, vocab, level):
   for tup in vocab:
      b = tup.split()
      if b[0] == first:
         for i in vocab:
            c = i.split()
            if b[1] == c[0]:
               for l in range(0,level):
                  print("  ", end="")
               print(b[1])
               for l in range(0,level+1):
                  print("  ", end="")
               print(c[1])

def max_sil_score(num_clusters, reduced_data):
   km = MiniBatchKMeans(n_clusters=int(num_clusters), init='k-means++')
   if len(np.shape(reduced_data)) > 2:
      return 1
   ret = km.fit(reduced_data)
   score = metrics.calinski_harabaz_score(reduced_data, km.labels_)
   return -score
   
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
   p = open('posts.txt', 'r+')
   tweets = json.load(p)
   #print(tweets)

   posts = []
   for k,v in tweets.items():
      posts.append(v['text'])
   print(len(posts))

   num_words = 0
   for p in posts:
      for word in p.split():
         num_words = num_words + 1
   avg_words = int(num_words / len(posts))
      
   print("Bag of words")
   v_vectorizer = CountVectorizer(ngram_range=(1,2), lowercase=True, analyzer='word')
   v_bow = v_vectorizer.fit_transform(posts)
   print(np.shape(v_bow))
   engl_vectorizer = CountVectorizer(ngram_range=(1,2), lowercase=True, analyzer='word', vocabulary=set(words.words()))
   e_bow = engl_vectorizer.fit_transform(posts)
   print(np.shape(e_bow))
   new_vocab = []
   for key in v_vectorizer.vocabulary_:
      new_vocab.append(key)
   for key in engl_vectorizer.vocabulary_:
      new_vocab.append(key)
   print(len(new_vocab))
   vectorizer = CountVectorizer(ngram_range=(1,2), lowercase=True, analyzer='word', vocabulary=set(new_vocab))
   bow = vectorizer.fit_transform(posts)
   print(np.shape(bow))
   print("PCA")
   print("0 999")
   pca_object = TruncatedSVD(n_components=2)
   reduced_data = pca_object.fit_transform(bow[0:999])
   #print(reduced_data)
   rounds = int((len(posts) / 1000)) + 1
   for i in range(1, rounds):
      first = (i*1000)
      last = (((i+1) * 1000) - 1)
      if last > (len(posts) - 1):
         last = len(posts) - 1
      print(str(first) + " " + str(last))
      pca = pca_object.fit_transform(bow[first:last])
      reduced_data = np.concatenate((reduced_data, pca)) 
   joblib.dump(reduced_data, "reduced_data.pickle")
   #print("Maximing CH Score")
   #opt = differential_evolution(max_sil_score, bounds=([(2, 100)]), args=([reduced_data]))
   #print(int(opt['x']))

   km = MiniBatchKMeans(n_clusters=6, init='k-means++')
   ret = km.fit(reduced_data)

      
if __name__ == "__main__":
   main()
