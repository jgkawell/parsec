import yaml

from nltk.corpus import wordnet


class ProcessInput:

    def __init__(self, dictFile):
        self.file = dictFile
        self.corrDict = {}
        self.stop_words = set(['the', 'is', 'and', 'a',
                               'like', 'i', 'that', 'didn\'t'])

    # build dictionary of comparison words
    def build_dicts(self):
        with open(self.file) as file:
            file_data = yaml.load(file, Loader=yaml.FullLoader)

            for corr in file_data.items():
                self.corrDict[corr[0]] = corr[1]

    # check the synset definitions of a word to find match dictionary entry
    def check_definitions(self, word):
        sets = wordnet.synsets(word)
        for s in sets:
            print(s)
            print("Synset definition: {}\n".format(s.definition()))

    # check similarity to words in dictionaries
    def get_similarity_scores(self, word):
        ret = [None, 0]
        for k in self.corrDict:
            # check if word matches any in dictionary
            if self.corrDict[k]['exact'] and word in self.corrDict[k]['exact']:
                ret[0] = k
                ret[1] = 1.0
                return ret
        # if word doesnt match generate similarity scores
        for k in self.corrDict:
            if self.corrDict[k]['match']:
                # itterate over synsets for words in dict
                for match in self.corrDict[k]['match']:
                    comp = wordnet.synset(match)
                    # generate a score for each definition of word
                    scores = [syn.wup_similarity(comp) for syn in
                              wordnet.synsets(word) if syn.wup_similarity(comp)
                              is not None]
                    # take the max score if it exists
                    largest = max(scores) if scores else 0
                    # if largest score is larger than cur max replace cur max
                    if largest > ret[1]:
                        ret[1] = largest
                        ret[0] = k
        return ret

    # function to get parameter/constraint correlations based on user input
    def process_input(self, string):
        # convert to list removing stopwords
        words = [word for word in string.split()
                 if word not in self.stop_words]
        keys = self.corrDict.keys()
        scores = dict(zip(keys, [0] * len(keys)))
        # itterate through words and generate similarities
        for word in words:
            # generate similarity max score
            ret = self.get_similarity_scores(word)
            # if largest similarity is larger than the
            # current similarity for a word replace it
            if ret[1] > scores.get(ret[0], 0):
                scores[ret[0]] = ret[1]
        # normalize similarity scores
        s = sum([scores[score] for score in scores])
        scores = {score: scores[score] / s for score in scores}
        return scores
