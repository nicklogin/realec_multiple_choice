import simple_phrase_parser as spp
import verb_forms_finder as vff

##нужно добавить возможность работать
##с пассивным залогом
##реализация пункта 7:
##elif self.error_type == 'Defining':
def task7(right):
    choices = [right]
    lex_verb = spp.find_verb_form(right[right.find('would'):],'any')
    if lex_verb.count(' ') == 0:
        lex_verb_forms = vff.find_verb_forms(lex_verb)
        if lex_verb_forms:
            new_choices = [lex_verb_forms['2nd'], 'would have '+lex_verb_forms['3rd'],'would '+lex_verb_forms['bare_inf']]
            [choices.append(i) for i in new_choices if i!=right]
    else:
        be_form, verb_form = lex_verb.split(' ')
        if (be_form == 'are') or (be_form == 'were'):
            choices.append('were '+verb_form)
        else:
            choices.append('was '+verb_form)
        choices.append('would have been '+verb_form)
        choices.append('would be '+verb_form)
    return choices[:4]

##реализация пункта 1:
##elif ((self.error_type == 'Choice_in_cond') or (self.error_type == 'Form_in_cond')) and ('would' in right):
def task1(right):
    choices = [right]
    gerund_form = spp.find_verb_form(right,'gerund')
    add_forms = vff.find_verb_forms(gerund_form)
    if gerund_form:
        choices.append(right.replace(gerund_form, 'being ' + add_forms['3rd'], 1))
        continuous_form = spp.find_synth_form(right,gerund_form)
        choices.append(right.replace(continuous_form, add_forms['2nd'], 1))
    return choices[:3]


##while True:
##    print(task7(input()))

##while True:
##    print(task1(input()))
