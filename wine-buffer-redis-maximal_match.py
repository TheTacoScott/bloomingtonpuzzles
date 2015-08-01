"""
wine.py
a bipartite non directed graphing solution to the bloomreach wine puzzle
example usage:
  python wine.py --input filename.txt
"""

import networkx as nx
import argparse, time, sys
import redis

parser = argparse.ArgumentParser(description='')
parser.add_argument('--input', action="store", dest="input")
parser.add_argument('--tree-merge', action="store", dest="tree_merge", default=80000)
parser.add_argument('--min-buffer', action="store", dest="min_buffer_size", default=1000000)
parser.add_argument('--max-buffer', action="store", dest="max_buffer_size", default=1100000)
parser.add_argument('--maxwine', action="store", dest="max_wine", default=3)
parser.add_argument('--maxpref', action="store", dest="max_prefs", default=10)
args = parser.parse_args()

MAX_WINE = int(args.max_wine)
MIN_MEM_NODE_COUNT = int(args.min_buffer_size)
MAX_MEM_NODE_COUNT = int(args.max_buffer_size)

fg = nx.Graph()

g_person_node_count = 0
g_wine_node_count = 0
g_root_node_count = 1

#let's redis shard out the blacklists
REDIS_SHARDS_W = {}
REDIS_SHARDS_W[0] = redis.Redis("localhost",6379,2)

REDIS_SHARDS_P = {}
REDIS_SHARDS_P[0] = redis.Redis("localhost",6379,3)

REDIS_SHARD_W_HASH_MOD = len(REDIS_SHARDS_W)
REDIS_SHARD_P_HASH_MOD = len(REDIS_SHARDS_P)
redis_has_values = False

#flush cache for this run
print "Flushing Databases"
for shard in REDIS_SHARDS_W:
  REDIS_SHARDS_W[shard].flushdb()
for shard in REDIS_SHARDS_P:
  REDIS_SHARDS_P[shard].flushdb()
print "Flushing Databases -- DONE"


def redis_set_value(key,value,kind):
  if kind == "p":
    shard = REDIS_SHARDS_P[hash(key) % REDIS_SHARD_P_HASH_MOD]
  elif kind == "w":
    shard = REDIS_SHARDS_W[hash(key) % REDIS_SHARD_W_HASH_MOD]
  if shard:
    return shard.set(key,value)
  return None

def redis_get_value(key,kind):
  if kind == "p":
    shard = REDIS_SHARDS_P[hash(key) % REDIS_SHARD_P_HASH_MOD]
  elif kind == "w":
    shard = REDIS_SHARDS_W[hash(key) % REDIS_SHARD_W_HASH_MOD]
  if shard:
    return shard.get(key)
  return None

def add_line_to_graph(line):
  """
  helper function to parse and add a line to the graph
  """
  added_nodes = 0
  global g_person_node_count, g_wine_node_count, redis_has_values
  (person, wine) = line[0:-1].split("\t")
  person = person.replace("person", "p")
  wine = wine.replace("wine", "w")

  person_id = long(person.replace("p",""))
  wine_id = long(wine.replace("w",""))
  if redis_has_values:
    pt_set = redis_get_value(person_id,"p")
    wt_set = redis_get_value(wine_id,"w")
  else:
    pt_set = wt_set = False

  if person not in fg and not pt_set: #do not add the same person twice, and do not add a person we've already sold 3 wines to
    fg.add_node(person, {"c": 0})
    g_person_node_count += 1
    added_nodes += 1
    
  if wine not in fg and not wt_set: #do not add the same wine twice, and do not add a wine we've already sold
    fg.add_node(wine)
    g_wine_node_count += 1
    added_nodes += 1

  if not pt_set and not wt_set:
    fg.add_edge(person, wine)
  return added_nodes

f = open(args.input, "r")

wine_sold = 0
lowest_wine_edge_count = 1
nodes_to_process = True

start = time.time()

#PREFILL THE BUFFER
more_file = True
while nodes_to_process or more_file:
  print "WHILE START",nodes_to_process,more_file,(g_person_node_count+g_wine_node_count),MIN_MEM_NODE_COUNT
  #REFILL THE BUFFER
  if (g_person_node_count+g_wine_node_count) < MIN_MEM_NODE_COUNT:
    print "Buffering..."
    while (g_person_node_count+g_wine_node_count) < MAX_MEM_NODE_COUNT and more_file:
      line = f.readline() #read in line from input
      if line:
        if add_line_to_graph(line): 
          nodes_to_process = True
      else:
        more_file = False
    print "Buffering Done"

  print "FG Length:",len(fg)
  max_match = nx.maximal_matching(fg)
  print "Match Count:",len(max_match)
  if len(max_match) == 0:
    fg.clear()
    g_person_node_count = 0
    g_wine_node_count = 0
    nodes_to_process = False
  for node in max_match:
    if node[0][0] == "w": 
      wine = node[0]
      person = node[1]
    elif node[0][0] == "p": 
      person = node[0]
      wine = node[1]

    person_id = long(person.replace("p",""))
    wine_id = long(wine.replace("w",""))

    wine_sold += 1
    fg.node[person]["c"] += 1
    if fg.node[person]["c"] == MAX_WINE:
      redis_set_value(person_id,1,"p") 
      fg.remove_node(person)
    redis_set_value(wine_id,1,"w")
    fg.remove_node(wine)
    redis_has_values = True

    print "{0}\t{1}\t{2}".format(person,wine,wine_sold)
    
f.close()
print args.min_buffer_size, args.max_buffer_size, wine_sold, round(time.time()-start, 3)
