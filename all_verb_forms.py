import re
import json
#VB - INF
#VBD - PAST
#VBG - PROG
#VBN - PPART
#VBP - PRES1sg
#VBZ - PRES3sg

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
    be_forms = {'INF':'be', 'PAST':'was', 'PAST2sg':'were', 'PPART':'been', 'PROG':'being', 'PRES1sg':'am', 'PRES2sg':'are', 'PRES3sg':'is'}
    have_forms = {'INF':'have', 'PAST':'had', 'PPART':'had', 'PRES1sg':'have', 'PRES3sg':'has', 'PROG':'having'}
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
                    two_first_forms = ['PRES3sg','PROG'] 
                    if match.group(2) == 'ing':
                        if stem.endswith('y'):
                            another_form_variants = {'PRES3sg':[stem[:len(stem)-1]+'ies',stem+'s']}
                        else:
                            another_form_variants = {'PRES3sg':[stem+'s', stem+'es']}
                    else:
                        if stem.endswith('i'):
                            another_form_variants = {'PROG':[stem[:len(stem)-1]+'ying']}
                        else:
                            another_form_variants = {'PROG':[stem+stem[len(stem)-1]+'ing', stem+'ing']}
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
                                        verb_forms_marked['INF'] =  i
                                        #verb_forms_marked['1PL2sg2PL3PL'] = i
                                        #verb_forms_marked['PRES1sg'] = i
                                        break
                                for i in past_form_variants:
                                    #print(i)
                                    if i in forms_completed:
                                        verb_forms[stem].append(i)
                                        verb_forms_marked['PAST'] = i
                                        verb_forms_marked['PPART'] = i
                                        break
                    
                    if ('INF' in verb_forms_marked) and (verb_forms_marked['INF'] in irregular_forms):
                        verb_forms_marked['PAST'] = irregular_forms[ verb_forms_marked['INF'] ][0]
                        verb_forms_marked['PPART'] = irregular_forms[ verb_forms_marked['INF'] ][1]
                        
                    stem_numbers_list[stem] = stem_number
                    stem_number += 1
                    #verb_forms_marked['PRES1sg'] = verb_forms_marked['PRES3sg']
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
                verb_forms_marked['PRES1sg'] = verb_forms_marked['INF']
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

def continuise(form):
    form = form.split(' ')
    form[0] = getsynthforms(form[0])['PROG']
    form = 'be ' + ' '.join(form)
    return form

def perfectise(form):
    form = form.split(' ')
    form[0] = getsynthforms(form[0])['PPART']
    form = 'have ' + ' '.join(form)
    return form    

def make_future(form):
    return 'will '+form

def make_past(form):
    form = form.split(' ')
    if form[0] == 'have':
        form[0] = 'had'
    else:
        form[0] = getsynthforms(form[0])['PAST']
    form = ' '.join(form)
    return form
    
def make_fut_in_past(form):
    return 'would '+form

def make_1sg(form):
    form = form.split(' ')
    form[0] = getsynthforms(form[0])['PRES1sg']
    form = ' '.join(form)
    return form

def make_2sg(form):
    form = form.split(' ')
    if form[0] == 'be':
        form[0] = 'are'
    elif form[0] == 'was':
        form[0] = 'were'
    form = ' '.join(form)
    return form


def make_3sg(form):
    form = form.split(' ')
    form[0] = getsynthforms(form[0])['PRES3sg']
    form = ' '.join(form)
    return form

def getform(verbdict,voice,cont,perf,tense,persnmb):
    form = ''
    if voice == 'Active':
        form = verbdict['INF']
    elif (verbdict==be_forms) or (verbdict==have_forms):
        return ''
    else:
        form = 'be ' + verbdict['PPART']
    if cont == 'Simple':
        form  = form
    else:
        form = continuise(form)
    if perf == 'Perfect':
        form = perfectise(form)
    else:
        form = form
    if tense == 'Future':
        form = make_future(form)
    elif tense == 'Past':
        form = make_past(form)
    elif tense == 'Future_in_the_past':
        form = make_fut_in_past(form)
    if persnmb == '2sg':
        if form.split(' ')[0] in ('be','was'):
            form = make_2sg(form)
        else:
            form = ''
    elif persnmb == '1sg' and tense == 'Present':
        form = make_1sg(form)
    elif persnmb == '3sg' and tense == 'Present':
        form = make_3sg(form)
    return form
    
    
def get_allforms(verbdict):
    #oppositions:
    #Active-Passive
    #Simple-Continuous
    #Perfect-Non_perfect
    #Future-Present-Past-Future_in_the_past
    #1sg-2sg-3sg
    if not verbdict:
        return {}
    allforms = dict()
    for voice in ('Active','Passive'):
        for cont in ('Simple','Continuous'):
            for perf in ['Perfect','Non_perfect']:
                for tense in ('Future','Present','Past','Future_in_the_past'):
                    for persnmb in ('1sg','2sg','3sg'):
                        allforms[' '.join([voice,tense,perf,cont,persnmb])] = getform(verbdict,voice,cont,perf,tense,persnmb)
                        #print(' '.join([voice,cont,perf,tense,persnmb]),allforms[' '.join([voice,cont,perf,tense,persnmb])])
    keys = [i for i in allforms.keys()]
    for k in keys:
        if allforms[k] == '':
            allforms.pop(k)
    return allforms
                     
def getsynthforms(verb):
    verbdict = dict()
    if verb in [val for key,val in have_forms.items()]:
        verbdict = have_forms
    elif verb in [val for key,val in be_forms.items()]:
        verbdict = be_forms
    else:
        verbdict = find_verb_forms(verb)
    return verbdict
    

have_forms = find_verb_forms('have')
be_forms = find_verb_forms('be')
print(get_allforms(getsynthforms(input())))
