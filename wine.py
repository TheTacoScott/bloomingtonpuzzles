"""
wine.py
a bipartite non directed graphing solution to the bloomreach wine puzzle
example usage:
  python wine.py --input filename.txt
"""

import networkx as nx
import argparse, time

parser = argparse.ArgumentParser(description='')
parser.add_argument('--input', action="store", dest="input")
parser.add_argument('--min-buffer', action="store", dest="min_buffer_size", default=1000000)
parser.add_argument('--max-buffer', action="store", dest="max_buffer_size", default=1000000)
parser.add_argument('--maxwine', action="store", dest="max_wine", default=3)
parser.add_argument('--maxpref', action="store", dest="max_prefs", default=10)
args = parser.parse_args()

MAX_WINE = int(args.max_wine)
MIN_MEM_NODE_COUNT = int(args.min_buffer_size)
MAX_MEM_NODE_COUNT = int(args.max_buffer_size)
FEWER_COMPARE = int(args.max_prefs + 1)

fg = nx.Graph() #final graph
g_person_node_count = 0
g_wine_node_count = 0
g_root_node_count = 1

def add_line_to_graph(line):
  """
  helper function to parse and add a line to the graph
  """
  global g_person_node_count, g_wine_node_count
  (person, wine) = line[0:-1].split("\t")
  person = person.replace("person", "p")
  wine = wine.replace("wine", "w")
  if not person in fg:
    fg.add_node(person, {"c": 0})
    g_person_node_count += 1
  if not wine in fg:
    fg.add_node(wine)
    g_wine_node_count += 1
  fg.add_edge(person, wine)
  fg.add_edge(person, "r")

f = open(args.input, "r")
valid_line = True

#PROCESS NODES
wine_sold = 0
lowest_wine_edge_count = 1
nodes_to_process = True

start = time.time()

#PREFILL THE BUFFER
print "Prebuffering...",
file_done = False
line = f.readline() #read in line from input
while line and (g_person_node_count+g_wine_node_count) < MAX_MEM_NODE_COUNT:
  add_line_to_graph(line)
  line = f.readline() #read in line from input
  if not line: file_done = True #in case prebuffer is whole file
print "DONE"

while nodes_to_process:
  #REFILL THE BUFFER
  if (g_person_node_count+g_wine_node_count) < MIN_MEM_NODE_COUNT and not file_done:
    while (g_person_node_count+g_wine_node_count) < MAX_MEM_NODE_COUNT and not file_done:
      line = f.readline() #read in line from input
      if line:
        add_line_to_graph(line)
      else:
        file_done = True

  # WINE SECTION
  wine_node_with_fewest_edges = None
  wine_node_with_fewest_edges_edge_count = FEWER_COMPARE
  wine_search_count = 0
  for node in nx.dfs_postorder_nodes(fg, "r"): #dfs postorder is magic and should be worshiped. --Andy Weir
    if node == "r": continue #skip root node
    if node[0] == "p": continue #doubt we'll ever hit here, but skip people nodes

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
    fg.node[person_node_with_fewest_edges]["c"] += 1
    wine_sold += 1
    print "{2: >10}\t{0: >10}\t{1: >10}\tBuffer: {3}\tW: {4}\tP:{5}".format(person_node_with_fewest_edges,
                                                                            wine_node_with_fewest_edges,
                                                                            wine_sold,
                                                                            g_person_node_count+g_wine_node_count,
                                                                            g_wine_node_count,
                                                                            g_person_node_count)
    if fg.node[person_node_with_fewest_edges]["c"] == MAX_WINE:
      fg.remove_node(person_node_with_fewest_edges)
      g_person_node_count -= 1
    fg.remove_node(wine_node_with_fewest_edges)
    g_wine_node_count -= 1
f.close()
print args.min_buffer_size, args.max_buffer_size, wine_sold, round(time.time()-start, 3)
