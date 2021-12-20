import os
import re

import nltk
import pymorphy2
import requests
from bs4 import BeautifulSoup
from nltk import CFG
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import pandas as pd
from tabulate import tabulate


def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN


V_list = []
Det_list = []
N_list = []
P_list = []
ADJ_list = []
RB_list = []
PRP_list = []


def create_grammar(sentence):
    tokenized_text = nltk.word_tokenize(sentence)
    tagged = nltk.pos_tag(tokenized_text)
    for i in range(len(tagged)):
        if re.match(r'VB', tagged[i][1]) or re.match((r'MD'), tagged[i][1]):
            V_list.append(tagged[i][0])
        elif re.match((r'DT'), tagged[i][1]) or re.match((r'WD'), tagged[i][1]) or re.match((r'WP'), tagged[i][
            1]) or re.match((r'WRB'), tagged[i][1]):
            Det_list.append(tagged[i][0])
        elif re.match((r'NN'), tagged[i][1]) or re.match((r'NNS'), tagged[i][1]) or re.match((r'NNP'), tagged[i][
            1]) or re.match((r'NNPS'), tagged[i][1]):
            N_list.append(tagged[i][0])
        elif 'PRP' == tagged[i][1]:
            PRP_list.append(tagged[i][0])
        elif re.match((r'TO'), tagged[i][1]) or re.match((r'IN'), tagged[i][1]) or 'PR' == tagged[i][1] or 'CC' == \
                tagged[i][1]:
            P_list.append(tagged[i][0])
        elif re.match((r'JJ'), tagged[i][1]) or 'PRP$' == tagged[i][1]:
            ADJ_list.append(tagged[i][0])
        elif re.match((r'RB'), tagged[i][1]):
            RB_list.append(tagged[i][0])


def parse(text):
    split_regex = re.compile(r'[.|!|?|…]')
    sentences = filter(lambda t: t, [t.strip() for t in split_regex.split(text)])
    count = 0
    for sentence in sentences:
        create_grammar(sentence)
        grammar_str = add_all_rules(start_grammar_str, V_list, Det_list, N_list, P_list, ADJ_list, RB_list, PRP_list)
        grammar = CFG.fromstring(grammar_str)
        ("\n======= " + str(sentence) + " =========")
        sent = sentence.split()
        parser = nltk.ChartParser(grammar)
        final_str = ''
        for t in parser.parse(sent):
            print(t)
            final_str += str(t)
        count += 1
        del N_list[:]
        del V_list[:]
        del Det_list[:]
        del N_list[:]
        del P_list[:]
        del ADJ_list[:]
        del RB_list[:]
        del PRP_list[:]


def add_rule(tagged_words, total_str):
    total_str += " \"" + tagged_words[0] + "\""
    for i in range(1, len(set(tagged_words))):
        total_str += " | \"" + tagged_words[i] + "\""
    return total_str


start_grammar_str = """S -> NP VP | S P S | S S
        VP -> V | V NP | V NP PP | V ADJ | V RB | V VP | P V | V NP | P V PRP | V RB V NP 
        PP -> P NP
        NP -> Det N | Det N PP | N | Det ADJ N | Det ADJ ADJ N | Det ADJ N PP | Det ADJ ADJ N PP | ADJ N PP | ADJ ADJ N PP | PRP | N PP | ADJ N """


def add_all_rules(total_str, V_list, Det_list, N_list, P_list, ADJ_list, RB_list, PRP_list):
    if len(set(V_list)) > 0:
        total_str += "\n\t\tV ->"
        total_str = add_rule(V_list, total_str)
    if len(set(Det_list)) > 0:
        total_str += "\n\t\tDet ->"
        total_str = add_rule(Det_list, total_str)
    if len(set(N_list)) > 0:
        total_str += "\n\t\tN ->"
        total_str = add_rule(N_list, total_str)
    if len(set(P_list)) > 0:
        total_str += "\n\t\tP ->"
        total_str = add_rule(P_list, total_str)
    if len(set(RB_list)) > 0:
        total_str += "\n\t\tRB ->"
        total_str = add_rule(RB_list, total_str)
    if len(set(ADJ_list)) > 0:
        total_str += "\n\t\tADJ ->"
        total_str = add_rule(ADJ_list, total_str)
    if len(set(PRP_list)) > 0:
        total_str += "\n\t\tPRP ->"
        total_str = add_rule(PRP_list, total_str)
    return total_str


