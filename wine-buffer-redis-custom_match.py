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
parser.add_argument('--min-buffer', action="store", dest="min_buffer_size", default=1000000)
parser.add_argument('--max-buffer', action="store", dest="max_buffer_size", default=1100000)
parser.add_argument('--maxwine', action="store", dest="max_wine", default=3)
parser.add_argument('--maxpref', action="store", dest="max_prefs", default=10)
args = parser.parse_args()

MAX_WINE = int(args.max_wine)
MIN_MEM_NODE_COUNT = int(args.min_buffer_size)
MAX_MEM_NODE_COUNT = int(args.max_buffer_size)
FEWER_COMPARE = int(args.max_prefs + 1)

#let's redis shard out the blacklists
REDIS_SHARDS_W = {}
REDIS_SHARDS_W[0] = redis.Redis("localhost",6379,0)

REDIS_SHARDS_P = {}
REDIS_SHARDS_P[0] = redis.Redis("localhost",6379,1)

REDIS_SHARD_W_HASH_MOD = len(REDIS_SHARDS_W)
REDIS_SHARD_P_HASH_MOD = len(REDIS_SHARDS_P)

fg = nx.Graph()

g_person_node_count = 0
g_wine_node_count = 0
g_root_node_count = 1
redis_has_values = False

def redis_set_value(key,kind):
  if kind == "p":
    shard = REDIS_SHARDS_P[hash(key) % REDIS_SHARD_P_HASH_MOD]
  elif kind == "w":
    shard = REDIS_SHARDS_W[hash(key) % REDIS_SHARD_W_HASH_MOD]
  if shard:
    return shard.incr(key,amount=1)
  return None

def redis_get_value(key,kind):
  if kind == "p":
    shard = REDIS_SHARDS_P[hash(key) % REDIS_SHARD_P_HASH_MOD]
  elif kind == "w":
    shard = REDIS_SHARDS_W[hash(key) % REDIS_SHARD_W_HASH_MOD]
  if shard:
    data = shard.get(key)
    if data:
      return int(data)
  return None

#flush cache for this run
print "Flushing Databases"
for shard in REDIS_SHARDS_W:
  REDIS_SHARDS_W[shard].flushdb()
for shard in REDIS_SHARDS_P:
  REDIS_SHARDS_P[shard].flushdb()
print "Flushing Databases -- DONE"

def add_line_to_graph(line):
  """
  helper function to parse and add a line to the graph
  """
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

  if person not in fg: #do not add the same person twice, and do not add a person we've already sold 3 wines to
    if not pt_set or pt_set < MAX_WINE: 
      fg.add_node(person)
      g_person_node_count += 1
    
  if wine not in fg and not wt_set: #do not add the same wine twice, and do not add a wine we've already sold
    fg.add_node(wine)
    g_wine_node_count += 1

  if not pt_set and not wt_set:
    fg.add_edge(person, wine)
  if not pt_set:
    fg.add_edge(person, "r")

f = open(args.input, "r")

#PROCESS NODES
wine_sold = 0
lowest_wine_edge_count = 1
nodes_to_process = True

start = time.time()

more_file = True
while nodes_to_process:
  #REFILL THE BUFFER
  if (g_person_node_count+g_wine_node_count) < MIN_MEM_NODE_COUNT:
    print_text = True
    while (g_person_node_count+g_wine_node_count) < MAX_MEM_NODE_COUNT and more_file:
      if print_text: 
        print "FILLING BUFFER"
        print_text = False
      line = f.readline() #read in line from input
      if line:
        add_line_to_graph(line)
      else:
        more_file = False

  # WINE SECTION
  wine_node_with_fewest_edges = None
  wine_node_with_fewest_edges_edge_count = FEWER_COMPARE
  wine_search_count = 0
  person_skip_count = 0
  people_to_delete = []
  for node in nx.dfs_postorder_nodes(fg, "r"): #dfs postorder is magic and should be worshiped. --Andy Weir
    if node == "r": continue #skip root node
    if node[0] == "p": 
      if len(fg.neighbors(node)) == 1:
        people_to_delete.append(node)
      person_skip_count += 1
      continue 

    wine_neighbors = fg.neighbors(node)
    wine_neighbor_count = len(wine_neighbors)
    wine_search_count += 1

    if wine_neighbor_count <= wine_node_with_fewest_edges_edge_count:
      wine_node_with_fewest_edges = node
      wine_node_with_fewest_edges_edge_count = wine_neighbor_count
      if wine_neighbor_count <= lowest_wine_edge_count: break

  if wine_search_count > 25: #optimization that is unlikley to be needed with dfs postorder and these data sets
    lowest_wine_edge_count = min(lowest_wine_edge_count + 1, 10)
  else:
    lowest_wine_edge_count = wine_node_with_fewest_edges_edge_count
  # END WINE SECTION

  # we're out of edges, time to call it a day
  if not wine_node_with_fewest_edges:
    nodes_to_process = False
    break

  # PERSON SECTION
  person_node_with_fewest_edges = None
  person_node_with_fewest_edges_edge_count = FEWER_COMPARE
  for person_node in fg.neighbors(wine_node_with_fewest_edges):
    person_neighbors = fg.neighbors(person_node)
    person_neighbor_count = len(person_neighbors)

    if person_neighbor_count < person_node_with_fewest_edges_edge_count: #don't need the optimizations of the wine section here
      person_node_with_fewest_edges = person_node
      person_node_with_fewest_edges_edge_count = person_neighbor_count

      if person_neighbor_count == 1: break #special case still safe on persons neighbors
  # END PERSON SECTION

  #found node(s) to possibly remove/satisfy
  if person_node_with_fewest_edges and wine_node_with_fewest_edges:
    print "Traversed W#: {6: >5}\tTraversed P#: {7: >5}\tP-ID: {0: >10}\tW-ID: {1: >10}\tBuffer: {3: >8}\tW: {4: >10}\tP:{5:>10}\tSold: {2: >10}".format(person_node_with_fewest_edges,
                                                                            wine_node_with_fewest_edges,
                                                                            wine_sold,
                                                                            g_person_node_count+g_wine_node_count,
                                                                            g_wine_node_count,
                                                                            g_person_node_count,
                                                                            wine_search_count,
                                                                            person_skip_count
                                                                    )
    wine_sold += 1
    person_id = long(person_node_with_fewest_edges.replace("p",""))
    wine_id = long(wine_node_with_fewest_edges.replace("w",""))
    redis_set_value(person_id,"p")
    if redis_get_value(person_id,"p") == MAX_WINE:
      fg.remove_node(person_node_with_fewest_edges)
      g_person_node_count -= 1
    fg.remove_node(wine_node_with_fewest_edges)
    g_wine_node_count -= 1
    redis_set_value(wine_id,"w")
    redis_has_values = True
  
  #these are people that have no edges that matter, we'll delete them from the graph for now
  #we'll readd them should they show up in the input file again
  for person in people_to_delete:
    fg.remove_node(person)
    g_person_node_count -= 1

f.close()
print args.min_buffer_size, args.max_buffer_size, wine_sold, round(time.time()-start, 3)
