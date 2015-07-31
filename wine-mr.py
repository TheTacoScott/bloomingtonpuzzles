from mrjob.job import MRJob
from mrjob.step import MRStep

class WineFind(MRJob):

    def steps(self):
      return [
        MRStep(mapper=self.edge_mapper,reducer=self.edge_reducer)
      ]
    def edge_mapper(self, _, line):
        person = line.split("\t")[0]
        wine = line.split("\t")[1]
        yield "edges",wine + "-" + person

    def edge_reducer(self, key, values):
        w = {}
        p = {}
        for edge in values:
          (wine,person) = edge.split("-")
          if person not in p: p[person] = []
          if wine not in w:   w[wine] = []

          if person not in w[wine]: w[wine].append(person)
          if wine not in p[person]: p[person].append(wine)

        for wine in w:
          yield wine, "|".join(w[wine])
        for person in p:
          yield person, "|".join(p[person])



if __name__ == '__main__':
    WineFind.run()
