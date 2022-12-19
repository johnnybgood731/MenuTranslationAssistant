from googletrans import Translator


def translate(text, targetLanguage):
    translator = Translator()
    return translator.translate(text, dest=targetLanguage).text
