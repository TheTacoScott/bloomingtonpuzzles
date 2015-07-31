import networkx as nx
import argparse,sys
from operator import methodcaller

parser = argparse.ArgumentParser(description='')
parser.add_argument('--input', action="store", dest="input")
args= parser.parse_args()
MAX_WINE = 3

fg = nx.Graph() #final graph
ng = nx.Graph() #neighbor count graph

f = open(args.input,"r")
for line in f:
  (person,wine) = line[0:-1].split("\t")
  person = person.replace("person","p")
  wine = wine.replace("wine","w")
  fg.add_node(person,{"c": 0})
  fg.add_node(wine)
    
  fg.add_edge(person,wine)
  
f.close()
print fg.number_of_nodes()
print fg.number_of_edges()

neighbor_counts = []
for node in fg:
  if node[0]=="p": continue
  neighbors = fg.neighbors(node)
  neighbor_count = len(neighbors)
  if neighbor_count not in neighbor_counts: neighbor_counts.append(neighbor_count)
  ng.add_edge(node,neighbor_count)

fg = nx.disjoint_union(fg,ng)
print fg.number_of_nodes()
print fg.number_of_edges()
sys.exit()  
#need to optimize the internal structure of the graph for quicker traversal
#current_length = 1
#wg_count = wg.number_of_nodes()
#while fg.number_of_nodes() != wg_count:
#  to_delete = []
#  for node in wg:
#    if node[0] == "p": continue
#    neighbors = wg.neighbors(node)
#    neighbor_count = len(neighbors)
#    if neighbor_count == current_length:
#      print current_length,node,neighbors,neighbor_count
#      fg.add_node(node)
#      for neighbor_node in neighbors:
#        fg.add_node(neighbor_node,{"count": 0})
#        fg.add_edge(node,neighbor_node)
#  current_length += 1
#
#  for node in to_delete:
#    wg.remove_node(node)

#TODO: test less graph-y approach, but I bet it will be unusuable as scale increases
#TODO: need to think of this in terms of map/combine/reduce (key for big data sets)
#TODO: output is out of order, easy fix if using mapreduce method, will have to output file, then fseek and change first line later... which stinks (for now)
#TODO: need to look into a method to iterate thought a sorted version of the nodes in order of edge count, not sure how to do this yet.

wine_sold = 0
for neighbor_count in neighbor_counts:
  for wine_node in nx.dfs_preorder_nodes(ng,neighbor_count):
    if wine_node==neighbor_count: continue
    neighbors = fg.neighbors(wine_node)
    neighbor_count = len(neighbors)
    if neighbor_count == 1:
      print "{0} {1}".format(neighbors[0],wine_node)
      fg.remove_node(wine_node)
      wine_sold += 1
    

sys.exit()
lowest_wine_edge_count = 1
while True:
  #iterate though all wine nodes, find one with fewest edges
  #if edge count=1, just break and sell that wine right away no reason to further examine,no one else wants it
  
  # WINE SECTION
  wine_node_with_fewest_edges = None
  wine_node_with_fewest_edges_edge_count = 99999
  wine_search_count = 0
  to_readd = []
  for node in fg.nodes_iter():
    if node[0]=="p": continue
    wine_search_count += 1
    wine_neighbors = fg.neighbors(node)
    wine_neighbor_count = len(wine_neighbors)
    if wine_neighbor_count == 0: continue

    if wine_neighbor_count < wine_node_with_fewest_edges_edge_count:
      wine_node_with_fewest_edges = node
      wine_node_with_fewest_edges_edge_count = wine_neighbor_count
      if wine_neighbor_count == lowest_wine_edge_count: break
  #  else:
  #    if wine_search_count > 1:
  #      to_readd.append(node)
  #for node in to_readd:
  #  wine_node = node 
  #  person_nodes = fg.neighbors(wine_node)
  #  person_counts = {}
  #  for person_node in person_nodes:
  #    print person_node,len(to_readd),fg[person_node]["count"]
  #    person_counts[person_node] = fg[person_node]["count"]
  #  print wine_node,person_nodes,person_counts
        
  lowest_wine_edge_count = wine_node_with_fewest_edges_edge_count
  # END WINE SECTION

  #iterate through all connected people to that wine
  #get their edge count
  #person with fewest edge count should be removed (less likley to be fullfilled elsewhere)
  #if edge count=1, just break and assume that person is the best person to sell that wine to, as it is either the only, or only remaining wine they want

  # PERSON SECTION
  person_node_with_fewest_edges = None
  person_node_with_fewest_edges_edge_count = 99999
  for person_node in fg.neighbors(wine_node_with_fewest_edges):
    person_neighbors = fg.neighbors(person_node)
    person_neighbor_count = len(person_neighbors)

    if person_neighbor_count < person_node_with_fewest_edges_edge_count:
      person_node_with_fewest_edges = person_node
      person_node_with_fewest_edges_edge_count = person_neighbor_count
      
      if person_neighbor_count == 1: break #special case still safe on persons neighbors
  # END PERSON SECTION

  #found node(s) to possibly remove/satisfy
  if person_node_with_fewest_edges and wine_node_with_fewest_edges:
    fg.node[person_node_with_fewest_edges]["c"] += 1
    wine_sold += 1
    print "{3}/{4}\t{5}\t{2}\t{0}\t{1}".format(person_node_with_fewest_edges,wine_node_with_fewest_edges,wine_sold,lowest_wine_edge_count,wine_search_count,skip_count)
    if fg.node[person_node_with_fewest_edges]["c"] == MAX_WINE:
      fg.remove_node(person_node_with_fewest_edges)
    else:
      fg.remove_node(wine_node_with_fewest_edges)
  else: 
    #no more person -> wine links, time to wrap it up
    break

print wine_sold
