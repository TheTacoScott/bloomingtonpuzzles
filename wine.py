import networkx as nx
import argparse,sys,time

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
  fg.add_edge(person,"r")
  
f.close()

#TODO: test less graph-y approach, but I bet it will be unusuable as scale increases, and this is clearly a graphing problem
#TODO: need to think of this in terms of map/combine/reduce (big data yo)
#TODO: output is out of order, easy fix if using mapreduce method, will have to output file, then change first line later... which stinks (for now)
#TODO: need to look into a method to iterate thought a sorted version of the nodes in order of edge count, not sure how to do this yet.
#TODO: use an additional node with numeral name of how many edges the nodes under it have, use tree traversal to navigate down it pre/post
#TODO: break up data and make small graphs. bucket persons based on 1st 2 digits of id or some such. we'll lose edges, but the speed gain will be significant (similar in mapreduce)
#TODO: write my own distributed graph processing daemons to handle problems like this
#TODO: possibly have a rolling adjustment of wine node edge counts the processor will accept. start with 1, then if you have to traverse too far down the tree to find another 1, start accepting 2, etc.
#TODO: since we're a bipartite/non directed graph, we could use a maximal matching algorithm. (thanks old comp sci textbook for reminding me of names)

wine_sold = 0
lowest_wine_edge_count = 1
while True:
  #iterate though all wine nodes, find one with fewest edges
  #if edge count=1, just break and sell that wine right away no reason to further examine,no one else wants it

  start_wine = time.time()  
  # WINE SECTION
  wine_node_with_fewest_edges = None
  wine_node_with_fewest_edges_edge_count = 99999
  wine_search_count = 0
  to_delete = []
  #for node in fg.nodes_iter():
  for node in nx.dfs_postorder_nodes(fg,"r"):
    if node == "r": continue
    if node[0]=="p": continue
    wine_neighbors = fg.neighbors(node)
    wine_neighbor_count = len(wine_neighbors)
    if wine_neighbor_count == 0: 
      #having this happen is non-optimal but would be a part of any concept,minimize this
      to_delete.append(node)
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

  #iterate through all connected people to that wine
  #get their edge count
  #person with fewest edge count should be removed (less likley to be fullfilled elsewhere)
  #if edge count=1, just break and assume that person is the best person to sell that wine to, as it is either the only, or only remaining wine they want

  start_person = time.time()
  # PERSON SECTION
  person_node_with_fewest_edges = None
  person_node_with_fewest_edges_edge_count = 99999
  if not wine_node_with_fewest_edges: break #we're out of edges, time to call it a day
  for person_node in fg.neighbors(wine_node_with_fewest_edges):
    if person_node is None: break
    person_neighbors = fg.neighbors(person_node)
    person_neighbor_count = len(person_neighbors)

    if person_neighbor_count < person_node_with_fewest_edges_edge_count:
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
    print "{2}\t{0}\t{1}\tTraversed: {4}\tEdge Count: {3}".format(person_node_with_fewest_edges,wine_node_with_fewest_edges,wine_sold,lowest_wine_edge_count,wine_search_count)
    if fg.node[person_node_with_fewest_edges]["c"] == MAX_WINE:
      fg.remove_node(person_node_with_fewest_edges)
    else:
      fg.remove_node(wine_node_with_fewest_edges)
  else: 
    #no more person -> wine links, time to wrap it up
    break
  end_sell = time.time()

  start_cleanup = time.time()
  for wine_node in to_delete:
    fg.remove_node(wine_node)
  end_cleanup = time.time()
  #print "{0:.2f} {1:.2f} {2:.2f} {3:.2f}".format(end_wine-start_wine,end_person-start_person,end_sell-start_sell,end_cleanup-start_cleanup)


print wine_sold
