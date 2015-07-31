import networkx as nx
import argparse,sys,time

parser = argparse.ArgumentParser(description='')
parser.add_argument('--input', action="store", dest="input")
args= parser.parse_args()
MAX_WINE = 3
MAX_MEM_NODE_COUNT = 1000000

fg = nx.Graph() #final graph
ng = nx.Graph() #neighbor count graph
g_person_node_count = 0
g_wine_node_count = 0
g_root_node_count = 1

def add_line_to_graph(line):
  global g_person_node_count,g_wine_node_count
  (person,wine) = line[0:-1].split("\t")
  person = person.replace("person","p")
  wine = wine.replace("wine","w")
  if not person in fg:
    fg.add_node(person,{"c": 0})
    g_person_node_count += 1
  if not wine in fg:
    fg.add_node(wine)
    g_wine_node_count += 1
  fg.add_edge(person,wine)
  fg.add_edge(person,"r")

f = open(args.input,"r")
valid_line = True

#PROCESS NODES
wine_sold = 0
lowest_wine_edge_count = 1
nodes_to_process = True

#PREFILL THE BUFFER
line = f.readline() #read in line from input
while line and (g_person_node_count+g_wine_node_count) < MAX_MEM_NODE_COUNT:
  add_line_to_graph(line)
  line = f.readline() #read in line from input

while nodes_to_process:

  #REFILL THE BUFFER
  if (g_person_node_count+g_wine_node_count) < MAX_MEM_NODE_COUNT:
    line = f.readline() #read in line from input
    if line:
      add_line_to_graph(line)

  start_wine = time.time()
  # WINE SECTION
  wine_node_with_fewest_edges = None
  wine_node_with_fewest_edges_edge_count = 99999 #the shame of a hard coded constant
  wine_search_count = 0
  wine_with_no_edges = []
  for node in nx.dfs_postorder_nodes(fg,"r"): #dfs postorder is magic and should be worshiped. --Andy Weir
    if node == "r": continue #skip root node
    if node[0]=="p": continue #doubt we'll ever hit here, but skip people nodes

    wine_neighbors = fg.neighbors(node)
    wine_neighbor_count = len(wine_neighbors)

    if wine_neighbor_count == 0: #no one wants this wine. having this happen is non-optimal but would be a part of any concept,minimize this
      wine_with_no_edges.append(node)
      continue
    wine_search_count += 1

    if wine_neighbor_count <= wine_node_with_fewest_edges_edge_count:
      wine_node_with_fewest_edges = node
      wine_node_with_fewest_edges_edge_count = wine_neighbor_count
      if wine_neighbor_count <= lowest_wine_edge_count: break
  if wine_search_count > 25:
    lowest_wine_edge_count = min(lowest_wine_edge_count + 1,10)
  else:
    lowest_wine_edge_count = wine_node_with_fewest_edges_edge_count
  # END WINE SECTION
  end_wine = time.time()
  if not wine_node_with_fewest_edges: 
    nodes_to_process = False
    break #we're out of edges, time to call it a day

  start_person = time.time()
  # PERSON SECTION
  person_node_with_fewest_edges = None
  person_node_with_fewest_edges_edge_count = 99999 #the TWICE shame of a hard coded constant
  for person_node in fg.neighbors(wine_node_with_fewest_edges):
    person_neighbors = fg.neighbors(person_node)
    person_neighbor_count = len(person_neighbors)

    if person_neighbor_count < person_node_with_fewest_edges_edge_count: #don't need the optimizations of the wine section here
      person_node_with_fewest_edges = person_node
      person_node_with_fewest_edges_edge_count = person_neighbor_count

      if person_neighbor_count == 1: break #special case still safe on persons neighbors
  # END PERSON SECTION
  end_person = time.time()

  start_sell = time.time()
  #found node(s) to possibly remove/satisfy
  if person_node_with_fewest_edges and wine_node_with_fewest_edges:
    fg.node[person_node_with_fewest_edges]["c"] += 1
    wine_sold += 1
    print "{2}\t{0}\t{1}\tTraversed: {4}\tEdge Count: {3}\tBuffer: {5}\tW: {6}\tP:{7}".format(person_node_with_fewest_edges,wine_node_with_fewest_edges,wine_sold,lowest_wine_edge_count,wine_search_count,g_person_node_count+g_wine_node_count,g_wine_node_count,g_person_node_count)
    #print "{0}\t{1}".format(person_node_with_fewest_edges,wine_node_with_fewest_edges)
    if fg.node[person_node_with_fewest_edges]["c"] == MAX_WINE:
      fg.remove_node(person_node_with_fewest_edges)
      g_person_node_count -= 1 
    else:
      fg.remove_node(wine_node_with_fewest_edges)
      g_wine_node_count -= 1
  end_sell = time.time()

  start_cleanup = time.time()
  for wine_node in wine_with_no_edges:
    fg.remove_node(wine_node)
  end_cleanup = time.time()
  #print "{0:.2f} {1:.2f} {2:.2f} {3:.2f}".format(end_wine-start_wine,end_person-start_person,end_sell-start_sell,end_cleanup-start_cleanup)
f.close()
print wine_sold
