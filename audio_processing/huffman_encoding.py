import math
from typing import Optional

class HuffmanTree:
    def __init__(self, prob, left_child=None, right_child=None, label=None) -> None:
        self.left: Optional[HuffmanTree] = left_child
        self.right: Optional[HuffmanTree] = right_child
        self.prob = prob
        self.label = label
    
    def get_dictionary(self, current_path = "") -> dict:
        if self.label is not None:
            return {self.label: current_path}
        assert (self.left is not None)
        assert (self.right is not None)
        return {**self.left.get_dictionary(current_path + "0"), **self.right.get_dictionary(current_path + "1")}

class HuffmanEncoder:
    def __init__(self) -> None:
        self.initialized = False
        self.alphabet_stats = dict()
        self.encoding_dictionary = dict()
        self.huffman_tree = None

    @staticmethod
    def _build_huffman_tree(weights: dict) -> HuffmanTree:
        sorted_weights = dict(sorted(weights.items(), key=lambda item: item[1]))
        leaves_queue: list[HuffmanTree] = []
        trees_queue: list[HuffmanTree] = []
        for character, weight in sorted_weights.items():
            leaves_queue.append(HuffmanTree(weight, label=character))
        while len(leaves_queue) + len(trees_queue) > 1:
            leaves0weight = leaves_queue[0].prob if len(leaves_queue) > 0 else math.inf
            leaves1weight = leaves_queue[1].prob if len(leaves_queue) > 1 else math.inf
            trees0weight = trees_queue[0].prob if len(trees_queue) > 0 else math.inf
            trees1weight = trees_queue[1].prob if len(trees_queue) > 1 else math.inf

            if leaves0weight < trees0weight:
                left_child = leaves_queue[0]
                leaves_queue.pop(0)
                if leaves1weight < trees0weight:
                    right_child = leaves_queue[0]
                    leaves_queue.pop(0)
                else:
                    right_child = trees_queue[0]
                    trees_queue.pop(0)
            else:
                left_child = trees_queue[0]
                trees_queue.pop(0)
                if leaves0weight < trees1weight:
                    right_child = leaves_queue[0]
                    leaves_queue.pop(0)
                else:
                    right_child = trees_queue[0]
                    trees_queue.pop(0)
            
            trees_queue.append(HuffmanTree(left_child.prob + right_child.prob, left_child=left_child, right_child=right_child))
        
        return trees_queue[0]

    def initialize(self, text: str) -> None:
        if self.initialized:
            raise ValueError("Encoder is already initialized")
        self.alphabet_stats = dict()
        for character in text:
            self.alphabet_stats[character] = self.alphabet_stats.get(character, 0) + 1
        self.huffman_tree = self._build_huffman_tree(self.alphabet_stats)
        self.encoding_dictionary = self.huffman_tree.get_dictionary()
        self.initialized = True

    def get_encoding_dictionary(self) -> dict:
        return self.encoding_dictionary
    
    def get_entropy(self) -> float:
        total_chars = sum(self.alphabet_stats.values())
        entropy = sum(-(v / total_chars) * math.log2(v / total_chars) for v in self.alphabet_stats.values())
        return entropy
    
    def encode(self, text: bytes) -> str:
        encoded_text = "".join(self.encoding_dictionary[character] for character in text)
        return encoded_text

    def decode(self, encoded_text: str):
        current_tree = self.huffman_tree
        text = bytearray()
        for character in encoded_text:
            assert (current_tree is not None)
            if character == "0":
                current_tree = current_tree.left
            elif character == "1":
                current_tree = current_tree.right
            else:
                raise ValueError("Encoded text can be only 1s and 0s")
            assert (current_tree is not None)
            if current_tree.label is not None:
                text.append(current_tree.label)
                current_tree = self.huffman_tree
        return text
