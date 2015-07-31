from mrjob.job import MRJob


class WineFind(MRJob):

    def mapper(self, _, line):
        person = line.split("\t")[0]
        wine = line.split("\t")[1]
        yield "edge",wine + "-" + person

    def reducer(self, key, values):
        yield key, "|".join(values)


if __name__ == '__main__':
    WineFind.run()
