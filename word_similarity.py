# code from
# http://sujitpal.blogspot.com/2013/02/checking-for-word-equivalence-using.html
from __future__ import division
import requests
from nltk.corpus import wordnet as wn, stopwords
from nltk import word_tokenize, pos_tag
import itertools as it
import sys

    
# similarity between two vectors as comparing
# all non-stop words, normalized to be between 0 and 1
# input is two vector tokens w/o stopwords
# for each word takes most similar word in other sentence
# only compares same part of speech
# normalized for total comarisons
def vec_semantic_sim(v1,v2,method='wn'):
    # print('sim v1, v2',v1,v2)
    v1 = word_tokenize(v1)#pos_tag(word_tokenize(v1))
    v2 = word_tokenize(v2)#pos_tag(word_tokenize(v2))

    v1 = pos_tag(v1)
    v2 = pos_tag(v2)
    v1 = [w for w in v1 if not w[0] in stopwords.words('english')]
    v2 = [w for w in v2 if not w[0] in stopwords.words('english')]

    t_sim = 0.0
    comparer = wordnet_similarity if method == 'wn' else cn_similarity
    # print(comparer)

    for w1 in v1:
        same_pos = [x[0] for x in v2 if x[1] == w1[1]]
        # print('same pos',same_pos,w1)
        t_sim += max([comparer(w1[0],x) for x in same_pos]) if same_pos else 0.0

    for w1 in v2:
        same_pos = [x[0] for x in v1 if x[1] == w1[1]]
        # print('same pos2',same_pos,w1)
        t_sim += max([comparer(w1[0],x) for x in same_pos]) if same_pos else 0.0

    # print('similarity',t_sim / float(len(v1)+len(v2)))
    t = float(len(v1)+len(v2))
    return t_sim / t if t > 0.0 else 0.0   


def wordnet_similarity(w1, w2, sim=wn.path_similarity):
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
