import pandas as pd
import spacy
# noinspection PyUnresolvedReferences
from pattern.en import number, ngrams
from transformers import pipeline
from task_manager import assist
from assistant_actions import *
from speech_text import *
from machine_translation import translate
import warnings
warnings.simplefilter("ignore", UserWarning)

THRESHOLD = 0.6


def main():
    # Load pipelines
    nlp = spacy.load("en_core_web_md")
    classifier = pipeline("token-classification", model="vblagoje/bert-english-uncased-finetuned-pos")

    # Remove all numbers from the list of stop words (obtained by finding CARDINAL entities in nlp.Defaults.stop_words)
    exceptions = ['none', 'nothing', 'twenty', 'eight', 'two', 'hundred', 'one', 'five',
                  'four', 'six', 'three', 'ten', 'fifty', 'nine', 'twelve']
    for exception in exceptions:
        nlp.Defaults.stop_words.remove(exception)

    # Load data
    data = pd.read_csv("data.csv").values.tolist()
    menu = pd.read_csv("menu.csv")
    menuItems = menu.values.tolist()

    # Initialize lists and variables
    request = ""
    language = ""
    orders = []
    transactions = []
    slots = ["none", [], [], "", 0]
    oldSlots = ["none", [], [], "", 0]

    isComplete = False
    while not isComplete:
        # Prompt assistance until all slots are filled
        filled = False
        while not filled:
            # Slots represent (in order) function, items, quantities, spicy level, drink
            oldSlots = list(slots)
            oldSlots[1] = list(slots[1])
            oldSlots[2] = list(slots[2])
            request, slots, language = assist(slots, orders, menuItems, nlp, classifier, language, data)
            if oldSlots == slots:
                text_to_speech(translate("Sorry, I didn't understand your request.", language), language)
            if slots[0] == "add":
                if len(slots[1]) > 0 and not (slots[3] == "" or slots[4] == 0) or (slots[1] == [] and slots[4] > 0):
                    filled = True
            elif slots[0] == "query" or slots[0] == "complete" or slots[0] == "remove" and len(slots[1]) > 0:
                filled = True

        # Given that all slots are filled, perform the requested action and ask for additional requests
        if slots[0] == "add":
            orders, transactions = addOrder(slots, orders, transactions, menuItems, language)
        elif slots[0] == "remove":
            orders, transactions = removeOrder(slots, orders, transactions, menuItems, language)
        elif slots[0] == "query":
            transactions = queryMenu(request, transactions, menuItems, nlp, classifier, language)
        elif slots[0] == "complete":
            transactions, isComplete = completeOrder(orders, transactions, menuItems, language)
        if slots[0] == "query":
            slots = list(oldSlots)
            slots[1] = list(oldSlots[1])
            slots[2] = list(oldSlots[2])
        else:
            slots = ["none", [], [], "", 0]
    text_to_speech(translate("Thank you for eating with us today!", language), language)

    return 0


if __name__ == '__main__':
    main()
