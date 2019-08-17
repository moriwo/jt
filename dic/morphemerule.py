import sys

from dic.dic import Morpheme
from lib import lisp


CONNECTION_FILE = './ipadic-2.7.0/connect.cha'


class MorphemeRule:
    """
    連接規則の品詞定義一個分
    """

    def __init__(self, pos_def):
        self.conjugation_type = '*'
        self.conjugation_form = '*'
        self.surface = '*'

        self.pos = '-'.join(pos_def[0])
        if len(pos_def) == 1:
            return
        self.conjugation_type = pos_def[1]
        if len(pos_def) == 2:
            return
        self.conjugation_form = pos_def[2]
        if len(pos_def) == 3:
            return
        self.surface = pos_def[3]
        return

    def match(self, morpheme: Morpheme):
        if not morpheme.pos.startswith(self.pos):
            return False
        if self.conjugation_type != '*' and morpheme.conjugation_type != self.conjugation_type:
            return False
        if self.conjugation_form != '*' and morpheme.conjugation_form != self.conjugation_form:
            return False
        if self.surface != '*' and morpheme.surface != self.surface:
            return False
        return True

    def __repr__(self):
        return '  > {} {} {} {}'.format(self.pos, self.conjugation_type, self.conjugation_form, self.surface)


class ConnectionRule:
    def __init__(self, rule):
        if len(rule[0]) == 2:  # 一番ふつうのルール
            self.before = None
            self.current = MorphemeRule(rule[0][0][0])
            self.after = MorphemeRule(rule[0][1][0])
            self.cost = int(rule[1])
        elif len(rule[0]) == 3:  # ３形態素ルール
            self.before = MorphemeRule(rule[0][0][0])
            self.current = MorphemeRule(rule[0][1][0])
            self.after = MorphemeRule(rule[0][2][0])
            self.cost = int(rule[1])
        else:
            import pprint
            pprint.pprint(rule)
            raise  # 想定外のルール

    def __repr__(self):
        return '{}¥n{}¥n{}¥n{}¥n¥n'.format(
            repr(self.before), repr(self.current), repr(self.after), self.cost
        )

    def match(self, before, current, after):
        if self.before is not None:
            if before is None:
                return False
            if not self.before.match(before):
                return False
        if not self.current.match(current):
            return False
        if not self.after.match(after):
            return False
        return True


def load_connection_rules():
    rules = dict()
    for entry in lisp.load(CONNECTION_FILE):
        rule = ConnectionRule(entry)
        if rule.current.pos not in rules:
            rules[rule.current.pos] = [rule]
        else:
            rules[rule.current.pos].append(rule)
    return rules


def find_rule(rules: {str: [ConnectionRule]}, before: Morpheme, current: Morpheme, after: Morpheme) -> ConnectionRule:
    """
    連接表ファイルのルールから適用されるべき連接コストを返す。
    同時に、3形態素ルールだったかどうかも返す。

    :param rules:
    :param before:
    :param current:
    :param after:
    :return:
    """
    for rule in reversed(rules[current.pos]):
        if rule.match(before, current, after):
            return rule
    return None
