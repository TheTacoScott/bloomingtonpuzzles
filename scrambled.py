import itertools
from pattern.en import parse
import nltk
import argparse


parser = argparse.ArgumentParser(description='')
parser.add_argument('--input', action="store", dest="input")
args = parser.parse_args()
with open(args.input, "r") as f:
  for line in f:
    print ""
    rating = 0
    split = line.split(" ")
    
    print "PATTERN"
    for i in itertools.permutations(split, len(split)): 
      print parse(" ".join(i)).split()

    print "NLTK"
    for i in itertools.permutations(split, len(split)):
      print nltk.pos_tag(nltk.word_tokenize(" ".join(i)))
