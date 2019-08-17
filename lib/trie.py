"""
TODO:
https://engineering.linecorp.com/ja/blog/simple-tries/
あとでこれの実装試してみる

"""
import time
from bisect import bisect


class TrieNode(object):
    """
    implementation of Trie tree node
    using sibling-first algorithm
    cf. https://engineering.linecorp.com/ja/blog/simple-tries/
    """

    def __init__(self, root):
        self.root = self
        self.labels = [None]
        self.existent_flags = [False]
        self.children_start = [0]
        self.children_end = [0]

    def find_child_id(self, node_id, label):
        """
        returns child node id for label
        :param node_id:
        :param label:
        :return:
        """
        children_start, children_end = self.children_start[node_id], self.children_end[node_id]
        if children_end - children_start == 1 and self.labels[children_start] == label:
            return children_start
        i = bisect(self.labels, label, children_start, children_end)
        if i > children_start and self.labels[i - 1] == label:
            return i - 1
        return None

    def add_children(self, node_id, labels, existent_flags):
        children_labels = list(labels)
        len_children_labels = len(children_labels)
        len_current_labels = len(self.labels)

        self.children_start[node_id] = len_current_labels
        self.labels += children_labels
        self.children_start += [0] * len_children_labels
        self.children_end += [0] * len_children_labels
        self.existent_flags += existent_flags
        self.children_end[node_id] = len_current_labels + len_children_labels

    def find_node_id(self, root, query):
        """
        return node id for query
        :param root: root node
        :param query: query
        :return:
        """
        node_id = 0

        for c in query:
            node_id = self.find_child_id(node_id, c)
            if node_id is None:
                return None
        return node_id

    def enumerate_existent_offspring_words(self, root, node_id, my_label):
        """
        enumerates all existent offsprings of this node, including itself (if it exists)
        :return: generator of TrieNode's
        """
        if self.existent_flags[node_id]:
            yield my_label
        children_start, children_end = self.children_start[node_id], self.children_end[node_id]
        for child_id in range(children_start, children_end):
            label = self.labels[child_id]
            for item in self.enumerate_existent_offspring_words(root, child_id, my_label + label):
                yield item

    # following methods are independent of data structure.

    def search(self, item) -> bool:
        """
        search given item
        :param item: item to search
        :return: True if found, else False
        """
        target_id = self.find_node_id(self.root, item)
        return (target_id is not None) and self.existent_flags[target_id]

    def common_prefix_search(self, query) -> [str]:
        """
        yields prefixes of given query
        :param query: query to search
        :return: possible prefixes in this Trie tree
        """
        node_id = 0
        for i, c in enumerate(query):
            node_id = self.find_child_id(node_id, c)
            if node_id is None:
                return
            if self.existent_flags[node_id]:
                yield query[0: i + 1]

    def predictive_search(self, prefix) -> [str]:
        """
        yields items which has the given prefix
        :param prefix:
        :return: possible strings in this Trie tree
        """

        target_node_id = self.find_node_id(self.root, prefix)
        if target_node_id is None:
            return []
        return self.enumerate_existent_offspring_words(self.root, target_node_id, prefix)
        # return self.root.sftrie_nodes[target_node_id].enumerate_existent_offsprings(prefix)

    def prefix_search(self, query) -> str:
        """
        returns longest prefix for given query
        :param query:
        :return:
        """
        longest = 0
        node_id = 0
        for i, c in enumerate(query):
            node_id = self.find_child_id(node_id, c)
            if node_id is None:
                break
            if self.existent_flags[node_id]:
                longest = i + 1

        if longest is None:
            return ''
        else:
            return query[0: longest]

    def __repr__(self):
        return f'{self.id}'


class TrieBuilder(object):
    """
    Builds Trie tree using Trie node class
    """

    def __init__(self, words: [str]):
        self.root = TrieNode(None)
        words = list(words)
        words.sort()
        word_lengths = list(len(w) for w in words)

        self.id = 0
        self.sibling_first_search(0, words, word_lengths, 0, len(words), 0)

    def compile(self) -> TrieNode:
        """
        compiles Trie tree
        :return: compiled root node object
        """
        trie = self.root

        return trie

    def sibling_first_search(self, node_id: int, words: [str], word_lengths: [int],
                             start_index: int, end_index: int, depth: int):
        """
        search words in sibling first algorithm
        :param root: root node
        :param node_id: id of parent node
        :param words: words for this trie tree
        :param start_index: starting index of parent node
        :param end_index: last index + 1 of parent node
        :param depth: depth of current search
        """
        next_labels = []
        existent_flags = []
        label_indices = []
        last_label = None
        child_ids = {}
        for i in range(start_index, end_index):
            if word_lengths[i] <= depth:
                continue
            current_label = words[i][depth]
            if last_label != current_label:
                next_labels.append(current_label)
                existent_flags.append(word_lengths[i] == depth + 1)
                label_indices.append(i)
                child_ids[current_label] = len(self.root.labels) + len(label_indices) - 1
                last_label = current_label
        label_indices.append(end_index)
        self.root.add_children(node_id, next_labels, existent_flags)
        for i in range(len(next_labels)):
            self.sibling_first_search(child_ids[next_labels[i]], words, word_lengths, label_indices[i],
                                      label_indices[i + 1], depth + 1)

