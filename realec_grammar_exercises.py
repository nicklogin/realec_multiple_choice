import sys, codecs, re, os
from collections import defaultdict
import shutil
import json
import verb_forms_finder as vff

"""Script that generates grammar exercises from REAELEC data """
print('started')
#класс объектов Exercise
#аргументы - путь к данным эссе, тип ошибки, тип задания
class Exercise:
    def __init__(self, path_to_realecdata, error_type, exercise_type):

        """"
        :param error_type: 'Tense_choice', 'Tense_form', 'Voice_choice', 'Voice_form', 'Number'
        :param exercise_type: multiple_choice, word_formation, short_answer, open_cloze
        """
        #путь к токенизированным текстам:
        self.path_new = './processed_texts/'
        #путь к нетокенизированным текстам(который
        #был передан в качестве аргумента)
        self.path_old = path_to_realecdata
        #свойство объекта тип ошибки -
        #было передано в качестве аргумента:
        self.error_type = error_type
        #свойство объекта тип задания -
        #было передано в качестве аргумента:
        self.exercise_type = exercise_type
        self.current_doc_errors = defaultdict()
        self.headword = ''
        self.write_func = {
            "short_answer": self.write_sh_answ_exercise,
            "multiple_choice": self.write_multiple_ch,
            "word_form": self.write_open_cloze,
            "open_cloze": self.write_open_cloze
        }
        os.makedirs('moodle_exercises', exist_ok=True)
        os.makedirs('processed_texts', exist_ok=True)
        with open('./nug_needs/wordforms.json', 'r', encoding="utf-8") as dictionary:
            self.wf_dictionary = json.load(dictionary)  # {'headword':[words,words,words]}

