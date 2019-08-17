import sys
import time

from dic.morphemerule import load_connection_rules, ConnectionRule, find_rule
from dic.dic import load_conjugation_types, load_dic_files, Morpheme
from lib.trie import TrieNode


def make_lattice(trie: TrieNode, dic: {str: [Morpheme]}, s: str):
    """
    Lattice design

    lattice[pos]: [Morpheme]
    """
    lattice = []
    for pos in range(len(s)):
        morphemes = []
        for prefix in trie.common_prefix_search(s[pos:]):
            morphemes += dic[prefix]
        lattice.append(morphemes)
    return lattice


def find_shortest_path(lattice: [[Morpheme]], rules: {str: [ConnectionRule]},
                       before: Morpheme, pos: int, cache: {int: (int, [Morpheme], bool)}) -> (int, [Morpheme], bool):
    """
    returns shortest path's cost and morphemes after current morpheme
    :param lattice:
    :param rules:
    :param before:
    :param pos:
    :return:
    """
    if pos in cache:
        return cache[pos]

    minimum_cost = sys.maxsize
    minimum_morphemes = []
    minimum_rule_3 = False

    for current in lattice[pos]:
        if pos + len(current.surface) == len(lattice):  # 最後まで見たとき
            if current.cost < minimum_cost:
                minimum_morphemes = [current]
                minimum_cost = current.cost
                minimum_rule_3 = False
            continue
        next_pos = pos + len(current.surface)
        for after in lattice[next_pos]:
            matched_rule = find_rule(rules, before, current, after)
            if matched_rule is not None:
                next_cost, next_morphemes, next_rule_3 = find_shortest_path(lattice, rules, current, next_pos, cache)
                current_cost = current.cost + next_cost + (0 if next_rule_3 else matched_rule.cost)
                if current_cost < minimum_cost:
                    minimum_cost = current_cost
                    minimum_morphemes = [current] + next_morphemes
                    minimum_rule_3 = (matched_rule.before is not None)

    cache[pos] = (minimum_cost, minimum_morphemes, minimum_rule_3)
    return cache[pos]

st = time.time()
rules = load_connection_rules()
conjugation_types = load_conjugation_types()
trie, dic = load_dic_files(conjugation_types)
et = time.time()

print('Ready. ({} sec)'.format(et - st))

while True:
    s = input('> ')
    # s = '高気圧です。'
    if s.startswith('?'):
        q = s[1:]
        print(dic[q])
        continue

    st = time.time()
    lattice = make_lattice(trie, dic, s)
    result = find_shortest_path(lattice, rules, None, 0, {})
    et = time.time()
    print(result)
    print('Ready. ({} sec)'.format(et - st))
    """
    min_cost = sys.maxsize
    min_cost_p = None
    for p in enumerate_tokenisation_possibilities(trie, dic, s):
        print(p)
        cost = calc_cost(p, connection_rules)
        print(cost)
        if min_cost > cost:
            min_cost = cost
            min_cost_p = p
    print('RESULT:')
    print(min_cost_p)
    """
