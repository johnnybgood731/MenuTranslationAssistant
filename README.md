# Readme

## Restaurant Ordering Chatbot

Welcome to our Restaurant Ordering Chatbot! This chatbot is designed to help users take restaurant orders in English or Chinese.
### Getting Started

To get started, you will need to install the following python libraries:

- `pandas`
- `spacy`
- `transformers`
- `flask`
- `pattern`
- `SpeechRecognition`
- `gTTS`
- `PlaySound`
- `math`
- `os`

Downloading pattern requires an existing MySQL config file. 

You will also need to download the required spacy language model, `en_core_web_md`, using the command:

`python -m spacy download en_core_web_md`

To run the chatbot, navigate to the main project directory
and enter the following command:

`flask --app flask-webapp run`

## Using the Chatbot

To use the chatbot, simply type your message into the input field and press send. The chatbot will respond with suggestions for menu items and assist you with placing your order.

## Language Support

The chatbot is able to understand and respond to orders in both English and Chinese. Simply enter your order in the desired language and the chatbot will respond appropriately.

We hope you enjoy using our Restaurant Ordering Chatbot!
