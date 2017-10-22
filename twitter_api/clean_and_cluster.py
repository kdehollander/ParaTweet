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
from nltk import CFG
import emoji
import numpy as np
import plotly.plotly as py

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
   p = open('small.txt', 'r+')
   tweets = json.load(p)

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
   nzs = bow.nonzero()
   print(len(nzs[0]))
   for rc in range(0, len(nzs[0])):
      if rc % 10000 == 0:
         print(rc)
      bow[nzs[0][rc], nzs[0][rc]] = bow[nzs[0][rc], nzs[0][rc]] * 50
   print(np.shape(bow))
   print("PCA")
   print("0 1999")
   pca_object = TruncatedSVD(n_components=2)
   reduced_data = pca_object.fit_transform(bow[0:1999])
   rounds = int((len(posts) / 2000)) + 1
   for i in range(1, rounds):
      first = (i*2000)
      last = (((i+1) * 2000) - 1)
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

   print("Enter text, then press enter!")
   for s in sys.stdin:
      sc = clean_up_text(s, 1)
      sl = [sc]
      sb = vectorizer.transform(sl)
      nzs = sb.nonzero()
      print(len(nzs[0]))
      for rc in range(0, len(nzs[0])):
         sb[nzs[0][rc], nzs[0][rc]] = sb[nzs[0][rc], nzs[0][rc]] * 50
      print(np.shape(sb))
      #print("PCA new input")
      sr = pca_object.transform(sb)
      #print("Find closest neighbors")
      neigh = NearestNeighbors(n_neighbors=3, algorithm='kd_tree')
      neigh.fit(reduced_data)
      neighbors = neigh.kneighbors(sr, return_distance=True)
      print(neighbors)
      replies = []
      for n in neighbors[1]:
         for idx in n:
            i = 0 
            for key in tweets:
               if i == idx:
                  txt = clean_up_text(tweets[key]['replies'][0]['text'], 0)
                  txt = "<START> " + txt + " <END>"
                  pos_txt = clean_up_text(tweets[key]['text'], 1)
                  print("post: " + pos_txt)
                  print("reply: " + txt)
                  replies.append(txt)
               i = i + 1
      bigram = CountVectorizer(ngram_range=(2,2), stop_words=None, analyzer='word', binary=True, min_df=0, max_df=1)
      bigram.fit_transform(replies)
      vocab = []
      for bg in bigram.vocabulary_:
         vocab.append(bg)
      graph = {}
      graph = create_trie(graph, vocab, "start")
      print(graph)

def create_trie(graph, vocab, word):
   if word not in graph:
      graph[word] = []
      for bg in vocab:
         if bg.split()[0] == word:
            graph[word].append(bg.split()[1])
      for val in graph[word]:
         if val == 'end':
            continue
         create_trie(graph, vocab, val)
   return graph
   

if __name__ == "__main__":
   main()