#T-mark'ами отмечены строки с ошибками, их типом и местом в тексте
#решётками отмечены строки с исправлениями и указаниями на t-номера ошибок
#находим ошибки, указанные в аннотации
#заносим информацию в словарь, ключ - T-mark
#значение - словарь из трёх элементов - тип ошибки, индексы начала и конца ошибки в тексте,
#неправильно употреблённая словоформа:
    def find_errors_indoc(self, line):
        """
        Find all T... marks and save in dictionary.
        Format: {"T1":{'Error':err, 'Index':(index1, index2), "Wrong":text_mistake}}
        """
        if re.search('^T', line) is not None and 'pos_' not in line:
            try:
                t, span, text_mistake = line.strip().split('\t')
                err, index1, index2 = span.split()
                self.current_doc_errors[t] = {'Error':err, 'Index':(index1, index2), "Wrong":text_mistake}
            except:
                print("Something wrong! No Notes probably", line)

    def find_answers_indoc(self, line):
        if re.search('^#', line) is not None and 'lemma =' not in line:
            try:
                number, annotation, correction = line.strip().split('\t')
                #получаем T-mark ошибки:
                t_error = annotation.split()[1]
                if self.current_doc_errors.get(t_error):
                    #заносим в словарь с ощибками исправленную словоформу:
                    self.current_doc_errors[annotation.split()[1]]['Right'] = correction
            except:
                print("Something wrong! No Notes probably", line)

    def find_delete_seqs(self, line):
        if re.search('^A', line) is not None and 'Delete' in line:
            t = line.strip().split('\t')[1].split()[1]
            if self.current_doc_errors.get(t):
                self.current_doc_errors[t]['Delete'] = 'True'

    def make_data_ready_4exercise(self):
        """ Collect errors info """
        anns = [f for f in os.listdir(self.path_old) if f.endswith('.ann')]
        for ann in anns:
            #print(ann)
            with open(self.path_old + ann, 'r', encoding='utf-8') as ann_file:
                for line in ann_file.readlines():
                    self.find_errors_indoc(line)
                    self.find_answers_indoc(line)
                    self.find_delete_seqs(line)
            self.make_one_file(ann.split('.')[0])
            self.current_doc_errors.clear()

    def make_one_file(self, filename):
        """
        Makes file with current types of errors. all other errors checkes.
        :param filename: name of the textfile
        return: nothing. just write files in dir <<processed_texts>>
        """
        with open(self.path_new+filename+'.txt', 'a', encoding='utf-8') as new_file:
            with open(self.path_old+filename+'.txt', 'r', encoding='utf-8') as text_file:
                one_text = text_file.read()
                for i, sym in enumerate(one_text):
                    for t_key, dic in self.current_doc_errors.items():
                        if dic.get('Index')[0] == str(i):
                            if dic.get('Right'):
                                #вычисляем длину ошибки:
                                indexes_comp = int(dic.get('Index')[1]) - int(dic.get('Index')[0])
                                if dic.get('Error') in self.error_type:
                                    #когда индекс символа в эссе равен начальному символу
                                    #ошибки, записываем в звёздочках правильный вариант и длину ошибки
                                    new_file.write("*"+str(dic.get('Right'))+'*'+str(indexes_comp)+'*')
                                else:
                                    new_file.write(dic.get('Right') +
                                                   '#'+str(indexes_comp)+ '#')
                            else:
                                if dic.get('Delete'):
                                    indexes_comp = int(dic.get('Index')[1]) - int(dic.get('Index')[0])
                                    new_file.write("#DELETE#"+str(indexes_comp)+"#")
                    new_file.write(sym)

    # ================Write Exercises to the files=================

    def find_choices(self, right, wrong): #TODO @Kate, rewrite this function #Nck rewrote this function
        """
        Finds two more choices for Multiple Choice exercise.
        :param right:
        :param wrong:
        :return: array of four choices (first is always right)
        """
        verb_forms = vff.find_verb_forms(right)
        conjuctions1 = ['except', 'besides','but for']
        conjuctions2 = ['even if', 'even though', 'even']
        ##this part of code is temporary
        verb_forms = [i for i in set(verb_forms[i] for i in verb_forms)]
        if verb_forms:
            choices = set(verb_forms)
        ##end of temporary part
        elif right in conjuctions1:
            for i in conjuctions1:
                choices.add(i)
        elif right in conjuctions2:
            for i in conjuctions2:
                choices.add(i)
        choices.add(wrong)
        choices = [i for i in choices]
        choices = [right]+choices
        return choices

    
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
        good_sentences = []
        sentences = [''] + new_text.split('. ')
        for sent1, sent2, sent3 in zip(sentences, sentences[1:], sentences[2:]):
            if '*' in sent2:
                try:
                    sent, right_answer, index, other = sent2.split('*')
                    wrong = other[:int(index)]
                    new_sent, answers = '', []
                    if self.exercise_type == 'short_answer':
                        new_sent = sent + '<b>' + wrong + '</b>' + other[int(index):] + '.'
                        answers = [right_answer]
                    elif self.exercise_type == 'open_cloze':
                        new_sent = sent + "{1:SHORTANSWER:=%s}" % right_answer + other[int(index):] + '.'
                        answers = [right_answer]
                    elif self.exercise_type == 'word_form':
                        new_sent = sent + "{1:SHORTANSWER:=%s}" % right_answer + '(' +\
                               self.check_headform(right_answer) + ')' + other[int(index):] + '.'
                        answers = [right_answer]
                    elif self.exercise_type == 'multiple_choice':
                        new_sent = sent + "_______ " + other[int(index):] + '.'
                        answers = self.find_choices(right_answer, wrong)
                    text = sent1 + '. ' + new_sent + ' ' + sent3
                    if '*' not in text:
                        good_sentences.append((text, answers))
                except:
                    print("Bad: ", sent2)
        return good_sentences

    def write_sh_answ_exercise(self, sentences):
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
        with open('./moodle_exercises/{}_{}.xml'.format(self.error_type, self.exercise_type), 'w', encoding='utf-8') as moodle_ex:
            moodle_ex.write('<quiz>\n')
            for n, ex in enumerate(sentences):
                moodle_ex.write((pattern.format(n, ex[0], ex[1][0])).replace('&','and'))
            moodle_ex.write('</quiz>')
        with open('./moodle_exercises/{}_{}.txt'.format(self.error_type, self.exercise_type), 'w', encoding='utf-8') as plait_text:
            for ex in sentences:
                plait_text.write(ex[1][0]+'\t'+ex[0]+'\n\n')

    def write_multiple_ch(self, sentences):
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

        with open('./moodle_exercises/{}_{}.xml'.format(self.error_type, self.exercise_type), 'w', encoding='utf-8') as moodle_ex:
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
        with open('./moodle_exercises/{}_{}.txt'.format(self.error_type, self.exercise_type), 'w',
                  encoding='utf-8') as plait_text:
            for ex in sentences:
                plait_text.write(ex[0] + '\n' + '\t'.join(ex[1]) + '\n\n')


    def write_open_cloze(self, sentences):
        """:param type: Word form or Open cloze"""
        type = ''
        if self.exercise_type == 'word_form':
            type = "Word form"
        elif self.exercise_type == 'open_cloze':
            type = "Open Cloze"
        pattern = '<question type="cloze"><name><text>Grammar realec. {} {}</text></name>\n\
                     <questiontext format="html"><text><![CDATA[<p>{}</p>]]></text></questiontext>\n''<generalfeedback format="html">\n\
                     <text/></generalfeedback><penalty>0.3333333</penalty>\n\
                     <hidden>0</hidden>\n</question>\n'
        with open('./moodle_exercises/{}_{}.xml'.format(self.exercise_type, self.exercise_type), 'w', encoding='utf-8') as moodle_ex:
            moodle_ex.write('<quiz>\n')
            for n, ex in enumerate(sentences):
                moodle_ex.write((pattern.format(type, n, ex[0], ex[1][0])).replace('&','and'))
            moodle_ex.write('</quiz>')
        with open('./moodle_exercises/{}_{}.txt'.format(self.error_type, self.exercise_type), 'w', encoding='utf-8') as plait_text:
            for ex in sentences:
                plait_text.write(ex[0]+'\n\n')

    def make_exercise(self):
        """Write it all in moodle format and txt format"""
        all_sents = []
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
            if '*' in new_text:
                all_sents += self.create_sentence_function(new_text)
        self.write_func[self.exercise_type](all_sents)

        #shutil.rmtree('./processed_texts/')

if __name__ == "__main__":

    path_to_data = './IELTS2015/'
    e = Exercise(path_to_data, 'Tense_choice', 'multiple_choice')
    e.make_data_ready_4exercise()

    e.make_exercise()
