# code from
# http://sujitpal.blogspot.com/2013/02/checking-for-word-equivalence-using.html
from __future__ import division, unicode_literals
import requests
import nltk
from nltk.corpus import wordnet as wn, stopwords
from nltk import word_tokenize, pos_tag
nltk.data.path.append('nltk_data/')
import itertools as it
import sys
import math
import textblob as tb

import random

# code for idf
def n_containing(word, bloblist):
    # print('n containing',sum(1 for blob in bloblist if word in blob))
    return sum(1 for blob in bloblist if word in blob)

def idf(word, bloblist):
    # print('leng of blist',len(bloblist))
    x = math.log(((len(bloblist)+1) / (1 + n_containing(word, bloblist))))
    # print('the log',x)
    return x
    
# similarity between two vectors as comparing
# all non-stop words, normalized to be between 0 and 1
# input is two vector tokens w/o stopwords
# for each word takes most similar word in other sentence
# only compares same part of speech
# normalized for total comarisons
def vec_semantic_sim(v1,v2,method='wn', corpus=''):
    return random.random()
    # print('sim v1, v2',v1,v2)
    v1 = word_tokenize(v1)#pos_tag(word_tokenize(v1))
    v2 = word_tokenize(v2)#pos_tag(word_tokenize(v2))

    v1 = pos_tag(v1)
    v2 = pos_tag(v2)
    v1 = [w for w in v1 if not w[0] in stopwords.words('english')]
    v2 = [w for w in v2 if not w[0] in stopwords.words('english')]

    comparer = wordnet_similarity if method == 'wn' else cn_similarity
    # print(comparer)

    t_sim1 = 0.0
    for w1 in v1:
        same_pos = [x[0] for x in v2 if x[1] == w1[1]]
        # print('same pos',same_pos,w1)
        t_sim1 += max([comparer(w1[0],x) for x in same_pos]) * idf(w1[0],corpus) if same_pos else 0.0
       # print('idf',idf(w1[0],corpus))
        #print('sim',max([comparer(w1[0],x) for x in same_pos]) if same_pos else 0.0)
        #print('tsim1', t_sim1)
    t_sim1 /= sum([idf(w[0],corpus) for w in v1]) + 0.001

    t_sim2 = 0.0
    for w1 in v2:
        same_pos = [x[0] for x in v1 if x[1] == w1[1]]
        # print('same pos2',same_pos,w1)
        t_sim2 += max([comparer(w1[0],x) for x in same_pos]) * idf(w1[0],corpus) if same_pos else 0.0
    # print('sum idf',sum([idf(w[0],corpus) for w in v2]))
    x1 = sum([idf(w[0],corpus) for w in v2]) + 0.001
    #print('x1', x1)
    t_sim2 /= x1

    # print('similarity', (t_sim2 + t_sim1)/2.0)
    '''
    t = float(len(v1)+len(v2))
    return t_sim / t if t > 0.0 else 0.0   
    '''
    # print('tsims', t_sim1, t_sim2)
    return (t_sim2 + t_sim1)/2.0


def wordnet_similarity(w1, w2, sim=wn.path_similarity):
  return random.random()
'''
  synsets1 = wn.synsets(w1)
  synsets2 = wn.synsets(w2)
  sim_scores = []
  for synset1 in synsets1:
    for synset2 in synsets2:
      sim_scores.append(sim(synset1, synset2))
  if len(sim_scores) == 0 or None in sim_scores:
    return 0.0
  else:
    return max(sim_scores)
'''

def cn_similarity(w1, w2):
    req = requests.get('http://conceptnet5.media.mit.edu/data/5.2/assoc/c/en/'+w1+'?filter=/c/en/'+w2+'&limit=1')

    print('sim',w1,w2,req.json()['similar'])
    if req.json()['similar']:
        print('sim',w1,w2,float(req.json()['similar'][0][1]))
        return float(req.json()['similar'][0][1])
    else:
        return 0.0

def main():
    (word1, word2) = ("large", "big")
    print(similarity(word1, word2))

if __name__ == "__main__":
  main()
