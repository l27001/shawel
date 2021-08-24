#!/usr/bin/python3
import numpy as np
from random import randint
from methods import Methods
#data = open('input.txt', encoding='utf8').read()

def make_pairs(ind_words):
    for i in range(len(ind_words) - 1):
        yield (ind_words[i], ind_words[i + 1])

def make_bred(ind_words):
    pair = make_pairs(ind_words)
    word_dict = {}
    for word_1, word_2 in pair:
        if word_1 in word_dict.keys():
            word_dict[word_1].append(word_2)
        else:
            word_dict[word_1] = [word_2]

    first_word = np.random.choice(ind_words)

    while first_word.islower():
        chain = [first_word]
        n_words = randint(20, 35)
        first_word = np.random.choice(ind_words)

        for i in range(n_words+1):
            try: chain.append(np.random.choice(word_dict[chain[-1]]))
            except KeyError: pass
    return chain

if(__name__ == "__main__"):
    Mysql = Methods.Mysql()
    all_data = Mysql.query("SELECT * FROM markov", fetch="all")
    for data in all_data:
        word_count = len(data['data'].split())
        if(word_count >= 80):
            Methods.send(data['id'], f"[Бредогенератор v0.1]\nИсходное кол-во слов: {word_count}\n\n"+' '.join(make_bred(data['data'].split())))
            Mysql.query("UPDATE markov SET data = %s WHERE id = %s", (' '.join(data['data'].split()[word_count//2:]) ,data['id']))
    Mysql.close()
