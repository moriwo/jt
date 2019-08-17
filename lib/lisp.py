"""
lisp-formatted file reader
"""


def load(filename: str) -> list:
    """
    loads lisp-formatted file
    all lisp lists parsed as python lists

    :param filename:
    :return: parsed data
    """
    with open(filename, 'rt', encoding='euc-jp') as f:
        s = ''.join(f)
    return parse(s, len(s), 0)


def parse(s: str, len_s: int, pos: int) -> (list, int):
    """
    parses lisp-formatted string

    :param s: string to parse
    :param len_s: length of s (=len(s))
    :param pos: give 0. used internally at recursive calls
    :return:

    >>> s = '(a "(" a\\\\" b "(\\\\")" \\\\\\\\)'
    >>> parse(s, len(s), 0)
    [['a', '(', 'a"', 'b', '(")', '\\\\']]
    >>> s = '(a b (c (d)) e)'
    >>> parse(s, len(s), 0)
    [['a', 'b', ['c', ['d']], 'e']]
    >>> s = '(a b (c (d)) e)\\n(f g ((h i) j (k)))'
    >>> parse(s, len(s), 0)
    [['a', 'b', ['c', ['d']], 'e'], ['f', 'g', [['h', 'i'], 'j', ['k']]]]
    """
    buf = []

    while pos < len_s:
        s_pos = s[pos]
        if s_pos == '(':
            child, pos = parse(s, len_s, pos + 1)
            buf.append(child)
        elif s_pos == ')':
            return buf, pos
        elif s_pos == ';':
            while s[pos] != '\n':
                pos += 1
        elif s_pos in {' ', '\n', '\t'}:
            pass
        else:
            value = ''
            quoted = False
            while True:
                c = s[pos]
                if not quoted and c in {' ', '\n', '\t', ')'}:
                    break
                if c == '"':
                    quoted = not quoted
                    pos += 1
                elif c == '\\':
                    value += s[pos+1]
                    pos += 2
                else:
                    value += c
                    pos += 1
            buf.append(value)
            pos -= 1
        pos += 1
    return buf


if __name__ == '__main__':
    import doctest
    doctest.testmod()