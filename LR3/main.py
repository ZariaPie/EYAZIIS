import math
import re

import nltk
import numpy as np
import pysummarization
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
import numpy as np


def read_article(file_name):
    file = open(file_name, "r", encoding='utf-8')
    filedata = file.read()
    article = filedata.split(".")
    sentences = []

    for sentence in article:
        sentences.append(re.sub("[^a-zA-Zа-яА-Я]", " ", sentence).split(" "))
    sentences.pop()

    return sentences


def get_word_freq(word, text):
    word_freq = 0

    for sentence in text:
        word_freq += word_freq_sent(word, sentence)

    return word_freq


def get_max_word_freq(text):
    words_freq = dict()
    max_freq = 0

    for sentence in text:
        for cur_word in sentence:
            if cur_word in words_freq:
                if words_freq[cur_word] > max_freq:
                    max_freq = words_freq[cur_word]
                words_freq[cur_word] += 1
            else:
                words_freq[cur_word] = 1

    return max_freq


def texts_with_word(word, texts):
    text_count = 0

    for text in texts:
        for sentence in text:
            # print(sentence)
            if word in sentence:
                text_count += 1
                break

    return text_count


def word_freq_sent(word, sentence):
    word_freq = 0

    for cur_word in sentence:
        if cur_word == word:
            word_freq += 1

    return word_freq


def word_weight(word, text, texts):
    weigth = 0.5 * (1 + get_word_freq(word, text)/get_max_word_freq(text))*math.log(len(texts)/texts_with_word(word, texts))
    return weigth


def get_score(sentence, text, texts, stopwords):
    score = 0
    for word in sentence:
        if word not in stopwords:
            score += word_freq_sent(word, sentence)*word_weight(word, text, texts)
    return score


def get_pos(sentence: list, text:str):
    return 1 - text.find(' '.join(sentence)) /len(text)


def generate_summary(file_name, texts, top_n=5):
    stop_words = stopwords.words('russian')
    summarize_text = []

    statistic = []

    # Step 1 - Read text anc split it
    sentences = read_article(file_name)
    print(sentences)

    text = ''
    for sentence in sentences:
        text += ' '.join(sentence) + '.'

    for sentence in sentences:
        statistic.append([sentence, get_score(sentence, sentences, texts, stop_words), get_pos(sentence, text)])

    statistic.sort(key=lambda x: x[1], reverse=True)
    most_weight = statistic[:10]
    most_weight.sort(key=lambda x: x[2], reverse=True)
    print(most_weight)

    text = ''
    for i in range(len(most_weight)):
        text += ' '.join(most_weight[i][0]) + '\n'

    print(text)

    # Step 2 - Generate Similary Martix across sentences


text_names = ["war_1_ru.txt", "war_2_ru.txt", "war_3_ru.txt"]
texts = []

for text_name in text_names:
    texts.append(read_article(text_name))

generate_summary("war_1_ru.txt", texts)
words = dict()
stop_words = stopwords.words('russian')

for sentence in texts[0]:
    for term in sentence:
        if term.lower() not in words and term.lower() not in stop_words and term != '':
            words[term] = get_word_freq(term, texts[0])

sorted_words = sorted(words.items(), key=lambda x:x[1], reverse=True)
for i in range(11):
    print(sorted_words[i])



import pysummarization
from pysummarization.nlpbase.auto_abstractor import AutoAbstractor
from pysummarization.tokenizabledoc.simple_tokenizer import SimpleTokenizer
from pysummarization.abstractabledoc.top_n_rank_abstractor import TopNRankAbstractor


f = open("war_1_ru.txt", "r", encoding='utf-8')
document = f.read()


auto_abstractor = AutoAbstractor()
auto_abstractor.tokenizable_doc = SimpleTokenizer()
auto_abstractor.delimiter_list = [".", "\n"]
abstractable_doc = TopNRankAbstractor()
result_dict = auto_abstractor.summarize(document, abstractable_doc)

for sentence in result_dict["summarize_result"]:
    print(sentence)

