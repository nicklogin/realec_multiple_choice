import simple_phrase_parser as spp
import verb_forms_finder as vff

##нужно добавить возможность работать
##с пассивным залогом
##реализация пункта 7:
def task7(right):
    choices = [right]
    lex_verb = spp.find_verb_form(right[right.find('would'):],'any')
    lex_verb_forms = vff.find_verb_forms(lex_verb)
    if lex_verb and lex_verb_forms:
        new_choices = [lex_verb_forms['2nd'], 'would have '+lex_verb_forms['3rd'],'would '+lex_verb_forms['bare_inf']]
        [choices.append(i) for i in new_choices if i!=right]
    return choices[:4]

##реализация пункта 1:
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

while True:
    print(task1(input()))
