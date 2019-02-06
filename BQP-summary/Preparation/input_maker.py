"developer: pegah"

import collections
import string
import glob


from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
import os
import xml.etree.ElementTree as ET

#nltk.download('stopwords')
#nltk.download('punkt')

stop_words = set(stopwords.words('english'))
tokenizer = RegexpTokenizer(r'\w+')
exclude = set(string.punctuation)
path = os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + '/TAC/u08_corr/'


class BQP_input_maker:

    def __init__(self, original_text, bigram_text, path_):

        self.original_text = original_text[0:-10]+'concat.xml'
        self.bigram_text = bigram_text
        #self.valid_summary_list = valid_summary_list
        self.path_ = path_

    def is_filter_token(self, input):

        no_punctuation_list = []
        for ch in input:
            if ch in exclude:
                return True
            else:
                no_punctuation_list.append(ch)

        no_punctuation = ''.join(i for i in no_punctuation_list)
        input = tokenizer.tokenize(no_punctuation)

        for w in input:
            if w in stop_words:
                return True

        return False

    def tokens_dictionary(self):

        bigram_dict = {}

        with open(self.bigram_text) as f:
            for line in f:
                tempo = line
                tt = tempo.split('\t')

                bigram_dict[tt[0]] = tt[1][0:-1]

        return  bigram_dict

    def clean_tockens(self, bigram_dic):
        real_bigrm_dic = dict()

        for key, value in bigram_dic.items():
            if not self.is_filter_token(value):
                real_bigrm_dic[key] = value

        return real_bigrm_dic

    def get_xml_source(self, with_filter = True):
        name = "concat-"+ self.path_[-8:-3]

        if with_filter:
            file = open(self.path_ + name + ".txt", 'w+')
        else:
            file = open(self.path_ + name + ".txt", 'w+')

        tree = ET.parse(self.original_text)
        root = tree.getroot()

        "number of sentences in the document"
        num_sent = len([child for child in root])
        file.write(str(num_sent))
        file.write('\n')

        bigram_dic = self.tokens_dictionary()
        if with_filter:
            "if we remove stop words and punctuations from the birgams"
            filter_bigram = ex.clean_tockens(bigram_dic)
            bigram_keys = [i for i in filter_bigram.keys()]
        else:
            "if we do no filtering"
            bigram_keys = [i for i in bigram_dic.keys()]

        sent_length_list = []
        dic_sent_tokens = dict()

        sent_id = 0
        for child in root:

            _bigram = child.find('bigrams').text
            tt = child.find('raw')

            sent_length_list.append(len((tt.text).split(' ')))

            if _bigram is None:
                dic_sent_tokens[sent_id] = []
            else:
                text_bigram = _bigram.split(' ')

                if tt is None:
                    print('****')
                    print(child[0].text)


                new_text_bigram = [i for i in text_bigram if i in bigram_keys]
                dic_sent_tokens[sent_id] = new_text_bigram

            sent_id += 1

        seti = set([])
        for element in dic_sent_tokens.values():
            seti = seti | set(element)

        indexed_tockens = dict()

        # "number of tockens"
        # num_tockens = sum(len(i) for i in dic_sent_tokens.values())
        # file.write(str(num_tockens))
        # file.write('\n')

        counter = 0
        for element in seti:
            indexed_tockens[element] = counter
            counter +=1

        vocabulary_size = len(seti)
        "vocabulary size"
        file.write(str(vocabulary_size))
        file.write('\n')

        "list of sentences length for the original text"

        for i in sent_length_list:
            file.write(str(i))
            file.write('\t')
        file.write('\n')

        for element in dic_sent_tokens.values():
            vector = [0]*vocabulary_size
            if len(element) > 0:
                counter = collections.Counter(element)
                for token, counter_ in counter.items():
                    vector[indexed_tockens[token]] = counter_

            for i in vector:
                file.write(str(i))
                file.write('\t')

            file.write('\n')

        file.close()
        return

if __name__ == '__main__':

    def get_directories(path_):
        directories = None
        for root, dirs, files in os.walk(path_):
            directories = dirs
            break
        return directories

    directory = get_directories(path)
    bigram = None

    counter = 1
    for dir in directory:
        sub_path = path+dir+'/'
        bigram = sub_path + 'index_bigrams'

        sub_sub_path = sub_path + dir + '-A/'
        # files = glob.glob(sub_sub_path +"*.xml")
        if counter < 10:
            files = [sub_sub_path + "concat.xml"]
        else:
            files = [sub_sub_path + "concat.xml"]
        for orig in files:
            print(orig)
            ex = BQP_input_maker(orig, bigram, sub_sub_path)
            ex.get_xml_source(with_filter=True)

        counter += 1



# sub_path = '/home/pegah/Documents/research/DVRC/NLP-for-NLP/BQP-summary/TAC/u08_corr/D0838/'
# bigram = sub_path + 'index_bigrams'
# sub_sub_path = '/home/pegah/Documents/research/DVRC/NLP-for-NLP/BQP-summary/TAC/u08_corr/D0838/D0838-A/'
# orig = sub_path + '/D0838-A/concat.xml'
#
#
# ex = BQP_input_maker(orig, bigram, sub_sub_path)
# ex.get_xml_source(with_filter=True)
