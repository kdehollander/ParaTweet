import twitter 
import json 
import time 
import urllib.parse
import atexit
import sys
import os
import re
from stemming.porter2 import stem
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.decomposition import PCA
from sklearn.naive_bayes import GaussianNB
from sklearn import metrics
from scipy.optimize import minimize, differential_evolution
from scipy.misc import derivative
import emoji
import numpy as np
import plotly.plotly as py
import matplotlib.pyplot as plt

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
   #t = open('tweets.txt', 'r+')
   #r = open('replies.txt', 'r+')
   p = open('tweets.txt', 'r+')
   tweets = json.load(p)
   print(tweets)

   #tweets = t.read()

   #replies = r.read().split('", "')
   #replies[0] = replies[0].replace('[', '')
   #replies[len(replies) - 1] = replies[len(replies) - 1].replace(']', '')

   posts = []
   #posts = p.read().split('", "')
   #posts[0] = posts[0].replace('[', '')
   #posts[len(posts) - 1] = posts[len(posts) - 1].replace(']', '')
   #print(len(posts))

   deleted_tweets = 0

   need_to_be_deleted_posts = []
   for i in range((len(posts) - 1)):
      posts[i] = clean_up_text(posts[i], 1)
      if not posts[i] or posts[i].isspace() or len(posts[i].split(' ')) <= 1:
         deleted_tweets = deleted_tweets + 1
         need_to_be_deleted_posts.insert(0, i)
   for inx in need_to_be_deleted_posts:
      del posts[inx]
   print(len(posts))

   #need_to_be_deleted_replies = []
   #for i in range((len(replies) - 1)):
      #replies[i] = clean_up_text(replies[i], 0)
      #if not replies[i] or replies[i].isspace() or len(replies[i].split(' ')) <= 1:
         #deleted_tweets = deleted_tweets + 1
         #need_to_be_deleted_replies.insert(0, i)
   #for inx in need_to_be_deleted_replies:
      #del replies[inx]

   print("deleted tweets = " + str(deleted_tweets))

   print("Bag of words")
   vectorizer = CountVectorizer()
   bow = vectorizer.fit_transform(posts).todense()
   print(bow)
   print("PCA")
   print("0 3999")
   reduced_data = PCA(n_components=2).fit_transform(bow[0:3999])
   print(reduced_data)
   rounds = int((len(posts) / 4000)) + 1
   for i in range(1, rounds):
      first = (i*4000)
      last = (((i+1) * 4000) - 1)
      if last > (len(posts) - 1):
         last = len(posts) - 1
      print(str(first) + " " + str(last))
      pca = PCA(n_components=2).fit_transform(bow[first:last])
      reduced_data = np.concatenate((reduced_data, pca))

   #print("Maximize Silhouette")
   #s_scores = []
   #ch_scores = []
   #in_scores = []
   #for i in range(3, 50):
      #km = MiniBatchKMeans(n_clusters=i, init='k-means++')
      #ret = km.fit(reduced_data)
      #s_scores.append(metrics.silhouette_score(reduced_data, km.labels_))
      #ch_scores.append(metrics.calinski_harabaz_score(reduced_data, km.labels_) / 5000)
      #in_scores.append(km.inertia_ / 1000)
      #if i % 10 == 0:
         #print(i)

   print("Maximing CH Score")
   opt = differential_evolution(max_sil_score, bounds=([(2, 100)]), args=([reduced_data]))
   print(int(opt['x']))

   km = MiniBatchKMeans(n_clusters=int(opt['x']), init='k-means++')
   ret = km.fit(reduced_data)
      
   #print("Starting Bayes")
   #clf = GaussianNB()
   #clf.fit(reduced_data, km.labels_)

   #i = open('input.txt', 'r')
   #s = i.read().split('\n')
   #sc = clean_up_text(s[0], 1)
   #print(sc)
   #sl = [sc]
   #sb = vectorizer.transform(sl).todense()
   #print(sb)
   #print("PCA new input")
   #sr = PCA(n_components=3).fit_transform(sb)
   #print(sr)

   #print("predict class")
   #cl = clf.predict(sr)
   #print(cl)

   #index = 0
   #reduced_cluster_x = []
   #reduced_cluster_y = []
   #for l in km.labels_:
      #if l == cl:
         #reduced_cluster_x.append(reduced_data[index][0])
         #reduced_cluster_y.append(reduced_data[index][1])
      #index = index + 1
   #plt.plot(reduced_cluster_x, reduced_cluster_y, 'k.', markersize=2)
   #plt.plot(sr[0][0], sr[0][1], 'r.', markersize=2)
   
   # Step size of the mesh. Decrease to increase the quality of the VQ.
   h = .02     # point in the mesh [x_min, x_max]x[y_min, y_max].

   # Plot the decision boundary. For that, we will assign a color to each
   x_min, x_max = reduced_data[:, 0].min() - 1, reduced_data[:, 0].max() + 1
   y_min, y_max = reduced_data[:, 1].min() - 1, reduced_data[:, 1].max() + 1
   xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

   # Obtain labels for each point in mesh. Use last trained model.
   Z = km.predict(np.c_[xx.ravel(), yy.ravel()])

   # Put the result into a color plot
   Z = Z.reshape(xx.shape)
   plt.figure(1)
   plt.clf()
   plt.imshow(Z, interpolation='nearest',
           extent=(xx.min(), xx.max(), yy.min(), yy.max()),
           cmap=plt.cm.Paired,
           aspect='auto', origin='lower')

   plt.plot(reduced_data[:, 0], reduced_data[:, 1], 'k.', markersize=2)
   # Plot the centroids as a white X
   centroids = km.cluster_centers_
   plt.scatter(centroids[:, 0], centroids[:, 1],
            marker='x', s=169, linewidths=3,
            color='w', zorder=10)
   plt.title('K-means clustering on the digits dataset (PCA-reduced data)\n'
          'Centroids are marked with white cross')
   plt.xlim(x_min, x_max)
   plt.ylim(y_min, y_max)
   plt.xticks(())
   plt.yticks(())
   plt.show()

if __name__ == "__main__":
   main()
