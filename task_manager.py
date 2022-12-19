from nlu import *
from speech_text import *
from machine_translation import translate


def assist(slots, orders, menuItems, nlp, classifier, language, data):
    # Ask for user request
    message = ""
    request = ""
    # If nothing has been successfully requested so far
    if language == "":
        message = "How can I be of assistance?"
        text_to_speech(message, 'en')
        message = translate("我可以帮你吗", "zh-cn")
    # If something is on the order already, but nothing additional has been successfully requested so far
    elif slots == ["none", [], [], "", 0]:
        message = translate("How else can I help?", language)
    # If only a drink has been requested, but no action associated with it
    elif slots[0] == "none" and slots[1] == [] and slots[4] > 0:
        for order in orders:
            if order[0] == slots[4]:
                message = translate("Are you adding or removing " + str(menuItems[order[0] - 1][2]) +
                                    " from your order?", language)
                break
            else:
                slots[0] = "add"
    # If a dish has been requested, but no action associated with it
    elif slots[0] == "none":
        for dish in slots[1]:
            flag = True
            for order in orders:
                for item in order[0]:
                    if item == dish:
                        flag = False
                        break
                if not flag:
                    break
            if flag:
                slots[0] = "add"
                break
        if slots[0] == "none" and len(slots[1]) == 1:
            message = translate("Are you adding or removing " + str(menuItems[slots[1][0] - 1][2]) +
                                " from your order?", language)
        elif slots[0] == "none":
            message = translate("Are you adding or removing the items from your order?", language)
    # If an action of "add" or "delete" is requested, but with no menu item associated with it
    elif (slots[0] == "add" or slots[0] == "remove") and slots[1] == [] and slots[4] == 0:
        if slots[0] == "add":
            message = translate("What do you want to add to your order?", language)
        else:
            message = translate("What do you want to remove from your order?", language)
    # If an action of "add" is requested along with a menu item, but there is no spicy level specified
    elif slots[0] == "add" and len(slots[1]) > 0 and slots[3] == "":
        choices = [["none", "nothing", "mild", "not", "tame", "minimum"],
                   ["medium", "middle", "mediocre"],
                   ["spicy", "hot", "intense", "burn", "maximum"]]
        while True:
            text_to_speech(translate("How spicy do you want it?", language), language)
            language, request = speech_to_text(language)
            request = translate(request, "en")
            tokens = classifier(request)
            spice = ""
            maxScore = 0.3
            for token in tokens:
                for i, group in enumerate(choices):
                    for choice in group:
                        similarity = nlp(token["word"]).similarity(nlp(choice))
                        if similarity > maxScore:
                            maxScore = similarity
                            if i == 0:
                                spice = "mild"
                            elif i == 1:
                                spice = "medium"
                            elif i == 2:
                                spice = "spicy"
            if spice == "mild" or spice == "medium" or spice == "spicy":
                slots[3] = spice
                request = ""
                break
            else:
                text_to_speech(translate("Sorry, I didn't understand that. How spicy do you want your food?", language),language)
    # If an action of "add" is requested along with a menu item, but there is no drink specified
    elif slots[0] == "add" and len(slots[1]) > 0 and slots[4] == 0:
        text_to_speech(translate("Do you want something to drink?", language), language)
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
                message = translate("What do you want to drink?", language)
                break
            elif answer == "no":
                slots[4] = -1
                request = ""
                break
            else:
                text_to_speech(translate("Sorry, I don't understand that response. "
                                         "What do you want to drink?", language), language)
                language, response = speech_to_text(language)
                response = translate(response, "en")

    # If the system needs to ask the user a question
    if not message == "":
        print(message)
        if language == "":
            text_to_speech(message, 'zh-cn')
        else:
            text_to_speech(message, language)
        language, request = speech_to_text(language)
        # If the preferred language is Chinese, parse data.csv to see if any direct translations are available
        if language == "zh-cn":
            i = -1
            j = -1
            for k, datum in enumerate(data):
                i = request.find(str(datum[1]))
                if i >= 0:
                    j = k
                    break
            if j >= 0:
                newRequest = ""
                for k in range(len(request)):
                    if k == i:
                        newRequest += data[j][2]
                        k += len(data[j][1])
                        if k >= len(request):
                            break
                    newRequest += request[k]
                request = newRequest
        request = translate(request, "en")
        print(request)

    # If the system needs to process an answer given by the user
    if not request == "":
        # Fill or update slots
        tokens = classifier(request)
        slots = fillAction(slots, tokens, nlp)
        if slots[0] == "none" or slots[0] == "add" or slots[0] == "remove":
            slots = fillItem(slots, nlp, menuItems, request)

    return request, slots, language
