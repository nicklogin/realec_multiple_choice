import json
import re

#verb_forms_marked - a dictionary with:
# - a bare_inf form
# - a gerund
# - a 3SG form
# - a 2nd form
# - a 3rd form
#задача программы - создать словарь со всеми синтетическими формами глагола

def prepare_dictionary():
    with open ('./nug_needs/wordforms.json', 'r', encoding = 'utf-8') as formlist:
        all_forms = json.load(formlist)
    return all_forms

def prepare_irregular_verbs():
    irregular_forms = dict()
    with open ('irregulars.txt', 'r', encoding = 'utf-8') as irrlist:
        irrlines = [i.split('|') for i in irrlist.readlines() if '|' in i]
    for line in irrlines:
        #print(line)
        sec = line[1]
        if '&' in sec:
            sec = sec.split('&')
            sec = sec[len(sec)-1]
        trd = line[2]
        if '&' in trd:
            trd = trd.split('&')
            trd = trd[len(trd)-1]
        irregular_forms[line[1]] = [sec, trd]
    return irregular_forms

def get_another_one(a,arr):
    if a == arr[0]:
        return arr[1]
    else:
        return arr[0]

def get_last_coincide(a,b):
    coincide_nmb = 0
    for sym_nmb in range(len(a)):
        if sym_nmb == len(b):
            break
        
        if a[sym_nmb] == b[sym_nmb]:
            coincide_nmb += 1
        else:
            break
    return coincide_nmb

def find_verb_forms(w):
    all_forms = prepare_dictionary()
    irregular_forms = prepare_irregular_verbs()
    be_forms = {'bare_inf':'be', '2nd':'was', '2ndPL':'were', '3rd':'been', 'gerund':'being', '1SG':'am', '1PL2SG2PL3PL':'are', '3SG':'is', 'Future':'will', 'Future-in-past':'would'}
    have_forms = {'bare_inf':'have', '2nd':'had', '3rd':'had', '3SG':'has', 'gerund':'having'}
    for key, val in be_forms.items():
        if w == val:
            return be_forms

    for key,val in have_forms.items():
        if w == val:
            return have_forms
    values = [all_forms[i] for i in all_forms]
    values = [j for i in values for j in i]
    if (w in all_forms) or (w in values):
        if w in all_forms:
            word = w
        elif w in values:
            for i in all_forms:
                if  w in all_forms[i]:
                    word = i
                    break
        verb_forms_marked_list = []
        #небольшой велосипед, чтобы
        stem_number = 0
        stem_numbers_list = dict()
        #не делать словарь словарей
        verb_forms = dict()
        stems = set()
        model = r'(\w{2,})(ing|s)'
        for form in all_forms[word]:
            verb_forms_marked = dict()
            match = re.match(model,form)
            if match and match.group(0) == form:
                stem = match.group(1)
                if not stem.endswith('ee'):
                    stem = stem.rstrip('e')
                #print(stem)
                if (stem not in stems) and not(len(stem)>2 and stem.endswith('ly')):
                    forms_completed = list(all_forms[word])
                    forms_completed.append(word)
                    two_first_forms = ['3SG','gerund'] 
                    if match.group(2) == 'ing':
                        if stem.endswith('y'):
                            another_form_variants = {'3SG':[stem[:len(stem)-1]+'ies',stem+'s']}
                        else:
                            another_form_variants = {'3SG':[stem+'s', stem+'es']}
                    else:
                        if stem.endswith('i'):
                            another_form_variants = {'gerund':[stem[:len(stem)-1]+'ying']}
                        else:
                            another_form_variants = {'gerund':[stem+stem[len(stem)-1]+'ing', stem+'ing']}
                    for key, variants in another_form_variants.items():
                        for variant in variants:
                            if variant in forms_completed:
                                verb_forms[stem] = [match.group(0),variant]
                                verb_forms_marked[key] = variant
                                verb_forms_marked[get_another_one(key,two_first_forms)] = match.group(0)
                                stems.add(stem)
                                bare_inf_form_variants = [stem,stem+'e',stem[:len(stem)-1]+'y',stem[:len(stem)-1]+'ie']
                                past_form_variants = [stem+stem[len(stem)-1]+'ed',stem[:len(stem)-1]+'ied',stem+'ed',stem+'d']
                                for i in bare_inf_form_variants:
                                    if i in forms_completed:
                                        verb_forms[stem].append(i)
                                        verb_forms_marked['bare_inf'] =  i
                                        #verb_forms_marked['1PL2SG2PL3PL'] = i
                                        #verb_forms_marked['1SG'] = i
                                        break
                                for i in past_form_variants:
                                    #print(i)
                                    if i in forms_completed:
                                        verb_forms[stem].append(i)
                                        verb_forms_marked['2nd'] = i
                                        verb_forms_marked['3rd'] = i
                                        break
                    
                    if ('bare_inf' in verb_forms_marked) and (verb_forms_marked['bare_inf'] in irregular_forms):
                        verb_forms_marked['2nd'] = irregular_forms[ verb_forms_marked['bare_inf'] ][0]
                        verb_forms_marked['3rd'] = irregular_forms[ verb_forms_marked['bare_inf'] ][1]
                        
                    stem_numbers_list[stem] = stem_number
                    stem_number += 1
                    verb_forms_marked_list.append(verb_forms_marked)
        #print(stems)
        last_coincide = 0
        for st in stems:
            new_coincide = get_last_coincide(w, st)
            if new_coincide >= last_coincide:
                last_coincide = new_coincide
                v_forms = verb_forms[st]
                outstem = st
                st_nmb = stem_numbers_list[st]
                verb_forms_marked = verb_forms_marked_list[st_nmb]

        #print(outstem)
        #print(v_forms)
        try:
            if w in [val for key,val in verb_forms_marked.items()]:
                return verb_forms_marked
            else:
               empty_dict = dict()
               return empty_dict
        except:
            empty_dict = dict()
            return empty_dict
    
    else:
        empty_dict = dict()
        return empty_dict

