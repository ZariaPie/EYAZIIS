import io
import os
import re
from itertools import groupby

str_to_token = {'1': True,
                '0': False,
                'AND': lambda left, right: left and right,
                'OR': lambda left, right: left or right,
                'NOT': lambda right: not right,
                '(': '(',
                ')': ')'}

empty_res = True


def create_token_lst(s, str_to_token=str_to_token):
    s = s.replace('(', ' ( ')
    s = s.replace(')', ' ) ')

    return [str_to_token[it] for it in s.split()]


def find(lst, what, start=0):
    return [i for i,it in enumerate(lst) if it == what and i >= start]


def parens(token_lst):
    left_lst = find(token_lst, '(')

    if not left_lst:
        return False, -1, -1

    left = left_lst[-1]

    if token_lst[left + 1] != 0 and token_lst[left + 1] != 1:
        right = find(token_lst, ')', left + 3)[0]
    else:
        right = find(token_lst, ')', left + 4)[0]

    return True, left, right


def bool_eval(token_lst):
    if len(token_lst) == 2:
        return token_lst[0](token_lst[1])
    else:
        return token_lst[1](token_lst[0], token_lst[2])


def formatted_bool_eval(token_lst, empty_res=empty_res):
    if not token_lst:
        return empty_res

    if len(token_lst) == 1:
        return token_lst[0]

    has_parens, l_paren, r_paren = parens(token_lst)

    if not has_parens:
        return bool_eval(token_lst)

    token_lst[l_paren:r_paren + 1] = [bool_eval(token_lst[l_paren+1:r_paren])]

    return formatted_bool_eval(token_lst, bool_eval)


def nested_bool_eval(s):
    return formatted_bool_eval(create_token_lst(s))


def find_word(word):
    os.chdir("D:\\BSUIR\\ЕЯИИС\\LR1")
    result = 0
    for root, dirs, files in os.walk(".", topdown=False):
        for name in files:
            with io.open(os.path.join(root, name), encoding='utf-8') as file:
                for line in file:
                    if word in line:
                        result = 1
                        # print(os.path.join(root, name))
    return str(result)


def find_word_in_file(file, word, words_list):
    result = 0
    with io.open(file, encoding='utf-8') as file:
        for line in file:
            if word in line:
                result = 1
                words_list.append(word)
                # print(os.path.join(root, name))
    return str(result)


def find_in_dir(text):
    os.chdir("D:\\BSUIR\\ЕЯИИС\\LR1")
    for root, dirs, files in os.walk(".", topdown=False):
        for name in files:
            words_list=[]
            pattern = re.compile('\'(.*?)\'', re.S)
            file_search_str = re.sub(pattern, lambda m: find_word_in_file(os.path.join(root, name), m.group()[1:-1], words_list=words_list), text)
            RSV = nested_bool_eval(file_search_str)
            new_words_list = [el for el, _ in groupby(words_list)]
            if RSV:
                print("Файл: " + os.path.abspath(os.path.join(root, name)) + "\nСписок присутствующих слов: " + str(new_words_list))


def print_menu():
    print('\n--------------Меню---------------\n'
          '1. Логический поиск\n'
          '2. Информация о метриках\n'
          '3. Справка\n'
          '0. Выход')

def menu():
    x = 1
    while x:
        print_menu()
        x = int(input())
        if x == 1:
            print('Введите логическую формулу для поиска:')
            text = input()
            find_in_dir(text)
        elif x == 2:
            print('Логическая модель трактует термины в запросе как булевы переменные. \n'
                  'При наличии термина в документе соответствующая переменная принимает значение «true» (истина). \n'
                  'Присваивание терминам весовых коэффициентов не допускается.\n '
                  'Запросы формулируются как произвольные булевы выражения, связывающие термины с помощью стандартных логических операций: AND, OR или NOT.\n'
                  'Мерой соответствия запроса документу служит значение статуса выборки (RSV, retrieval status value).\n'
                  'В булевой модели статус выборки равен либо 1, если для данного документа вычисление выражения запроса дает значение «истина», либо 0 в противном случае. \n'
                  'Все документы с RSV = 1 считаются релевантными запросу.')
        elif x == 0:
            break;


# (('Рогожин' AND 'Мышкин') OR 'Каренина')

menu()