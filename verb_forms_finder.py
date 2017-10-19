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
        sec = line[2]
        if '&' in sec:
            sec = sec.split('&')
            sec = sec[len(sec)-1]
        trd = line[3]
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

def neg(verb_form):
    try:
        dSN = 'must','should','is','was','were','are','can','could','should','would'
        verb_form = verb_form.split(' ')
        head_verb = verb_form[0]
        have_forms = find_verb_forms('have')
        try:
            other_verbs = ' '.join(verb_form[1:])
        except:
            other_verbs = ''
    ##    print(other_verbs)
        head_verb_forms = find_verb_forms(head_verb)
        if (head_verb in dSN) or ((head_verb in tuple(have_forms[i] for i in have_forms)) and (other_verbs != '')):
            return makeSN(head_verb) + ' ' + other_verbs
        elif head_verb == 'am':
            return head_verb + ' not ' + other_verbs
        elif head_verb_forms:
            bare_inf_phrase = ' ' + head_verb_forms['bare_inf'] + ' ' + other_verbs
            if head_verb == head_verb_forms['2nd']:
                return "didn't" + bare_inf_phrase
            elif head_verb == head_verb_forms['3SG']:
                return "doesn't" + bare_inf_phrase
            elif head_verb == head_verb_forms['bare_inf']:
                return "don't" + bare_inf_phrase
        else:
            return 'not ' + str(' '.join(verb_form))
    except:
        return ''

def pos(neg_verb_form):
    if neg_verb_form.count(' ')>0:
        if 'not' in neg_verb_form:
            return neg_verb_form.replace('not','',1)
        else:
            neg_verb_form = neg_verb_form.split(' ')
            if neg_verb_form[0].endswith("n't"):
                neg_verb_form[0] = neg_verb_form[0][:neg_verb_form[0].find("n't")]
                if neg_verb_form[0] == 'do' and find_verb_forms(neg_verb_form[1]):
                    neg_verb_form = neg_verb_form[1:]
            neg_verb_form = str(' '.join(neg_verb_form))
    else:
        if neg_verb_form.endswith("n't"):
            neg_verb_form = neg_verb_form[:neg_verb_form.find("n't")]
    return neg_verb_form
    

##while True:
##    print(find_verb_forms(input()))

##while True:
##    print(neg(input()))

##while True:
##    print(pos(input()))

        
    
