import time

from lib.trie import TrieBuilder, TrieNode
from lib import lisp
import glob
import copy

DIC_FILES = './ipadic-2.7.0/*.dic'
CFORMS_FILE = './ipadic-2.7.0/cforms.cha'


class ConjugationForm(object):
    def __init__(self, cform):
        self.name = cform[0]
        if cform[1] != '*':
            self.ending = cform[1]
            self.ending_kana = cform[2]
        else:
            self.ending = ''
            self.ending_kana = ''


class ConjugationType():
    def __init__(self, ctype):
        self.name = ctype[0]
        self.forms = {}
        for cform in ctype[1]:
            form = ConjugationForm(cform)
            self.forms[form.name] = form

    def conjugate(self, morpheme):
        """
        yields list of conjugated forms
        :param morpheme:
        :return:
        """
        basic_form_ending = self.forms['基本形'].ending
        if not morpheme.surface.endswith(basic_form_ending):
            raise ValueError()
        stem = morpheme.surface[0: -len(basic_form_ending)]
        for form in self.forms.values():  # type: ConjugationForm
            new_form = stem + form.ending
            new_morpheme = copy.copy(morpheme)
            new_morpheme.surface = new_form
            new_morpheme.conjugation_form = form.name
            yield new_morpheme


def load_conjugation_types():
    conjugation_types = {}
    for cform in [ConjugationType(f) for f in lisp.load(CFORMS_FILE)]:
        conjugation_types[cform.name] = cform
    return conjugation_types


class Morpheme:
    def __init__(self, entry):
        self.pos = '-'.join(entry[0][1])
        self.conjugation_form = '基本形'
        self.conjugation_type = None
        midashigo = entry[1][0][1]
        if type(midashigo) is str:
            # コストなしの場合
            self.surface = midashigo
            self.cost = None
        else:
            self.surface = midashigo[0]
            self.cost = int(midashigo[1])
        for info in entry[1][1:]:
            if info[0] == '活用型':
                self.conjugation_type = info[1]
            if info[0] == '活用形':
                self.conjugation_form = info[1]

    def __repr__(self):
        return '{}({}-{}-{})'.format(self.surface, self.pos, self.conjugation_type, self.conjugation_form)


def get_dic_files():
    """
    returns list of dic files
    :return:
    """
    return glob.glob(DIC_FILES)


def load_dic_files(conjugation_types: {str: ConjugationType}):
    dic = dict()

    for filename in get_dic_files():
        print('loading {}...'.format(filename))
        entries = lisp.load(filename)
        for i in range(0, len(entries), 2):
            entry = (entries[i], entries[i + 1])
            morpheme = Morpheme(entry)
            if morpheme.surface in dic:
                dic[morpheme.surface].append(morpheme)
            else:
                dic[morpheme.surface] = [morpheme]
            if morpheme.conjugation_type:
                for conjugated in conjugation_types[morpheme.conjugation_type].conjugate(morpheme):
                    if conjugated.surface in dic:
                        dic[conjugated.surface].append(conjugated)
                    else:
                        dic[conjugated.surface] = [conjugated]

    t = TrieBuilder(dic.keys())

    return t.compile(), dic

