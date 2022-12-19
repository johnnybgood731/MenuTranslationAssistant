import os
import pandas as pd
import spacy
from transformers import pipeline

from flask import Flask, request, Response, render_template, session
import nlu
import assistant_actions
import web_actions


def create_app(test_config=None):
    nlp = spacy.load("en_core_web_md")
    classifier = pipeline("token-classification", model="vblagoje/bert-english-uncased-finetuned-pos")
    action_words ={"order", "add", "take", "purchase", "buy", "get", "have","replace", "substitute","remove", "leave", "subtract", "cancel", "delete","query", "search", "list", "find", "show","finish", "exit", "complete", "checkout", "done", "nothing"}

    # Load data
    data = pd.read_csv("data.csv")
    glossary = web_actions.initialize_glossary(data)
    menu = pd.read_csv("menu.csv")
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='Cobalt15')

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Sends the appropriate response to a given prompt
    @app.route('/submit-prompt', methods=['POST'])
    def handle_prompt():
        # Get text if prompt
        prompt = request.json['textPrompt']
        # Add chat bubble with sent prompt
        response = render_template('chat-bubble-sent.html', message=prompt)
        # extract tokens from prompt
        tokens = classifier(prompt)
        # check for recommended actions and handle those

        # Determine desired action from prompt
        try:
            action, _ = max([nlu.identifyAction(nlp, token['word']) for token in tokens if token["entity"] == "VERB" or token['word'] in action_words], key=lambda x:x[1])
        except ValueError:
            response += render_template('chat-bubble-received.html',
                                        message="I'm not sure what you mean, can you rephrase?")
            return Response(response, mimetype='text/html')
        print(action)

        if action == 'add':
            response += web_actions.add_html(prompt, menu, glossary)
        elif action == 'remove':
            response += web_actions.remove_html(prompt, glossary)
        elif action == 'query':
            response += web_actions.query_html(prompt, menu, glossary)
        elif action == 'complete':
            response += render_template('checkout.html', cart=session["order"], total=session["order_total"])
            pass
        return Response(response, mimetype='text/html')

    @app.route('/', methods =['GET'])
    def home_page():
        if "order" not in session:
            session["order"] = []
            session["order_total"] = 0
        return render_template('index.html')

    return app
