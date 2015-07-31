from mrjob.job import MRJob


class WineFind(MRJob):

    def mapper(self, _, line):
        person = line.split("\t")[0]
        wine = line.split("\t")[1]
        yield "edges",wine + "-" + person

    def reducer(self, key, values):
        e = {}
        for edge in values:
          (wine,person) = edge.split("-")
          if wine not in e:
            e[wine] = []
          if person not in e[wine]:
            e[wine].append(person)
        for wine in e:
          yield "wine", "|".join(e[wine])


if __name__ == '__main__':
    WineFind.run()
