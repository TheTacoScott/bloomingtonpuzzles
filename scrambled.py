import itertools
from pattern.en import parse
import argparse

parser = argparse.ArgumentParser(description='')
parser.add_argument('--input', action="store", dest="input")
args = parser.parse_args()
f = open(args.input, "r")
with open(args.input, "r") as f:
  for line in f:
    print ""
    rating = 0
    split = line.split(" ")
    
    for i in itertools.permutations(split, len(split)): 
      print parse(" ".join(i)).split()
