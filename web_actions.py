import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import render_template, session
import spacy

menu_stopwords = {"in", "with", "and", "or"}


def initialize_glossary(data: pd.DataFrame):
    data["English"] = data["English"].str.lower()
    data["English"] = data["English"].str.replace(r'[^\w\s]', ' ', regex = True)
    glossary = set(data["English"].str.cat(sep=' ').split()) - menu_stopwords
    return glossary


def query_menu(query: str, menu: pd.DataFrame, glossary:set):

    # replace NaN elements with empty strings
    menu = menu.fillna('')
    # Combine Item Name with Description to Query both
    menu['query-text'] = menu['Dish'] + ' ' + menu['Description']
    # Convert text to lowercase
    menu['query-text'] = menu['query-text'].str.lower()
    # remove characters that aren't word or whitespace
    menu['query-text'] = menu['query-text'].str.replace(r'[^\w\s]', ' ', regex = True)

    # Tokenize the text data
    vectorizer = CountVectorizer()
    vectors = vectorizer.fit_transform(menu['query-text'])

    # extract keywords from query request
    keywords = [word for word in query.split()]
    keywords = [keyword.lower().replace(r'[^\w\s]', ' ') for keyword in keywords]
    keywords = [word for word in keywords if word in glossary]
    # Tokenize the keywords
    keyword_vectors = vectorizer.transform(keywords)

    # Calculate the cosine similarity between the keywords and the text data
    similarities = cosine_similarity(keyword_vectors, vectors)

    # Calculate the mean similarity score across all the keywords
    mean_similarities = similarities.mean(axis=0)

    # Add the mean similarities as a new column in the DataFrame
    menu['similarity'] = mean_similarities

    # Sort the DataFrame by the similarity column and return the most relevant results with a nonzero similarity score
    return menu.loc[menu['similarity'] != 0].sort_values(by='similarity', ascending=False).head(8)


def query_html(query: str, menu: pd.DataFrame, glossary:set):
    items = query_menu(query, menu, glossary)
    if items is None or items.empty:
        return render_template("chat-bubble-received.html",
                               message="I'm not sure what you mean, can you rephrase?")
    return render_template('menu-container.html', items=items)


def add_html(query: str, menu: pd.DataFrame, glossary:set):
    try:
        item_to_add = query_menu(query, menu, glossary).iloc[0]
    except IndexError:
        return render_template("chat-bubble-received.html",
                                message="I'm sorry, I couldn't find the item you were trying to add.")
    server_session_order = session["order"]
    item_to_add = item_to_add.to_dict()
    item_to_add["Quantity"] = 1
    session["order_total"] += float(item_to_add["Price"])
    for i, item in enumerate(server_session_order):
        if item["ID"] == item_to_add["ID"]:
            item["Quantity"] +=1
            session["order"] = server_session_order
            return render_template("chat-bubble-received.html",
                                   message=f"Added another {item['Dish']} to order")
    session["order"] = session["order"] + [item_to_add]
    return render_template("chat-bubble-received.html",
                           message=f"Added {session['order'][-1]['Dish']} to order")


def remove_html(query:str, glossary:set):
    if not session["order"]:
        return render_template("chat-bubble-received.html",
                               message="There's nothing in your cart to remove!")
    cart = pd.DataFrame.from_records(session['order'])
    try:
        item_to_remove = query_menu(query, cart, glossary).iloc[0]
    except IndexError:
        return render_template("chat-bubble-received.html",
                                message="I'm sorry, I couldn't find that item in your cart.")
    item_to_remove = item_to_remove.to_dict()
    server_session_order = [item for item in session["order"] if item["ID"] != item_to_remove["ID"]]
    session["order"] = server_session_order
    session["order_total"] -= float(item_to_remove['Price']) * int(item_to_remove['Quantity'])
    return render_template("chat-bubble-received.html",
                           message=f"{item_to_remove['Dish']} removed from cart.")

def test():
    nlp = spacy.load("en_core_web_md")
    data = pd.read_csv("data.csv")
    menu = pd.read_csv("menu.csv")
    # glossary = initialize_glossary(data)
    # print(glossary)
    # query_html("show me beef options", menu, glossary)
    # query_html("show me broccoli options", menu, glossary)


if __name__ == "__main__":
    test()
