import sys, codecs, re, os, traceback
from collections import defaultdict, OrderedDict
import shutil
import random
import json
import pprint
import difflib
import verb_forms_finder as vff
import simple_phrase_parser as spp
import nltk.tag.stanford as stag

def ind(array, value):
    for i in range(len(array)):
        if array[i] == value:
            return i
    return len(array)+1
"""Script that generates grammar exercises from REALEC data 
grammar tags:
	Punctuation
	Spelling
	Capitalisation
	Grammar
		Determiners
			Articles
				Art_choice
				Art_form
			Det_choice
			Det_form
		Quantifiers
			Quant_choice
			Quant_form
		Verbs
			Tense
				Tense_choice
					Seq_of_tenses
					Choice_in_cond
				Tense_form
					Neg_form
					Form_in_cond
			Voice
				Voice_choice
				Voice_form
			Modals
				Modals_choice
				Modals_form
			Verb_pattern
				Intransitive
				Transitive
					Reflexive_verb
					Presentation
				Ambitransitive
				Two_in_a_row
					Verb_Inf
						Verb_object_inf
						Verb_if
					Verb_Gerund
						Verb_prep_Gerund
							Verb_obj_prep_Gerund
					Verb_Inf_Gerund
						No_diff
						Diff
					Verb_Bare_Inf
						Verb_object_bare
						Restoration_alter
					Verb_part
						Get_part
					Complex_obj
					Verbal_idiom
				Prepositional_verb
					Trans_phrasal
					Trans_prep
					Double_object
					Double_prep_phrasal
				Dative
				Followed_by_a_clause
					that_clause
					if_whether_clause
					that_subj_clause
					it_conj_clause
			Participial_constr
			Infinitive_constr
			Gerund_phrase
			Verb_adj
			Verb_adv
		Nouns
			Countable_uncountable
			Prepositional_noun
			Possessive
			Noun_attribute
			Noun_inf
			Noun_number
				Collective
					Adj_as_collective
		Prepositions
		Conjunctions
			And_syn
			Contrast
			Concession
			Causation
		Adjectives
			Comparative_adj
			Superlative_adj
			Prepositional_adjective
			Adjective_inf
			Adjective_ger
		Adverbs
			Comparative_adv
			Superlative_adv
			Prepositional_adv
			Modifier
		Numerals
			Num_choice
			Num_form
		Pronouns
			Personal
			Reflexive
			Demonstrative
		Agreement_errors
			Animacy
			Number
			Person
		Word_order
			Standard
			Emphatic
			Cleft
			Interrogative
		Abs_comp_clause
			Exclamation
			Title_structure
			Note_structure
		Conditionals
			Cond_choice
			Cond_form
		Attributes
			Relative_clause
				Defining
				Non_defining
				Coordinate
			Attr_participial
		Lack_par_constr
		Negation
		Comparative_constr
			Numerical
		Confusion_of_structures
	Vocabulary
		Word_choice
			lex_item_choice
				Often_confused
			Choice_synonyms
			lex_part_choice
				Absence_comp_colloc
				Redundant
		Derivation
			Conversion
			Formational_affixes
				Suffix
				Prefix
			Category_confusion
			Compound_word
	Discourse
		Ref_device
			Lack_of_ref_device
			Dangling_ref
			Redundant_ref
			Choice_of_ref
		Coherence
			Incoherent_articles
			Incoherent_tenses
				Incoherent_in_cond
			Incoherent_pron
			Linking_device
				Incoherent_conj
				Incoherent_intro_unit
				Lack_of_connective
		Inappropriate_register
		Absence_comp_sent
		Redundant_comp
		Tautology
		Absence_explanation
"""

