import json
import string 
import time 
import urllib.parse
import atexit
import sys
import os
import re
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

#paths = []

def max_sil_score(num_clusters, reduced_data):
   km = MiniBatchKMeans(n_clusters=int(num_clusters), init='k-means++')
   if len(np.shape(reduced_data)) > 2:
      return 1
   ret = km.fit(reduced_data)
   score = metrics.calinski_harabaz_score(reduced_data, km.labels_)
   print(score)
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
   joblib.dump(tweets, 'tweets.pkl')

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
   joblib.dump(vectorizer, 'vectorizer.pkl')
   #Need to do this
   bow = vectorizer.fit_transform(posts)
   joblib.dump(bow, 'bow.pkl')
   #Need to do this
   print(np.shape(bow))
   posts_tokenized = []
   print("Pos_tagging")
   for p in posts:
      posts_tokenized.append(posts_tokenized.append(pos_tag(p.split())))
   sentence_tokens = []
   for s in posts_tokenized:
      if s == None:
         continue
      to = []
      for t in s:
         to.append(t[1])
      result_str = ""
      for w in to:
         result_str = result_str + ' ' + w 
      sentence_tokens.append(result_str)
   print("Count vecting pos")
   tfid = TfidfVectorizer(ngram_range=(2,2), lowercase=False, smooth_idf=True, sublinear_tf=True)
   tf_vec = tfid.fit_transform(sentence_tokens)
   print(tf_vec)
   print(tfid.stop_words_)
   print("Creating pcfg")
   pcfg = {}
   count = 0
   for key in tfid.vocabulary_:
      k_sp = key.split()
      if k_sp[0] not in pcfg:
         pcfg[k_sp[0]] = {}
      for val in tfid.vocabulary_:
         v_sp = val.split()
         if k_sp[1] == v_sp[0]:
            pcfg[k_sp[0]][k_sp[1]] = 0
   count = 0
   for vocab in tfid.vocabulary_:
      v_sp = vocab.split()
      if pcfg[v_sp[0]][v_sp[1]] == 0:
         pcfg[v_sp[0]][v_sp[1]] = tfid.idf_[count] + pcfg[v_sp[0]][v_sp[1]]
      else:
         pcfg[v_sp[0]][v_sp[1]] = tfid.idf_[count] * pcfg[v_sp[0]][v_sp[1]]
      #pcfg[v_sp[0]][v_sp[1]] = pcfg[v_sp[0]][v_sp[1]] / len(tfid.idf_)
      count = count + 1
   joblib.dump(pcfg, 'pcfg.pkl')
   #print(pcfg)
   #print("Maximing CH Score")
   #opt = differential_evolution(max_sil_score, bounds=([(2, 100)]), args=([bow]))
   #print(int(opt['x']))

   km = MiniBatchKMeans(n_clusters=6, init='k-means++')
   ret = km.fit(bow)

   print("Enter text, then press enter!")
   for s in sys.stdin:
      sc = clean_up_text(s, 1)
      sl = [sc]
      sb = vectorizer.transform(sl)
      nzs = sb.nonzero()
      neigh = NearestNeighbors()
      neigh.fit(bow)
      neighbors = neigh.kneighbors(sb, n_neighbors=1, return_distance=True)
      replies = []
      for n in neighbors[1]:
         for idx in n:
            i = 0 
            for key in tweets:
               if i == idx:
                  for r in range(0, len(tweets[key]['replies'])):
                     txt = clean_up_text(tweets[key]['replies'][r]['text'], 0)
                     for c in txt:
                        if c == '.' or c == '.' or c == '!' or c == '?':
                           txt = txt.replace(c, ' <END> <START> ')
                     txt = "<START> " + txt + " <END>"
                     #print("reply: " + txt)
                     replies.append(txt)
               i = i + 1
      bigram = CountVectorizer(ngram_range=(2,2), stop_words=None, analyzer='word', binary=True, min_df=0, max_df=1, token_pattern='[^ ]+')
      bigram.fit_transform(replies)
      vocab = []
      for bg in bigram.vocabulary_:
         vocab.append(bg)
      graph = {}
      graph = create_trie(graph, vocab, "<start>")
      #print(graph)
      visited = create_visited(graph)
      #print(visited)
      #print("Finding sentences")
      paths = create_sentences("<start>", "<end>", graph, [])
      #print(paths)
      #print("POSing sentences")
      path_pos = []
      for p in paths:
         path_pos.append(pos_tag(p)) 
      #print(path_pos)
      #print("Getting hueristics for sentences")
      pos_sents = []
      for p in path_pos:
         pos = ""
         for t in p:
            pos = pos + " " + t[1]
         pos_sents.append(pos)
      #print(pos_sents)
      huer= []
      for p in pos_sents:
         h = 0
         p_sp = p.split()
         if len(p_sp) < 2:
            continue
         for i in range(0, len(p_sp) - 1):
            first = p_sp[i]
            second = p_sp[i + 1]
            if first in pcfg :
               if second in pcfg[first]:
                  if h == 0:
                     h = h + (pcfg[first][second] / len(p_sp))
                  else:
                     h = h * (pcfg[first][second] / len(p_sp))
         #print(h/len(p_sp))
         huer.append(h/len(p_sp))
      #print(huer)
      best_sent = paths[huer.index(max(huer))]
      bs_str = ""
      for w in best_sent:
        bs_str = bs_str + " " + w 
      print(bs_str)
      tts = gTTS(text=bs_str, lang='en')
      tts.save("txt.mp3")
      os.system("afplay txt.mp3")

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

def create_visited(graph):
   visited = {}
   for key in graph:
      if key not in visited:
         visited[key] = []
         for idx in range(0, len(graph[key])):
            visited[key].append(0)
   return visited

if __name__ == "__main__":
   main()
