from mrjob.job import MRJob
from mrjob.step import MRStep

class WineFind(MRJob):

    def steps(self):
      return [
        MRStep(mapper=self.edge_mapper,reducer=self.edge_reducer),
        #MRStep(mapper=self.sell_mapper),#,reducer=self.sell_reducer),
      ]
    def edge_mapper(self, _, line):
        person = line.split("\t")[0].replace("person","p")
        wine = line.split("\t")[1].replace("wine","w")
        yield "edges",wine + "-" + person

    def edge_reducer(self, key, values):
        w = {}
        p = {}

        for edge in values:
          (wine,person) = edge.split("-")

          if wine not in w:
            w[wine] = []
          if person not in p:
            p[person] = []

          if person not in w[wine]:
            w[wine].append(person)
          if wine not in p[person]:
            p[person].append(wine)

        
        for cwine in w:
          p_with_fewest_edges = None
          p_with_fewest_edges_count = 99999
          for cperson in w[cwine]:
            p_edge_count = len(p[cperson])
            if p_edge_count < p_with_fewest_edges_count:
              p_with_fewest_edges = cperson
              p_with_fewest_edges_count = p_edge_count                
          
          yield p_with_fewest_edges,cwine


if __name__ == '__main__':
    WineFind.run()
