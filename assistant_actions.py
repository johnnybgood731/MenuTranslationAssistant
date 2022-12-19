from speech_text import *
from machine_translation import translate
import tkinter as tk
from tkinter import ttk


def textBox(text):
    popup = tk.Tk()
    popup.wm_title("!")
    label = ttk.Label(popup, text=text, font=("Verdana", 10))
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Okay", command=popup.destroy)
    B1.pack()
    popup.mainloop()


def addOrder(slots, orders, transactions, menuItems, language):
    orders += [[slots[1], slots[2], slots[3], slots[4]]]
    transactions += [slots]
    for i, itemNumber in enumerate(slots[1]):
        name = menuItems[itemNumber - 1][2]
        if slots[2][i] == 1:
            text_to_speech(translate(name + " was added to your order.", language), language)
        else:
            text_to_speech(translate(str(slots[2][i]) + " orders of " + name +
                                     " was added to your order.", language), language)
    char = ''
    name = menuItems[slots[4] - 1][2]
    if name.lower()[0] == 'a' or name.lower()[0] == 'e' or name.lower()[0] == 'i' or \
            name.lower()[0] == 'o' or name.lower()[0] == 'u':
        char = 'n'
    if slots[4] > 0:
        text_to_speech(translate("A" + char + " " + name + " was added to your order.", language), language)

    return orders, transactions


def removeOrder(slots, orders, transactions, menuItems, language):
    flag = True
    for i, itemNumber in enumerate(slots[1]):
        name = menuItems[itemNumber - 1][2]
        quantity = slots[2][i]
        for order in orders:
            for j, item in enumerate(order[0]):
                if item == itemNumber and (order[1][j] > quantity or quantity <= 0):
                    if flag:
                        slots[2][i] = order[1][j]
                    else:
                        slots[2][i] += order[1][j]
                    flag = False
                    order[1][j] -= quantity
                    if quantity == 1:
                        text_to_speech(translate("1 order of " + name + " was removed from your order.", language),
                                       language)
                    else:
                        text_to_speech(translate(str(quantity) + "orders of " + name +
                                                 " was removed from your order.", language), language)
                    quantity = 0
                    break
                elif item == itemNumber:
                    if flag:
                        slots[2][i] = order[1][j]
                    else:
                        slots[2][i] += order[1][j]
                    if order[1][j] == 1:
                        text_to_speech(translate("1 order of " + name + " was removed from your order.", language),
                                       language)
                    else:
                        text_to_speech(translate(str(order[1][j]) + " orders of " + name +
                                                 " was removed from your order.", language), language)
                    quantity -= order[1][j]
                    order[1][j] = 0
                    flag = False
                    if quantity == 0:
                        break
            if quantity == 0:
                break
        if flag:
            slots[2][i] = 0
            text_to_speech(translate(str(menuItems[itemNumber - 1][2]) +
                                     " was not on your order, so I was unable to remove it.", language), language)
        transactions += [slots]
    for order in orders:
        needsRemoved = []
        for i, item in enumerate(order[0]):
            if order[1][i] == 0:
                needsRemoved += [i]
        counter = 0
        for i in range(len(needsRemoved)):
            order[0].pop(i - counter)
            order[1].pop(i - counter)
            counter += 1

    return orders, transactions


def queryMenu(response, transactions, menuItems, nlp, classifier, language):
    # Remove stop words and lemmatize the words in the query
    text_to_speech(translate("Here are the menu items that are similar:", language), language)
    transactions += [["query", response]]
    doc = nlp(response)
    doc = ' '.join([str(token.lemma_).lower() for token in doc if not token.is_stop and not token.is_punct])
    tokens = classifier(doc)
    doc = nlp(doc)

    # Extract Noun Chunks, Nouns, and Adjectives from the query
    chunks = doc.noun_chunks
    nounChunks = []
    nouns = []
    adjectives = []
    for chunk in chunks:
        nounChunks += [chunk.text]
    for token in tokens:
        if token["entity"] == 'NOUN' or token["entity"] == 'PROPN':
            nouns += [str(token["word"])]
        elif token["entity"] == 'ADJ':
            adjectives += [str(token["word"])]

    # Query the menu for items matching any of the Noun Chunks, Nouns, or Adjectives, in that order
    items = []
    for item in menuItems:
        doc = nlp(item[2])
        doc = nlp(' '.join([str(token.lemma_).lower() for token in doc if not token.is_stop and not token.is_punct]))
        docChunks = []
        for chunk in doc.noun_chunks:
            docChunks += [chunk.text]
        for nounChunk in nounChunks:
            if nounChunk in docChunks:
                items += [item]
    for item in menuItems:
        doc = nlp(item[2])
        doc = [str(token.lemma_).lower() for token in doc if not token.is_stop and not token.is_punct]
        for noun in nouns:
            if noun in doc:
                flag = True
                for x in items:
                    if item[0] == x[0]:
                        flag = False
                        break
                if flag:
                    items += [item]
    for item in menuItems:
        doc = nlp(item[2])
        doc = [str(token.lemma_).lower() for token in doc if not token.is_stop and not token.is_punct]
        for adjective in adjectives:
            if adjective in doc:
                flag = True
                for x in items:
                    if item[0] == x[0]:
                        flag = False
                        break
                if flag:
                    items += [item]

    # Display the query results to the user
    message = ""
    for item in items:
        if language == "en":
            message += f"{item[1]}.\t{item[2]}\t${item[5]}\n"
        else:
            message += f"{item[1]}.\t{item[3]}\t${item[5]}\n"
    textBox(message)

    return transactions


def completeOrder(orders, transactions, menuItems, language):
    # Confirm Order
    text_to_speech(translate("Here is your order:", language), language)
    message = ""
    for order in orders:
        for i, item_id in enumerate(order[0]):
            message += f"{order[1][i]} {order[2]} {menuItems[item_id - 1][2]}"
            message += f" with a {menuItems[order[3]][2]}" if order[3] != -1 else ""
            message += f"\t${order[1][i] * float(menuItems[item_id - 1][5])}\n"
    textBox(message)
    text_to_speech(translate("Is your order correct?", language), language)
    language, response = speech_to_text(language)
    response = translate(response, "en")
    while True:
        answer = ""
        for char in response.lower():
            if char == 'y' or char == 's':
                answer = "yes"
                break
            elif char == 'n':
                answer = "no"
                break
        if answer == "yes":
            text_to_speech(translate("Your server will bring your food to you. Enjoy your meal!", language), language)
            transactions += [["complete", answer]]
            return transactions, True
        elif answer == "no":
            transactions += [["complete", answer]]
            return transactions, False
        else:
            text_to_speech(translate("Sorry, I don't understand that response. Is your order correct?", language),
                           language)
            language, response = speech_to_text(language)
            response = translate(response, "en")