def translate(text):
    rs = requests.get('http://www.7english.ru/dictionary.php?id=2000&letter=all')
    root = BeautifulSoup(rs.content, 'html.parser')

    en_ru_items = dict()
    f = open('result.txt', 'w', encoding='utf-8')
    f.close()
    f = open('result.txt', 'a', encoding='utf-8')
    f.write('Входной текст: ' + text)
    for tr in root.select('tr[onmouseover]'):
        td_list = [td.text.strip() for td in tr.select('td')]
        # Количество ячеек в таблице со словами — 9
        if len(td_list) != 9 or not td_list[1] or not td_list[5]:
            continue
        en = td_list[1]
        # Перевод английских слов предлагает несколько вариантов, мы берем первое слово из них
        ru = td_list[5].split(', ')[0]
        en_ru_items[en] = ru

    with open('dict_en_ru.txt', 'w') as file:
        file.write(str(en_ru_items))
    lemmatizer = WordNetLemmatizer()
    words = nltk.word_tokenize(text)
    print("Количество слов во входном тексте: ", len(words))
    result = []
    # Подсчет частоты встречаемости слов
    words_count = {i: words.count(i) for i in words}
    print('Дерево синтаксического разбора: ')
    parse(text)
    words_stat = []
    translated_count = 0
    morph = pymorphy2.MorphAnalyzer()

    for word in words_count.keys():
        if word == 'I':
            lemma = lemmatizer.lemmatize(word)
        else:
            lemma = lemmatizer.lemmatize(word.lower())
        # lemma = lemmatizer.lemmatize(word.lower())
        # переведенное слово en_ru_items.get(lemma)
        if en_ru_items.get(lemma) is not None:
            p = morph.parse(en_ru_items.get(lemma))[0]
            words_stat.append([word, en_ru_items.get(lemma), words_count[word],
                               re.sub('({})'.format('|'.join(map(re.escape, translator.keys()))),
                                      lambda m: translator[m.group()], str(p.tag.POS)),
                               re.sub('({})'.format('|'.join(map(re.escape, translator.keys()))),
                                      lambda m: translator[m.group()], str(p.tag.gender)),
                               re.sub('({})'.format('|'.join(map(re.escape, translator.keys()))),
                                      lambda m: translator[m.group()], str(p.tag.number))])
        else:
            words_stat.append([word, 'N/A', words_count[word], 'N/A', 'N/A', 'N/A'])
        words_stat.sort(key=lambda x: x[2], reverse=True)
    df = pd.DataFrame(words_stat)
    col = list(["Слово", "Перевод", "Сколько раз встречается", "Часть речи", "Род", "Число"])
    df.columns = col
    df.style.hide_index()
    pprint_df(df.head())
    for token in nltk.pos_tag(words):
        if token[0] == 'I':
            lemma = lemmatizer.lemmatize(token[0], pos=get_wordnet_pos(token[1]))
        else:
            lemma = lemmatizer.lemmatize(token[0].lower(), pos=get_wordnet_pos(token[1]))
        if en_ru_items.get(lemma) is not None:
            result.append(en_ru_items.get(lemma))
            translated_count += 1
    print("Переведено слов: " + str(translated_count))
    print('Перевод текста на русский язык: ' + ' '.join(result))
    f.write('\nПеревод входного текста: ' + ' '.join(result)+'\n')
    f.write(df.to_string(header=True, index=False))
    f.close()


def pprint_df(dframe):
    print(tabulate(dframe, headers='keys', tablefmt='psql', showindex=False))


def print_file():
    os.startfile("result.txt", "print")


def print_menu():
    print('\n--------------Меню---------------\n'
          '1. Перевод фразы\n'
          '2. Печать файла с результатами\n'
          '3. Справка\n'
          '0. Выход')


def menu():
    x = 1
    while x:
        print_menu()
        x = int(input())
        if x == 1:
            print('Введите текст для перевода:')
            text = input()
            translate(text)
        elif x == 2:
            print_file()
        elif x == 3:
            print('Система предназначена для перевода текстов с английского языка на русский и использует словарь, '
                  'содержащий перевод 2000 самых часто употребляемых слов английского языка.')
        elif x == 0:
            break


# для удобства пользователя значения, полученные библиотекой при морфологическом анализе, транслируются на русский язык
translator = {'NOUN': 'Имя существительное',
              'ADJF': 'Имя прилагательное (полное)',
              'ADJS': 'Имя прилагательное (краткое)',
              'COMP': 'Компаратив',
              'VERB': 'Глагол (личная форма)',
              'INFN': 'Инфинитив',
              'PRTF': 'Причастие (полное)',
              'PRTS': 'Причастие (краткое)',
              'GRND': 'Деепричастие',
              'NUMR': 'Числительное',
              'ADVB': 'Наречие',
              'NPRO': 'Местоимение',
              'PRED': 'Предикатив',
              'PREP': 'Предлог',
              'CONJ': 'Союз',
              'PRCL': 'Частица',
              'INTJ': 'Междометие',
              'nomn': 'Иминительный',
              'gent': 'Родительный',
              'datv': 'Дательный',
              'accs': 'Винительный',
              'ablt': 'Творительный',
              'loct': 'Предложный',
              'gen2': 'Родительный',
              'acc2': 'Винительный',
              'loc2': 'Предложный',
              'sing': 'Единственное число',
              'plur': 'Множественное число',
              'masc': 'Мужской род',
              'femn': 'Женский род',
              'neut': 'Средний род'
              }


menu()