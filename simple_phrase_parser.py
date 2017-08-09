##this is a very simple
##ad-hoc parser for exercize-creating needs
import verb_forms_finder as vff

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

def find_verb_form(phrase, formname):
    phrase = phrase.split(' ')
    form = ''
    ##в этом случае возвращаем последнюю аналитическую форму в составе
    ##первой встреченной синтетической
    if formname == 'any':
        be_forms = [val for key,val in vff.find_verb_forms('be').items()]
        form_start = False
        form_end = False
        prev_token = ''
        for token in phrase:
            verb_forms = vff.find_verb_forms(token)
            if verb_forms:
                form_start = True
                form_end = False
                if (token == verb_forms['3rd']) and (prev_token in be_forms):
                    prev_token += ' '+token
                else:
                    prev_token = token
            else:
                form_end = True
            if form_start and form_end:
                break
        
        return str(prev_token)

    ##в этом случае находим первую попавшуюся аналитическую форму заданного
    ##характера и возвращаем её.
    else:
        for token in phrase:
            verb_forms = vff.find_verb_forms(token)
            if formname in verb_forms.keys():
                if verb_forms[formname] == token:
                    form = token
                    break
        return form

##следует добавить:
##отрицательные формы
##инверсию (why would i talk to her?)
def find_synth_form(phrase, anal_form):
    phrase = phrase.split(' ')
    be_forms = [val for key,val in vff.find_verb_forms('be').items()]
    have_forms =[val for key,val in vff.find_verb_forms('have').items()]
    form = ''
    for token in phrase:
        if token == anal_form:
            form += ' '+token
            break
        elif (vff.pos(token) in be_forms) or (vff.pos(token) in have_forms):
            form += ' '+token
        elif token != 'not':
            form = ''
    form = form.strip(' ')
    return form   

##while True:
##    print(find_verb_form(input(), 'any'))

##while True:
##    print(find_verb_form(input(), 'gerund'))

##while True:
##    print(find_prep(input()))

##while True:
##    print(find_synth_form(input(), 'playing'))
