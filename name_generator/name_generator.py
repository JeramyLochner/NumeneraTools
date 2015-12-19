import random

class Markov(object):

    def __init__(self, open_file):
        self.cache = {}
        self.open_file = open_file
        self.names = self.file_to_names()
        self.names_size = sum([len(name) for name in self.names])
        self.database()

    def file_to_names(self):
        self.open_file.seek(0)
        names = [line.strip('\n') for line in self.open_file.readlines()]
        return names

    def triples(self):
        """ Generates triples from the given data string """
        for name in self.names:
            if len(name) < 3:
                self.names.remove(name)
                continue
            for i in range(len(name)-3):
                yield (name[i], name[i+1], name[i+2])

    def database(self):
        for l1, l2, l3 in self.triples():
            key = (l1, l2)
            if key in self.cache:
                self.cache[key].append(l3)
            else:
                self.cache[key] = [l3]

    def generate_markov_text(self, size=13):
        while True:
            seed_name = random.choice([name for name in self.names if len(name) > 3])
            seed = random.randint(0, len(seed_name)-3)
            seed_letter, next_letter = seed_name[seed], seed_name[seed+1]
            w1, w2 = seed_letter, next_letter
            gen_letters = []
            try:
                for i in range(size):
                    gen_letters.append(w1)
                    w1, w2 = w2, random.choice(self.cache[(w1, w2)])
                gen_letters.append(w2)
            except KeyError:
                continue
            return ''.join(gen_letters).lower().title()


#file_ = open('names.txt')

#markov = Markov(file_)

#for x in range(100):
#    print(markov.generate_markov_text(random.randint(4, 20)))


firstnames = open('firstnames.txt')
lastnames = open('lastnames.txt')

firstMarkov = Markov(firstnames)
lastMarkov = Markov(lastnames)

for x in range(0, 100):
    print(firstMarkov.generate_markov_text(random.randint(3, 10)) + ' ' + lastMarkov.generate_markov_text(random.randint(4, 12)))
