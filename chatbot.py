from flask import Flask, jsonify, request
import nltk
from nltk.stem import WordNetLemmatizer
import pickle
import numpy as np
import json
import random
from tensorflow.keras.models import load_model
import speech_recognition as sr
import pyttsx3
import os
import datetime
import wikipedia
import webbrowser
import smtplib
import json
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

app = Flask(__name__)

@app.route('/')
def home():
    dict_res = {
        'input': '',
        'response': 'Hi, my name is Joanna. How can I help you?',
    }
    return  dict_res

@app.route('/api/<string:user_input_text>')
def chatbot_response(user_input_text):
    lemmatizer = WordNetLemmatizer()
    intents = json.loads(open('intents.json').read())
    words = pickle.load(open('words.pkl', 'rb'))
    classes = pickle.load(open('classes.pkl', 'rb'))
    model = load_model('chatbot_model.h5')

    class chatBot():
        def __init__(self, name):
            print(f'Starting up, {name}')
            self.name = name

        def takeCommand(self):
            r = sr.Recognizer()
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source)
                print('Listening...')
                r.pause_threshold = 1
                audio = r.listen(source)
            try:
                print('Recognizing..')
                query = r.recognize_google(audio, language='en-in')
                print(f'User said: {query}\n')
            except Exception as e:
                print(e)
                print('Could you repeat that again please...')
                return 'none'
            return query

        def wake_up(self, text):
            if self.name.lower() in text:
                return True
            else:
                return False

        def speak(self, text):
            engine = pyttsx3.init('sapi5')
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[2].id)
            engine.say(text)
            print("AI --> ", text)
            engine.runAndWait()

        def wishMe(self):
            hour = int(datetime.datetime.now().hour)

            if hour >= 0 and hour < 12:
                res = 'Good Morning, Master Wayne!'
                # ai.speak('Good Morning, Master Wayne!')

            elif hour >= 12 and hour < 18:
                res = 'Good Afternoon, Master Wayne!'
                # ai.speak('Good Afternoon, Master Wayne!')

            else:
                res = 'Good Evening, Master Wayne!'
                # ai.speak('Good Evening, Master Wayne!')
            return res

        def filteredQuery(self, query):
            stop_words = set(stopwords.words('english'))
            word_tokens = word_tokenize(query)
            filtered_query = [w for w in word_tokens if not w.lower() in stop_words]
            bannedWord = ['google', 'search', 'open', 'start', 'youtube', 'play', 'wikipedia']
            query_1 = str()
            query_1 = (' '.join(w for w in filtered_query if w not in bannedWord))
            return query_1

        def action_time(self):
            return datetime.datetime.now().time().strftime('%H:%M')

        def clean_up_sentence(self, sentence):
            # tokenize the pattern - split words into array
            sentence_words = nltk.word_tokenize(sentence)
            # stem each word - create short form for word
            sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
            return sentence_words
            # return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

        def bow(self, sentence, words, show_details=True):
            # tokenize the pattern
            sentence_words = ai.clean_up_sentence(sentence)
            # bag of words - matrix of N words, vocabulary matrix
            bag = [0] * len(words)
            for s in sentence_words:
                for i, w in enumerate(words):
                    if w == s:
                        # assign 1 if current word is in the vocabulary position
                        bag[i] = 1
                        if show_details:
                            print("found in bag: %s" % w)
            return (np.array(bag))

        def predict_class(self, sentence, model):
            # filter out predictions below a threshold
            p = ai.bow(sentence, words, show_details=False)
            res = model.predict(np.array([p]))[0]
            ERROR_THRESHOLD = 0.25
            results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
            # sort by strength of probability
            results.sort(key=lambda x: x[1], reverse=True)
            return_list = []
            for r in results:
                # r[1] = str(r[1])
                return_list.append({"intent": classes[r[0]], "probability": r[1]})
            return return_list

        def getResponse(self, ints, intents_json):
            tag = ints[0]['intent']
            list_of_intents = intents_json['intents']
            for i in list_of_intents:
                if (i['tag'] == tag):
                    result = random.choice(i['responses'])
                    break
            return result

        def chatbot_response(self, text):
            ints = ai.predict_class(text, model)
            res = ai.getResponse(ints, intents)
            return res

    def chatbot_script(text):
        # text = input()
        # text = ai.takeCommand().lower()
        res = ''
        if ai.wake_up(text) == True:
            res = ai.wishMe()
            res = f"{res}. I am Joanna the AI. what can I do for you?"

        elif 'time' in text:
            res = ai.action_time()

        elif 'wikipedia' in text:
            # ai.speak('Searching wikipedia...')
            text = text.replace('wikipedia', '')
            results = wikipedia.summary(text, sentences=2)
            # ai.speak('According to wikipedia')
            # ai.speak(results)
            res = f'According to wikipedia, {results}'

        elif 'google' in text:
            # ai.speak('Opening google...')
            res = 'Opening google...'
            text = ai.filteredQuery(text)
            webbrowser.open(f'https://www.google.com/search?q={text}')

        elif 'youtube' in text:
            # ai.speak('Opening youtube...')
            res = 'Opening youtube...'
            text = ai.filteredQuery(text)
            webbrowser.open('youtube.com')

        elif 'music' in text:
            # ai.speak('Opening Amazon prime music...')
            res = 'Opening Amazon prime music...'
            webbrowser.open(
                'https://music.amazon.in/stations/A1ESXGJW9GSMCX?marketplaceId=A3K6Y4MI8GDYMT&musicTerritory=IN&ref=dm_sh_b0bokLtyOS6TlPaJjJxe0uCVE')

        elif 'stack overflow' in text:
            # ai.speak('Opening stack overflow...')
            res = 'Opening stack overflow...'
            webbrowser.open('stackoverflow.com')

        else:
            res = ai.chatbot_response(text)
        # ai.speak(res)
        return res

    ai = chatBot(name='Joanna')
    #user_input_text = 'hi'
    response = chatbot_script(user_input_text)
    dict_res = {
        'input': user_input_text,
        'response': response
    }
    return dict_res

if __name__ == '__main__':
    app.run(debug=True)