class Exercise:
    def __init__(self, path_to_realecdata, error_type, exercise_types, bold, context):

        """"
        :param error_type: 'Tense_choice', 'Tense_form', 'Voice_choice', 'Voice_form', 'Number
        :param exercise_types: list, any from: multiple_choice, word_form, short_answer, open_cloze
        """
        self.path_new = './processed_texts/'
        self.path_old = path_to_realecdata
        self.error_type = error_type
        self.exercise_types = exercise_types
        self.current_doc_errors = OrderedDict()
        self.bold = bold
        self.context = context
        self.headword = ''
        self.write_func = {
            "short_answer": self.write_sh_answ_exercise,
            "multiple_choice": self.write_multiple_ch,
            "word_form": self.write_open_cloze,
            "open_cloze": self.write_open_cloze
        }
        self.tagger = stag.StanfordPOSTagger('english-caseless-left3words-distsim.tagger')
        os.makedirs('moodle_exercises', exist_ok=True)
        os.makedirs('processed_texts', exist_ok=True)
        with open('wordforms.json', 'r', encoding="utf-8") as dictionary:
            self.wf_dictionary = json.load(dictionary)  # {'headword':[words,words,words]}

    def find_errors_indoc(self, line):
        """
        Find all T... marks and save in dictionary.
        Format: {"T1":{'Error':err, 'Index':(index1, index2), "Wrong":text_mistake}}
        """
        if re.search('^T', line) is not None and 'pos_' not in line:
            try:
                t, span, text_mistake = line.strip().split('\t')
                err, index1, index2 = span.split()
                self.current_doc_errors[t] = {'Error':err, 'Index':(int(index1), int(index2)), "Wrong":text_mistake}
                return (int(index1), int(index2))
            except:
                #print (''.join(traceback.format_exception(*sys.exc_info())))
                print("Errors: Something wrong! No notes or a double span", line)

    def validate_answers(self, answer):
        # TO DO: multiple variants?
        if answer.upper() == answer:
            answer = answer.lower()
        answer = answer.strip('\'"')
        answer = re.sub(' ?\(.*?\) ?','',answer)
        if '/' in answer:
            answer = answer.split('/')[0]
        if '\\' in answer:
            answer = answer.split('\\')[0]
        if ' OR ' in answer:
            answer = answer.split(' OR ')[0]
        if ' или ' in answer:
            answer = answer.split(' или ')[0]
        if answer.strip('? ') == '' or '???' in answer:
            return None
        return answer

    def find_answers_indoc(self, line):
        if re.search('^#', line) is not None and 'lemma =' not in line:
            try:
                number, annotation, correction = line.strip().split('\t')
                t_error = annotation.split()[1]
                if self.current_doc_errors.get(t_error):
                    validated = self.validate_answers(correction)
                    if validated is not None:
                        self.current_doc_errors[annotation.split()[1]]['Right'] = validated
            except:
                #print (''.join(traceback.format_exception(*sys.exc_info())))
                print("Answers: Something wrong! No Notes probably", line)

    def find_delete_seqs(self, line):
        if re.search('^A', line) is not None and 'Delete' in line:
            t = line.strip().split('\t')[1].split()[1]
            if self.current_doc_errors.get(t):
                self.current_doc_errors[t]['Delete'] = 'True'

    def make_data_ready_4exercise(self):
        """ Collect errors info """
        anns = []
        for root, dire, files in os.walk(self.path_old):
            anns += [root+'/'+f for f in files if f.endswith('.ann')]
        i = 0
        for ann in anns:
            #print(ann)
            self.error_intersects = set()
            with open(ann, 'r', encoding='utf-8') as ann_file:
                for line in ann_file.readlines():
                    ind = self.find_errors_indoc(line)
                    self.find_answers_indoc(line)
                    self.find_delete_seqs(line)
                    
            new_errors = OrderedDict()
            for x in sorted(self.current_doc_errors.items(),key=lambda x: (x[1]['Index'][0],x[1]['Index'][1],int(x[0][1:]))):
                if 'Right' in x[1] or 'Delete' in x[1]:
                    new_errors[x[0]] = x[1]
            self.current_doc_errors = new_errors
            
            unique_error_ind = []
            error_ind = [self.current_doc_errors[x]['Index'] for x in self.current_doc_errors]
            for ind in error_ind:
                if ind in unique_error_ind:
                    self.error_intersects.add(ind)
                else:
                    unique_error_ind.append(ind)                
            self.embedded,self.overlap1,self.overlap2 = self.find_embeddings(unique_error_ind)
            self.make_one_file(ann[:ann.find('.ann')],str(i))
            i += 1
            self.current_doc_errors.clear()

    def find_embeddings(self,indices):
        indices.sort(key=lambda x: (x[0],-x[1]))
        embedded = []
        overlap1, overlap2 = [],[]
        self.embedding = defaultdict(list)
        for i in range(1,len(indices)):
            find_emb = [x for x in indices if (x[0] <= indices[i][0] and x[1] > indices[i][1]) or \
                                              (x[0] < indices[i][0] and x[1] >= indices[i][1])]
            if find_emb:
                for j in find_emb:
                    self.embedding[str(j)].append(indices[i])
                embedded.append(indices[i])
            else:
                overlaps = [x for x in indices if x[0] < indices[i][0] and (x[1] > indices[i][0] and
                                                                            x[1] < indices[i][1])]
                if overlaps:
                    overlap1.append(overlaps[0])
                    overlap2.append(indices[i])
        return embedded, overlap1, overlap2
        
    def tackle_embeddings(self,dic):
        b = dic.get('Index')[0]
        emb_errors = [x for x in self.current_doc_errors.items() if x[1]['Index'] in self.embedding[str(dic.get('Index'))]]
        new_wrong = ''
        nw = 0
        ignore = []
        for j,ws in enumerate(dic['Wrong']):
            emb_intersects = []
            for t,e in emb_errors:
                if e['Index'][0]-b == j:
                    if 'Right' in e and 'Right' in dic and e['Right'] == dic['Right']:
                        break
                    if str(e['Index']) in self.embedding:
                        ignore += self.embedding[str(e['Index'])]
                    if e['Index'] in self.error_intersects:
                        emb_intersects.append((int(t[1:]),e))
                        continue
                    if e['Index'] not in ignore:
                        if 'Right' in e:
                            new_wrong += e['Right']
                            nw = len(e['Wrong'])
                        elif 'Delete' in e:
                            nw = len(e['Wrong'])
            if emb_intersects:
                emb_intersects = sorted(emb_intersects,key=lambda x: x[0])
                last = emb_intersects[-1][1]
                L = -1
                while 'Right' not in last:
                    L -= 1
                    last = emb_intersects[L][1]
                new_wrong += last['Right']
                nw = len(last['Wrong'])
            if not nw:
                new_wrong += ws
            else:
                nw -= 1
        return new_wrong

    def find_overlap(self,s1,s2):
        m = difflib.SequenceMatcher(None, s1, s2).get_matching_blocks()
        if len(m) > 1:
            for x in m[:-1]:
                if x.b == 0:
                    return x.size
        return 0
            

    def make_one_file(self, filename, new_filename):
        """
        Makes file with current types of errors. all other errors checked.
        :param filename: name of the textfile
        return: nothing. just write files in dir <<processed_texts>>
        """
        with open(self.path_new+new_filename+'.txt', 'w', encoding='utf-8') as new_file:
            with open(filename+'.txt', 'r', encoding='utf-8') as text_file:
                one_text = text_file.read()
                not_to_write_sym = 0
                for i, sym in enumerate(one_text):
                    intersects = []
                    for t_key, dic in self.current_doc_errors.items():
                        if dic.get('Index')[0] == i:
                            if dic.get('Error') == 'Punctuation' and 'Right' in dic and \
                               not dic.get('Right').startswith(','):
                                dic['Right'] = ' '+dic['Right']
                            if dic.get('Index') in self.embedded:
                                continue
                            if str(dic.get('Index')) in self.embedding:
                                if dic.get('Error') in self.error_type:
                                    new_wrong = self.tackle_embeddings(dic)
                                    new_file.write('**'+str(dic.get('Right'))+'**'+str(len(new_wrong))+'**'+new_wrong)
                                    not_to_write_sym = len(dic['Wrong'])
                                    break

                            if dic.get('Index') in self.overlap1:
                                if dic.get('Error') not in self.error_type:
                                    overlap2_ind = self.overlap2[self.overlap1.index(dic.get('Index'))]
                                    overlap2_err = [x for x in self.current_doc_errors.values() if x['Index'] == overlap2_ind][-1]
                                    if 'Right' in dic and 'Right' in overlap2_err:
                                        rn = self.find_overlap(dic['Right'],overlap2_err['Right'])
                                        wn = dic['Index'][1] - overlap2_err['Index'][0]
                                        indexes_comp = dic.get('Index')[1] - dic.get('Index')[0] - wn
                                        if rn == 0:
                                            new_file.write(str(dic.get('Right'))+'#'+str(indexes_comp)+'#'+str(dic.get('Wrong'))[:-wn])
                                        else:
                                            new_file.write(str(dic.get('Right')[:-rn])+'#'+str(indexes_comp)+'#'+str(dic.get('Wrong'))[:-wn])
                                        not_to_write_sym = len(str(dic.get('Wrong'))) - wn
                                        break

                            if dic.get('Index') in self.overlap2:
                                overlap1_ind = self.overlap1[self.overlap2.index(dic.get('Index'))]
                                overlap1_err = [x for x in self.current_doc_errors.values() if x['Index'] == overlap1_ind][-1]
                                if overlap1_err['Error'] in self.error_type:
                                    if dic.get('Error') not in self.error_type:
                                        if 'Right' in dic and 'Right' in overlap1_err:
                                            rn = self.find_overlap(overlap1_err['Right'],dic['Right'])
                                            wn = overlap1_err['Index'][1] - dic['Index'][0]
                                            indexes_comp = dic.get('Index')[1] - dic.get('Index')[0] - wn
                                            new_file.write(dic.get('Wrong')[:wn] + dic.get('Right')[rn:] +'#'+str(indexes_comp)+ '#'+dic.get('Wrong')[wn:])
                                            not_to_write_sym = len(str(dic.get('Wrong')))
                                    break
                                    
                                    
                            if dic.get('Index') in self.error_intersects:
                                intersects.append((int(t_key[1:]),dic))
                                continue
    
                            if dic.get('Right'):
                                indexes_comp = dic.get('Index')[1] - dic.get('Index')[0]
                                if dic.get('Error') in self.error_type:
                                    new_file.write('**'+str(dic.get('Right'))+'**'+str(indexes_comp)+'**')
                                else:
                                    new_file.write(dic.get('Right') +
                                                   '#'+str(indexes_comp)+ '#')
                            else:
                                if dic.get('Delete'):
                                    indexes_comp = dic.get('Index')[1] - dic.get('Index')[0]
                                    new_file.write("#DELETE#"+str(indexes_comp)+"#")
                                    
                    if intersects:
                        intersects = sorted(intersects,key=lambda x: x[0])
                        intersects = [x[1] for x in intersects]
                        needed_error_types = [x for x in intersects if x['Error'] in self.error_type]
                        if needed_error_types and 'Right' in needed_error_types[-1]:
                            saving = needed_error_types[-1]
                            intersects.remove(saving)
                            if intersects:
                                to_change = intersects[-1]
                                if 'Right' not in to_change or to_change['Right'] == saving['Right']:
                                    indexes_comp = saving['Index'][1] - saving['Index'][0]
                                    new_file.write('**'+str(saving['Right'])+'**'+str(indexes_comp)+'**')
                                else: 
                                    indexes_comp = len(to_change['Right'])
                                    not_to_write_sym = saving['Index'][1] - saving['Index'][0]
                                    new_file.write('**'+str(saving['Right'])+'**'+str(indexes_comp)+'**'+to_change['Right'])
                        else:
                            if 'Right' in intersects[-1]:
                                if len(intersects) > 1 and 'Right' in intersects[-2]:
                                    indexes_comp = len(intersects[-2]['Right'])
                                    not_to_write_sym = intersects[-1]['Index'][1] - intersects[-1]['Index'][0]
                                    new_file.write(intersects[-1]['Right'] + '#'+str(indexes_comp)+ '#' + intersects[-2]['Right'])
                                else:
                                    indexes_comp = intersects[-1]['Index'][1] - intersects[-1]['Index'][0]
                                    new_file.write(intersects[-1]['Right'] + '#'+str(indexes_comp)+ '#')
                    if not not_to_write_sym:
                        new_file.write(sym)
                    else:
                        not_to_write_sym -= 1

    # ================Write Exercises to the files=================

    def find_choices(self, right, wrong, new_sent): #TODO @Kate, rewrite this function
        """
        Finds two more choices for Multiple Choice exercise.
        :param right:
        :param wrong:
        :return: array of four choices (first is always right)
        """
        right = re.sub('[а-яА-ЯЁё].*?[а-яёА-ЯЁ]','',right)
        wrong = re.sub('[а-яА-ЯЁё].*?[а-яёА-ЯЁ]','',wrong)
        choices = [right, wrong]
        #смотрим на то, какой массив мы передали объекту, так как отследить, какая ошибка обрабатывается сейчас мы уже не можем
        if self.error_type == ['Number']:
            quantifiers = ('some', 'someone', 'somebody', 'one', 'everyone', 'everybody', 'noone', 'no-one', 'nobody', 'something', 'everything', 'nothing')
            if nltk.tag.staford(right.split()[0])[1].startswith('V') and nltk.tag.stanford([wrong.split()[0]])[1].startswith('V'):
                quant_presence = False
                tagged_sent = self.tagger.tag(new_sent.replace('_______',right).split())
                for i in range(len(tagged_sent)):
                    if tagged_sent[i][0] in quantifiers:
                        quant_presence = True
                    if tagged_sent[i][0] == right.split()[0] and tagged_sent[i][1].startswith('V') and quant_presence:
                        [choices.append(i) for i in (vff.neg(right), vff.neg(wrong))\
                         if (i!=right) and (i!=wrong) and (i!='') and (i!=None)]
                        break
        #смотрим на то, какой массив мы передали объекту, так как отследить, какая ошибка обрабатывается сейчас мы уже не можем
        elif self.error_type == ['Preposotional_noun','Prepositional_adjective','Prepositional_adv', 'Prepositional_verb']:
            #переписать с использованием nltk.stanford
            pr1 = spp.find_prep(right)
            pr2 = spp.find_prep(wrong)
            if pr1['prep']:
                prep, left, rite = pr1['prep'], pr1['left'], pr1['right']
                preps = 'at', 'for', 'on'
                variants = set(left + i + rite for i in preps)
                if ((left + rite).strip(' ') == (pr2['left']+pr2['right']).strip(' ')):
                    [choices.append(i) for i in variants if i.strip(' ') != right.lower().strip(' ') and i.strip(' ') != wrong.lower().strip(' ')]
            elif pr2['prep']:
                prep, left, rite = pr2['prep'], pr2['left'], pr2['right']
                preps = 'at', 'for', 'on'
                variants = set(left + i + rite for i in preps)
                if left+rite.strip(' ') == pr1['left'].strip(' '):
                    [choices.append(i) for i in variants if i.strip(' ') != right.lower().strip(' ') and i.strip(' ') != wrong.lower().strip(' ')]
        #на союзы(пункт 4-5) не находит примеров
        elif self.error_type == ['Conjunctions','Absence_comp_sent','Lex_item_choice','Word_choice','Conjunctions','Lex_part_choice','Often_confused','Absence_comp_colloc','Redundant','Redundant_comp']:
            #переписать с использованием nltk.stanford
            conjunctions1 = ['except', 'besides','but for']
            conjunctions2 = ['even if', 'even though', 'even']
            if right in conjunctions1:
                [choices.append(i) for i in conjunctions1 if (i != right) and (i != wrong)]
            elif right in conjunctions2:
                [choices.append(i) for i in conjunctions2 if (i != right) and (i != wrong)]
        elif self.error_type == ['Defining']:
            #переписать с использованием nltk.stanford
            gerund_form = spp.find_verb_form(right,'gerund')
            add_forms = vff.find_verb_forms(gerund_form)
            new_choices = []
            if gerund_form:
                continuous_form = spp.find_anal_form(right,gerund_form)
                new_choices.append(right.replace(gerund_form, 'being ' + add_forms['3rd'], 1))
                new_choices.append(right.replace(continuous_form, add_forms['2nd'], 1))
                if ("n't" in continuous_form) or ('not' in continuous_form):
                    new_choices = [vff.neg(i) for i in new_choices]
                [choices.append(i) for i in new_choices if i != right and i != wrong]
        elif self.error_type == ['Choice_in_cond','Form_in_cond','Incoherent_in_cond'] and ('would' in right):
            #переписать с использованием nltk.stanford
            neg = False
            if "wouldn't" in right:
                neg = True
            lex_verb = spp.find_verb_form(right[right.find('would'):],'any')
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
            new_choices = [right[:right.find('would')]+i+right[right.find(lex_verb)+len(lex_verb):] for i in new_choices]
            [choices.append(i) for i in new_choices if i!=right and i != wrong]
        return choices[:4]

    

    def check_headform(self, word):
        """Take initial fowm - headform of the word"""
        for key, value in self.wf_dictionary.items():
            headword = [val for val in value if val == word]
            if len(headword)>0:
                return key

    def create_sentence_function(self, new_text):
        """
        Makes sentences and write answers for all exercise types
        :return: array of good sentences. [ (sentences, [right_answer, ... ]), (...)]
        """
        good_sentences = {x:list() for x in self.exercise_types}
        sentences = [''] + new_text.split('. ')
        i = 0
        for sent1, sent2, sent3 in zip(sentences, sentences[1:], sentences[2:]):
            i += 1
            to_skip = False
            if '**' in sent2:
                ex_type = random.choice(self.exercise_types)
                try:
                    sent, right_answer, index, other = sent2.split('**')
                    wrong = other[:int(index)]
                    new_sent, answers = '', []
                    if ex_type == 'word_form':
                        try:
                            new_sent = sent + "{1:SHORTANSWER:=%s}" % right_answer + ' (' +\
                                   self.check_headform(right_answer) + ')' + other[int(index):] + '.'
                            answers = [right_answer]
                        except:
                            if len(self.exercise_types) > 1:
                                while ex_type == 'word_form':
                                    ex_type = random.choice(self.exercise_types)
                            else:
                                continue
                    if ex_type == 'short_answer':
                        if self.bold:
                            new_sent = sent + '<b>' + wrong + '</b>' + other[int(index):] + '.'
                        else:
                            new_sent = sent + wrong + other[int(index):] + '.'
                        answers = [right_answer]
                    if ex_type == 'open_cloze':
                        new_sent = sent + "{1:SHORTANSWER:=%s}" % right_answer + other[int(index):] + '.'
                        answers = [right_answer]
                    if ex_type == 'multiple_choice':
                        new_sent = sent + "_______ " + other[int(index):] + '.'
                        answers = self.find_choices(right_answer, wrong, new_sent)
                        if len(answers)<3:
                            sentences[i] = sent + ' ' + right_answer + ' ' + other[int(index):] + '.'
                            answers = []
                        else:
                            print('choices: ',answers)
                        
                except:
                    split_sent = sent2.split('**')
                    n = (len(split_sent) - 1) / 3
                    try:
                        chosen = random.randint(0,n-1)
                    except:
                        print('Some issues with markup, skipping:',sent2)
                        continue
                    new_sent,answers = '',[]
                    for i in range(0,len(split_sent),3):
                        if len(split_sent[i:i+4]) > 1 and not to_skip:
                            sent, right_answer, index, other = split_sent[i],split_sent[i+1],split_sent[i+2],split_sent[i+3]
                            try:
                                index = int(index)
                            except:
                                to_skip = True
                                continue
                            if ex_type == 'open_cloze' or ex_type == 'word_form':
                                if ex_type == 'open_cloze':
                                    new_sent += "{1:SHORTANSWER:=%s}" % right_answer + other[int(index):]
                                elif ex_type == 'word_form':
                                    try:
                                        new_sent += "{1:SHORTANSWER:=%s}" % right_answer + ' (' +\
                                            self.check_headform(right_answer) + ')' + other[int(index):]
                                    except:
                                        new_sent += right_answer + other[int(index):]
                            else:
                                if i == chosen*3:
                                    wrong = other[:int(index)]
                                    if ex_type == 'short_answer':
                                        if self.bold:
                                            new_sent += '<b>' + wrong + '</b>' + other[int(index):]
                                        else:
                                            new_sent += wrong + other[int(index):]
                                        answers = [right_answer]
                                    elif ex_type == 'multiple_choice':
                                        new_sent += "_______ " + other[int(index):]
                                        answers = self.find_choices(right_answer, wrong, sent)
                                        if len(answers)<3:
                                            new_sent += right_answer + other[int(index):]
                                            answers = []
                                else:
                                    new_sent += right_answer + other[int(index):]
                            if i == 0:
                                new_sent = sent + new_sent
                        else:
                            new_sent = new_sent + '.'
                if sent1 and sent3 and self.context: # fixed sentences beginning with a dot
                    text = sent1 + '. ' + new_sent + ' ' + sent3 + '.'
                elif sent3 and self.context:
                    text = new_sent + ' ' + sent3 + '.'
                else:
                    text = new_sent
                text = re.sub(' +',' ',text)
                text = re.sub('[а-яА-ЯЁё]+','',text)
                if ('**' not in text) and (not to_skip) and (answers != []):
                    print('answers: ', answers)
                    good_sentences[ex_type].append((text, answers))
                elif '**' in text:
                    print('answers arent added cause ** in text: ', answers)
                elif to_skip:
                    print('answers arent added cause to_skip = True: ', answers)
        return good_sentences

    def write_sh_answ_exercise(self, sentences, ex_type):
        pattern = '<question type="shortanswer">\n\
                    <name>\n\
                    <text>Grammar realec. Short answer {}</text>\n\
                     </name>\n\
                <questiontext format="html">\n\
                <text><![CDATA[{}]]></text>\n\
             </questiontext>\n\
        <answer fraction="100">\n\
        <text><![CDATA[{}]]></text>\n\
        <feedback><text>Correct!</text></feedback>\n\
        </answer>\n\
        </question>\n'
        with open('./moodle_exercises/{}.xml'.format(ex_type), 'w', encoding='utf-8') as moodle_ex:
            moodle_ex.write('<quiz>\n')
            for n, ex in enumerate(sentences):
                moodle_ex.write((pattern.format(n, ex[0], ex[1][0])).replace('&','and'))
            moodle_ex.write('</quiz>')
        with open('./moodle_exercises/{}.txt'.format(ex_type), 'w', encoding='utf-8') as plait_text:
            for ex in sentences:
                plait_text.write(ex[1][0]+'\t'+ex[0]+'\n\n')

    def write_multiple_ch(self, sentences, ex_type):
        pattern = '<question type="multichoice">\n \
        <name><text>Grammar realec. Multiple Choice question {} </text></name>\n \
        <questiontext format = "html" >\n <text> <![CDATA[ <p> {}<br></p>]]></text>\n</questiontext>\n\
        <defaultgrade>1.0000000</defaultgrade>\n<penalty>0.3333333</penalty>\n\
        <hidden>0</hidden>\n<single>true</single>\n<shuffleanswers>true</shuffleanswers>\n\
        <answernumbering>abc</answernumbering>\n<correctfeedback format="html">\n\
        <text>Your answer is correct.</text>\n</correctfeedback>\n\
        <partiallycorrectfeedback format="html">\n<text>Your answer is partially correct.</text>\n\
        </partiallycorrectfeedback>\n<incorrectfeedback format="html">\n\
        <text>Your answer is incorrect.</text>\n</incorrectfeedback>\n'

        with open('./moodle_exercises/{}.xml'.format(ex_type+'_'+' '.join(self.error_type)), 'w', encoding='utf-8') as moodle_ex:
            moodle_ex.write('<quiz>\n')
            for n, ex in enumerate(sentences):
                moodle_ex.write((pattern.format(n, ex[0])).replace('&','and'))
                for n, answer in enumerate(ex[1]):
                    correct = 0
                    if n == 0:
                        correct = 100
                    moodle_ex.write('<answer fraction="{}" format="html">\n<text><![CDATA[<p>{}<br></p>]]>'
                                    '</text>\n<feedback format="html">\n</feedback>\n</answer>\n'.format(correct, answer))
                moodle_ex.write('</question>\n')
            moodle_ex.write('</quiz>')
        with open('./moodle_exercises/{}.txt'.format(ex_type+'_'+' '.join(self.error_type)), 'w',encoding='utf-8') as plait_text:
            for ex in sentences:
                plait_text.write(ex[0] + '\n' + '\t'.join(ex[1]) + '\n\n')


    def write_open_cloze(self, sentences, ex_type):
        """:param type: Word form or Open cloze"""
        type = ''
        if ex_type == 'word_form':
            type = "Word form"
        elif ex_type == 'open_cloze':
            type = "Open Cloze"
        pattern = '<question type="cloze"><name><text>Grammar realec. {} {}</text></name>\n\
                     <questiontext format="html"><text><![CDATA[<p>{}</p>]]></text></questiontext>\n''<generalfeedback format="html">\n\
                     <text/></generalfeedback><penalty>0.3333333</penalty>\n\
                     <hidden>0</hidden>\n</question>\n'
        with open('./moodle_exercises/{}.xml'.format(ex_type), 'w', encoding='utf-8') as moodle_ex:
            moodle_ex.write('<quiz>\n')
            for n, ex in enumerate(sentences):
                moodle_ex.write((pattern.format(type, n, ex[0])).replace('&','and'))
            moodle_ex.write('</quiz>')
        with open('./moodle_exercises/{}.txt'.format(ex_type), 'w', encoding='utf-8') as plait_text:
            for ex in sentences:
                plait_text.write(ex[0]+'\n\n')

    def make_exercise(self):
        """Write it all in moodle format and txt format"""
        all_sents = {x:list() for x in self.exercise_types}
        for f in os.listdir(self.path_new):
            new_text = ''
            with open(self.path_new + f,'r', encoding='utf-8') as one_doc:
                text_array = one_doc.read().split('#')
                current_number = 0
                for words in text_array:
                    words = words.replace('\n', ' ').replace('\ufeff', '')
                    if re.match('^[0-9]+$', words):
                        if words != '':
                            current_number = int(words)
                    elif words == 'DELETE':
                        current_number = 0
                    else:
                        new_text += words[current_number:]
                        current_number = 0
            if '**' in new_text:
                new_sents = self.create_sentence_function(new_text)
                for key in all_sents:
                    all_sents[key] += new_sents[key]
        for key in all_sents:
            self.write_func[key](all_sents[key],key)

        #shutil.rmtree('./processed_texts/')

if __name__ == "__main__":

    path_to_data = './new/IELTS/'
    #передаём только определённый вариат задания
    e = Exercise(path_to_data, ['Preposotional_noun','Prepositional_adjective','Prepositional_adv', 'Prepositional_verb'], ['multiple_choice'], bold=False, context=True)
    e.make_data_ready_4exercise()

    e.make_exercise()
