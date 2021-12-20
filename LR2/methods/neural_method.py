import json
import nltk
import pandas as pd
from collections import Counter
from keras.models import load_model
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import LabelEncoder

model = load_model('./methods/resources/neural/en_ru_model')
vectorizer = CountVectorizer(analyzer='char',
                             ngram_range=(3, 3),
                             vocabulary=json.load(open('./methods/resources/neural/vocabulary.json')))

languages = ['eng', 'rus']
encoder = LabelEncoder()
encoder.fit(languages)


def lang(text: str):
    corpus = nltk.sent_tokenize(text)
    x = vectorizer.fit_transform(corpus)
    feature_names = vectorizer.get_feature_names_out()

    x = pd.DataFrame(data=x.toarray(), columns=feature_names)
    y = model.predict(x)

    print(y)

    predictions = encoder.inverse_transform([0 if l[0] >= 0.5 else 1 for l in y])
    counter = Counter(predictions)

    if counter['rus'] > counter['eng']:
        return 'Russian'
    elif counter['rus'] < counter['eng']:
        return 'English'
    else:
        return 'Unable to recognize'
