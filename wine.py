import networkx as nx
import argparse,sys
from operator import methodcaller

parser = argparse.ArgumentParser(description='')
parser.add_argument('--input', action="store", dest="input")
args= parser.parse_args()
MAX_WINE = 3

wg = nx.Graph()

f = open(args.input,"r")
for line in f:
  (person,wine) = line[0:-1].split("\t")
  #person = person.replace("person","p")
  #wine = wine.replace("wine","w")
  wg.add_node(person,{"count": 0})
  wg.add_node(wine)
  wg.add_edge(person,wine)
  
f.close()
print wg.number_of_nodes()
print wg.number_of_edges()

#TODO: test less graph-y approach, but I bet it will be unusuable as scale increases
#TODO: need to think of this in terms of map/combine/reduce (key for big data sets)
#TODO: output is out of order, easy fix if using mapreduce method, will have to output file, then fseek and change first line later... which stinks (for now)
#TODO: need to look into a method to iterate thought a sorted version of the nodes in order of edge count, not sure how to do this yet.

wine_sold = 0
lowest_wine_edge_count = 1
while True:
  #iterate though all wine nodes, find one with fewest edges
  #if edge count=1, just break and sell that wine right away no reason to further examine,no one else wants it
  
  # WINE SECTION
  wine_node_with_fewest_edges = None
  wine_node_with_fewest_edges_edge_count = 99999
  wine_search_count = 0
  for x in wg:
    print x,type(x)
    sys.exit()
  #print sorted(wg.nodes_iter(),key=len(methodcaller())[0:10]
  sys.exit()
  for node in wg.nodes_iter():
    if node[0]=="p": continue
    wine_search_count += 1
    wine_neighbors = wg.neighbors(node)
    wine_neighbor_count = len(wine_neighbors)
    if wine_neighbor_count == 0: continue

    if wine_neighbor_count < wine_node_with_fewest_edges_edge_count:
      wine_node_with_fewest_edges = node
      wine_node_with_fewest_edges_edge_count = wine_neighbor_count
      if wine_neighbor_count == lowest_wine_edge_count: break
  lowest_wine_edge_count = wine_node_with_fewest_edges_edge_count
  # END WINE SECTION

  #iterate through all connected people to that wine
  #get their edge count
  #person with fewest edge count should be removed (less likley to be fullfilled elsewhere)
  #if edge count=1, just break and assume that person is the best person to sell that wine to, as it is either the only, or only remaining wine they want

  # PERSON SECTION
  person_node_with_fewest_edges = None
  person_node_with_fewest_edges_edge_count = 99999
  for person_node in wg.neighbors(wine_node_with_fewest_edges):
    person_neighbors = wg.neighbors(person_node)
    person_neighbor_count = len(person_neighbors)

    if person_neighbor_count < person_node_with_fewest_edges_edge_count:
      person_node_with_fewest_edges = person_node
      person_node_with_fewest_edges_edge_count = person_neighbor_count
      
      if person_neighbor_count == 1: break #special case still safe on persons neighbors
  # END PERSON SECTION

  #found node(s) to possibly remove/satisfy
  if person_node_with_fewest_edges and wine_node_with_fewest_edges:
    wg.node[person_node_with_fewest_edges]["count"] += 1
    wine_sold += 1
    print "{3}/{4}\t{2}\t{0}\t{1}".format(person_node_with_fewest_edges,wine_node_with_fewest_edges,wine_sold,lowest_wine_edge_count,wine_search_count)
    if wg.node[person_node_with_fewest_edges]["count"] == MAX_WINE:
      wg.remove_node(person_node_with_fewest_edges)
    else:
      wg.remove_node(wine_node_with_fewest_edges)
  else: 
    #no more person -> wine links, time to wrap it up
    break

print wine_sold
