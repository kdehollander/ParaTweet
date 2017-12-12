from nltk import pos_tag
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer

pcfg = joblib.load('pcfg.pkl')

st = "The quick brown fox jumps over the lazy dog"
print(st)
tagged = pos_tag(st.split())
sp = ''
for tup in tagged:
   sp = sp + ' ' + tup[1]
   print(tup[1], end=' ')
huer = []
h = 0
p_sp = sp.split()
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
         print('Did not find second')
         h = h / (len(p_sp))
   else:
      print('Did not find first')
      h = h / (len(p_sp))
h = h * len(p_sp * 2)
print("h = " + str(h))
print('\n')

st = "Five hexing wizard bots jump quickly"
print(st)
tagged = pos_tag(st.split())
sp = ''
for tup in tagged:
   sp = sp + ' ' + tup[1]
   print(tup[1], end=' ')
huer = []
h = 0
p_sp = sp.split()
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
h = h * len(p_sp * 2)
print("h = " + str(h))
print('\n')

st = "Jim quickly realized that the beautiful gowns are expensive"
print(st)
tagged = pos_tag(st.split())
sp = ''
for tup in tagged:
   sp = sp + ' ' + tup[1]
   print(tup[1], end=' ')
huer = []
h = 0
p_sp = sp.split()
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
h = h * len(p_sp * 2)
print("h = " + str(h))
print('\n')

vects = ["Jim quickly realized that the beautiful gowns are expensive",
         "The quick brown fox jumps over the lazy dog",
         "Five hexing wizard bots jump quickly"]
bigram = CountVectorizer(ngram_range=(2,2), stop_words=None, analyzer='word', binary=True, min_df=0, max_df=1, token_pattern='[^ ]+')
bigram.fit_transform(vects)
for bg in bigram.vocabulary_:
   print(bg)
print()
