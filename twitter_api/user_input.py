import sys
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.externals import joblib
from clean_and_cluster import clean_up_text


def main():
   reduced_data = joblib.load('reduced_data.pickle')
   vectorizer = joblib.load('vectorizer.pickle')
   vectorizer.fit(reduced_data)
   print("Enter text, then press enter!")
   for s in sys.stdin:
      sc = clean_up_text(s, 1)
      sl = [sc]
      sb = vectorizer.transform(sl)
      sd = sb.todense()
      #print("PCA new input")
      sr = pca_object.transform(sd)
      #print("Find closest neighbors")
      neigh = NearestNeighbors(n_neighbors=1, algorithm='kd_tree')
      neigh.fit(reduced_data)
      neighbors = neigh.kneighbors(sr, return_distance=False)
      replies = []
      for n in neighbors:
         for idx in n:
            i = 0 
            for key in tweets:
               if i == idx:
                  txt = clean_up_text(tweets[key]['replies'][0]['text'], 0)
                  txt = "<START> " + txt + " <END>"
                  pos_txt = clean_up_text(tweets[key]['text'], 1)
                  #print("post: " + pos_txt)
                  print("reply: " + txt)
                  replies.append(txt)
               i = i + 1
      #bigram = CountVectorizer(ngram_range=(2,2), stop_words=None, analyzer='word', binary=True)
      #bigram.fit_transform(replies)
      #print(bigram.stop_words_)
      #decision_tree("start", bigram.vocabulary_, 0)
      #print("\n")

if __name__ == "__main__":
   main()
