import simple_phrase_parser as spp
import verb_forms_finder as vff

##нужно добавить возможность работать
##с пассивным залогом
##реализация пункта 7:
##elif ((self.error_type == 'Choice_in_cond') or (self.error_type == 'Form_in_cond')) and ('would' in right):
def task7(right):
    choices = [right]
    if "wouldn't" in right:
        neg = True
    elif 'would' in right:
        neg = False
    lex_verb = spp.find_verb_form(right[right.find('would'):],'any')
    print(lex_verb)
    if lex_verb.count(' ') == 0:
        lex_verb_forms = vff.find_verb_forms(lex_verb)
        if lex_verb_forms:
            new_choices = set([lex_verb_forms['2nd'], 'would have '+lex_verb_forms['3rd'],'would '+lex_verb_forms['bare_inf']])
    else:
        be_form, verb_form = lex_verb.split(' ')
        new_choices = set()
        if (be_form == 'are') or (be_form == 'were'):
            new_choices.add('were '+verb_form)
        else:
            new_choices.add('was '+verb_form)
        new_choices.add('would have been '+verb_form)
        new_choices.add('would be '+verb_form)
    if neg:
        new_choices = [vff.neg(i) for i in new_choices]
        print(new_choices)
    [choices.append(i) for i in new_choices if i!=right]
    return choices[:4]

##реализация пункта 1:
##elif self.error_type == 'Defining':
def task1(right):
    choices = [right]
    gerund_form = spp.find_verb_form(right,'gerund')
    add_forms = vff.find_verb_forms(gerund_form)
    new_choices = []
    if gerund_form:
        continuous_form = spp.find_synth_form(right,gerund_form)
        new_choices.append(right.replace(gerund_form, 'being ' + add_forms['3rd'], 1))
        new_choices.append(right.replace(continuous_form, add_forms['2nd'], 1))
        if ("n't" in continuous_form) or ('not' in continuous_form):
            new_choices = [vff.neg(i) for i in new_choices]
    [choices.append(i) for i in new_choices if i!=right]
    return choices[:3]


##while True:
##    print(task7(input()))

##while True:
##    print(task1(input()))
