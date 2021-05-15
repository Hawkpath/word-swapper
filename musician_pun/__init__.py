from collections.abc import MutableSequence
import random
from typing import Annotated as A, Generic, Optional, TypeVar

from nltk import word_tokenize
from nltk.corpus import words, wordnet
from nltk.tokenize import *

V = TypeVar('V')


class FlatJaggedArray(Generic[V]):

    def __init__(self, seq: MutableSequence[MutableSequence[V]]):
        self.seq = seq

    def __len__(self):
        count = 0
        for i in self.seq:
            count += len(i)
        return count

    def __getitem__(self, index: int) -> V:
        x = index
        for y_list in self.seq:
            try:
                return y_list[x]
            except IndexError:
                x -= len(y_list)
        raise IndexError(
            f"Flat index {index} out of bounds for jagged array with flat "
            f"length of {len(self)}"
        )

    def __setitem__(self, index: int, value: V):
        x = index
        for y_list in self.seq:
            try:
                y_list[x] = value
                return
            except IndexError:
                x -= len(y_list)
        raise IndexError(
            f"Flat index {index} out of bounds for jagged array with flat "
            f"length of {len(self)}"
        )


def tokenize(text: str):
    text_words = word_tokenize(text)
    # tokenizer = LegalitySyllableTokenizer(words.words())
    # tokenizer = TweetTokenizer()
    tokenizer = LegalitySyllableTokenizer()
    return [tokenizer.tokenize(word) for word in text_words]


def thesaurize(
        word: str
) -> tuple[A[set[str], 'synonyms'], A[set[str], 'antonyms']]:
    synonyms = []
    antonyms = []

    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.append(lemma.name())
            if lemma.antonyms():
                antonyms.append(lemma.antonyms()[0].name())

    return set(synonyms), set(antonyms)


def make_pun(text) -> Optional[str]:
    tokenized_words: list[list[str]] = tokenize(text)
    flat = FlatJaggedArray(tokenized_words)
    indices = list(range(len(flat)))
    random.shuffle(indices)
    for i in indices:
        synonyms, antonyms = thesaurize(flat[i])
        if not antonyms:
            continue
        replacement = random.choice(list(antonyms))
        flat[i] = replacement
        break
    else:
        return None

    return ' '.join(''.join(i) for i in tokenized_words)


pass
