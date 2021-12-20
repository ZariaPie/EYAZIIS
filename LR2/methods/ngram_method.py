import json

from nltk import sent_tokenize
from sklearn.feature_extraction.text import CountVectorizer

ru_profile = json.load(open('./methods/resources/ngram/rus.json'))
en_profile = json.load(open('./methods/resources/ngram/eng.json'))


def lang(text):
    vectorizer = CountVectorizer(analyzer='char',
                                 ngram_range=(5, 5),
                                 max_features=300)
    vectorizer.fit_transform(sent_tokenize(text))
    ngrams = vectorizer.get_feature_names_out()

    ru_dist = 0
    for i, ng in enumerate(ngrams):
        try:
            ru_dist += abs(ru_profile[ng] - i)
        except KeyError:
            ru_dist += 300  # max dist

    en_dist = 0
    for i, ng in enumerate(ngrams):
        try:
            en_dist += abs(en_profile[ng] - i)
        except KeyError:
            en_dist += 300  # max dist

    print(f'ru dist {ru_dist}, en dist {en_dist}')

    if en_dist < ru_dist:
        return 'English'
    elif en_dist > ru_dist:
        return 'Russian'
    else:
        return 'Unable to recognize'
