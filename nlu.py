# noinspection PyUnresolvedReferences
from pattern.en import number
from math import ceil

THRESHOLD = 0.6


def identifyAction(nlp, token):
    # Identify the action based on the given token as either "add", "replace", "remove", "query", "complete", or "none"
    actions = [["order", "add", "take", "purchase", "buy", "get", "have"],
               ["replace", "substitute"],
               ["remove", "leave", "subtract", "cancel", "delete"],
               ["query", "search", "list", "find", "show", "look"],
               ["finish", "exit", "complete", "checkout", "done", "nothing", "review"]]
    function = "none"
    maxScore = THRESHOLD
    for i, group in enumerate(actions):
        for action in group:
            similarity = nlp(token).similarity(nlp(action))
            if similarity > maxScore:
                maxScore = similarity
                if i == 0:
                    function = "add"
                elif i == 1:
                    function = "replace"
                elif i == 2:
                    function = "remove"
                elif i == 3:
                    function = "query"
                elif i == 4:
                    function = "complete"

    return function, maxScore


def fillAction(slots, tokens, nlp):
    # Identify the action verb in the request using POS tagging
    maxScore = 0
    reqAction = "none"
    for token in tokens:
        if token["entity"] == 'VERB' and token["score"] > maxScore:
            maxScore = token["score"]
            reqAction = token["word"]

    # Identify the action being requested as either "add", "replace", "remove", "query", "complete", or "none"
    function, maxScore = identifyAction(nlp, reqAction)
    if not function == "none" or slots[0] == "none":
        slots[0] = function

    # If no action verb is present, check for non-verb matches
    maxScore = THRESHOLD
    if slots[0] == "none":
        for token in tokens:
            function, score = identifyAction(nlp, token["word"])
            if score > maxScore:
                maxScore = score
                slots[0] = function
    return slots


def fillItem(slots, nlp, menuItems, response):
    # Identify all phrases that closely match a menu item
    matches = []
    doc = nlp(response)
    doc = nlp(' '.join([str(token.lemma_) for token in doc if not token.is_stop and not token.is_punct]))
    for n in range(1, len(doc) + 1):
        for i in range(len(doc) + 1 - n):
            phrase = ""
            for j in range(n):
                phrase += str(doc[i + j])
                if j < n - 1:
                    phrase += " "
            for item in menuItems:
                similarity = nlp(item[2].lower()).similarity(nlp(phrase))
                if similarity > THRESHOLD:
                    matches += [[item[0], similarity, i, i + n]]
                if item[1] == phrase:
                    matches += [[item[0], 1, i, i + n]]

    # Remove all phrases that overlap with a phrase with a higher similarity score
    bestMatches = []
    while len(matches) > 0:
        maxScore = 0
        bestMatch = 0
        for i, match in enumerate(matches):
            if match[1] > maxScore:
                maxScore = match[1]
                bestMatch = i
        bestMatches += [matches[bestMatch]]
        needsRemoved = []
        for match in matches:
            if not (match[3] <= matches[bestMatch][2] or matches[bestMatch][3] <= match[2]):
                needsRemoved += [match]
        for i in range(len(needsRemoved)):
            matches.remove(needsRemoved[i])

    # Identify the quantity for each of the best matches using a dependency parser
    entities = doc.ents
    quantities = []
    # Find the entities which are numbers greater than 0
    for entity in entities:
        if entity.label_ == "CARDINAL" and number(str(entity)) > 0:
            quantities += [[entity, entity.start, entity.end, -1]]
    # Find the dependency head of each number
    for quantity in quantities:
        for i in range(quantity[1], quantity[2]):
            for j in range(len(doc)):
                if doc[i].head == doc[j] and (j < quantity[1] or j >= quantity[2]):
                    quantity[3] = j
                    break
    # For each menu item, find the number that shares a common ancestor, or default to 1 if no common ancestors
    for match in bestMatches:
        quant = 1
        flag = False
        for quantity in quantities:
            for i in range(match[2], match[3]):
                head = doc[i]
                while True:
                    if doc[quantity[3]] == head:
                        quant = ceil(number(str(quantity[0])))
                        flag = True
                        break
                    if head.head == head:
                        break
                    head = head.head
                if flag:
                    break
            if flag:
                break
        # Fill a slot by adding the menu items and corresponding quantities one at a time
        slots[1] += [match[0]]
        slots[2] += [quant]
    # If any orders are drinks, assign the first one to the drink slot
    for i, item in enumerate(slots[1]):
        if menuItems[item - 1][1][0] == "D":
            slots[4] = item
            if slots[2][i] > 1:
                slots[2][i] -= 1
            else:
                slots[1].pop(i)
                slots[2].pop(i)
            break
    return slots
