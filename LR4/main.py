import json

import wikipedia as wikipedia
from vosk import Model, KaldiRecognizer
import nltk
import pymorphy2
import os
import pyaudio

model = Model(r"vosk-model-small-ru-0.22")
nltk.download('punkt')
wikipedia.set_lang("ru")

rec = KaldiRecognizer(model, 16000)
p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=16000
)
stream.start_stream()
start = 0

morph = pymorphy2.MorphAnalyzer()

while True:
    data = stream.read(4000)
    if len(data) == 0:
        break

    recognized_data = rec.Result() if rec.AcceptWaveform(data) else rec.PartialResult()
    result = ''
    if 'старт' in recognized_data:
        start = 1
    if start:
        if 'text' in json.loads(recognized_data):
            result = json.loads(recognized_data)['text']
            if result != '':
                print(result)
                words = nltk.word_tokenize(result)
                for i, word in enumerate(words):
                    words[i] = morph.normal_forms(word)[0]
                print(words)
                if 'википедия' in words:
                    results = wikipedia.summary(' '.join(words[1:]), sentences=5)
                    print(results)
                if 'создать файл' in ' '.join(words):
                    open(words[2], 'w')
                if 'открыть файл' in ' '.join(words):
                    file = open(words[2], 'r')
                    print(file.read())
                if 'записать файл' in ' '.join(words):
                    file = open(words[2], 'w')
                    file.write(' '.join(words[3:]))
                    file.close()

    if 'стоп' in recognized_data:
        break



    if rec.AcceptWaveform(data):
        print(rec.Result())
    else:
        print('----------')
        print(rec.PartialResult())
    recognized_data = rec.Result()

print(rec.FinalResult())
