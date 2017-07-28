##this is a very simple
##ad-hoc parser for exercize-creating needs

def find_prep(phrase):
    found_prep = False
    with open ('prepositions.txt', 'r', encoding = 'utf-8') as p:
        prep_list = [i.strip('\n') for i in p.readlines()]
    phrase = phrase.split(' ')
    for i in phrase:
        if i.lower() in prep_list:
            return i

def word_replace(phrase, word1, word2):
    phrase = phrase.split(' ')
    new_phrase = []
    for word in phrase:
        if word == word1:
            new_phrase.append(word2)
        else:
            new_phrase.append(word)

    return ' '.join(new_phrase)

##while True:
##    print(find_prep(input()))

##while True:
##    phrase, word1, word2 = input().split(';')
##    print(word_replace(phrase, word1, word2))
