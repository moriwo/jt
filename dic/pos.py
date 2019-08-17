# !!! unused


from lib import lisp

POS_DEFINITION_FILE = './ipadic-2.7.0/grammar.cha'


class Pos():
    def __init__(self, pos_list):
        self.name = pos_list[0].rstrip('%')
        self.conjugatable = pos_list[0][-1] == '%'
        self.conjugation_types = {}
        self.sub_pos = {}
        for sub_list in pos_list[1:]:
            pos = Pos(sub_list)
            self.sub_pos[pos.name] = pos


def load_pos_definition():
    pos_definition = {}
    for pos in [Pos(p) for p in lisp.load(POS_DEFINITION_FILE)]:
        pos_definition[pos.name] = pos




if __name__ == '__main__':
    print(load_pos_definition())