def makeSN(form):
    if form == 'can':
        return form+"'t"
    else:
        return form+"n't"

##returns a negation of verb phrase
def neg(verb_phrase):
    if ("n't" in verb_phrase) or ("not" in verb_phrase):
        return verb_phrsae
    dSN = 'must','should','is','was','were','are','can','could','should','would'
    left_context = ''
    head_verb_forms = False
    verb_phrase = verb_phrase.split(' ')
    for i in range(len(verb_phrase)):
        if find_verb_forms(verb_phrase[i]):
            head_verb = verb_phrase[i]
            break
        else:
            left_context += verb_phrase[i]
            left_context += ' '
    have_forms = find_verb_forms('have')
    right_context =' '.join(verb_phrase[i+1:])
##    print(right_context)
    head_verb_forms = find_verb_forms(head_verb)
    if (head_verb in dSN) or ((head_verb in tuple(have_forms[i] for i in have_forms)) and (right_context != '')):
        output = makeSN(head_verb) + ' ' + right_context
    elif head_verb == 'am':
        output = head_verb + ' not ' + right_context
    elif head_verb_forms:
        bare_inf_phrase = ' ' + head_verb_forms['bare_inf'] + ' ' + right_context
        if head_verb == head_verb_forms['2nd']:
            output = "didn't" + bare_inf_phrase
        elif head_verb == head_verb_forms['3SG']:
            output = "doesn't" + bare_inf_phrase
        elif head_verb == head_verb_forms['bare_inf']:
            output = "don't" + bare_inf_phrase
    else:
        output += 'not ' + str(' '.join(verb_phrase))
    return left_context+output


def pos(neg_verb_phrase):
    if neg_verb_phrase.count(' ')>0:
        neg_verb_phrase = neg_verb_phrase.split(' ')
        for i in range(len(neg_verb_phrase)):
            if neg_verb_phrase[i].endswith("n't"):
                neg_verb_phrase[i] = neg_verb_phrase[i][:neg_verb_phrase[i].find("n't")]
                if neg_verb_phrase[i] == 'did':
                    neg_verb_phrase[i+1] = find_verb_forms(neg_verb_phrase[i+1])['2nd']
                    neg_verb_phrase.pop(i)
                elif neg_verb_phrase[i] == 'does':
                    neg_verb_phrase[i+1] = find_verb_forms(neg_verb_phrase[i+1])['3SG']
                    neg_verb_phrase.pop(i)
                elif neg_verb_phrase[i] == 'do':
                    neg_verb_phrase[i+1] = find_verb_forms(neg_verb_phrase[i+1])['bare_inf']
                    neg_verb_phrase.pop(i)
                break
            if neg_verb_phrase[i] == 'not':
                if i>0:
                    if neg_verb_phrase[i-1] == 'did':
                        if i<len(neg_verb_phrase)-1:
                            neg_verb_phrase[i+1] = find_verb_forms(neg_verb_phrase[i+1])['2nd']
                        neg_verb_phrase.pop(i-1)
                    elif neg_verb_phrase[i-1] == 'does':
                        if i<len(neg_verb_phrase)-1:
                            neg_verb_phrase[i+1] = find_verb_forms(neg_verb_phrase[i+1])['2nd']
                        neg_verb_phrase.pop(i-1)
                    elif neg_verb_phrase[i-1] == 'do':
                        if i<len(neg_verb_phrase)-1:
                            neg_verb_phrase[i+1] = find_verb_forms(neg_verb_phrase[i+1])['2nd']
                        neg_verb_phrase.pop(i-1)
                neg_verb_phrase.pop(i)
                break
        neg_verb_phrase = ' '.join(neg_verb_phrase)
    else:
        if neg_verb_phrase.endswith("n't"):
            neg_verb_phrase = neg_verb_phrase[:neg_verb_phrase.find("n't")]
    return neg_verb_phrase
    

##while True:
##    print(find_verb_forms(input()))

##while True:
##    print(neg(input()))

##while True:
##    print(pos(input()))

        
    
