import speech_recognition as sr
# from pprint import pprint
from gtts import gTTS
from playsound import playsound
from machine_translation import translate
import os


def speech_to_text(language):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
    if language == "":
        english_speech = r.recognize_google(audio, language='en')
        english_speech_confidence = r.recognize_google(audio, language='en', show_all=True)['alternative'][0][
            'confidence']
        chinese_speech = r.recognize_google(audio, language='zh')
        chinese_speech_confidence = r.recognize_google(audio, language='zh', show_all=True)['alternative'][0][
            'confidence']
        if english_speech_confidence >= chinese_speech_confidence:
            language = "en"
            transcript = english_speech
        else:
            language = "zh-CN"
            transcript = chinese_speech
    else:
        try:
            transcript = r.recognize_google(audio, language=language)
        except sr.UnknownValueError:
            text_to_speech(translate("Sorry, I did not understand your response.", language), language)
            transcript = None
    return language, transcript


def text_to_speech(message, language):
    if os.path.exists('DataFlair.mp3'):
        os.remove('DataFlair.mp3')
    speech = gTTS(text=message, lang=language, slow=False)
    speech.save('DataFlair.mp3')
    playsound('DataFlair.mp3')
