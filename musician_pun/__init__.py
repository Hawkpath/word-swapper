import random
from typing import Annotated as A, Set, Tuple, TypeVar

from nltk import word_tokenize
from nltk.corpus import wordnet, words as corpus_words
from nltk.tokenize import LegalitySyllableTokenizer

V = TypeVar('V')


class DerivativeWord:

    __tokenizer = LegalitySyllableTokenizer(corpus_words.words())

    def __init__(self, word: str):
        self.word = word
        self.syllables = self.__tokenizer.tokenize(word)
        self._generate_derivatives()

    def _generate_derivatives(self):
        sylls = self.syllables
        self.derivatives = []
        for win_len in range(len(sylls), 0, -1):
            for offset in range(len(sylls) - win_len + 1):
                subword = ''.join(sylls[offset:offset+win_len])
                _, antonyms = self.thesaurize(subword)
                for antonym in antonyms:
                    self.derivatives.append(''.join((
                        sylls[:offset] + [antonym] + sylls[offset+win_len:]
                    )))

    def __len__(self):
        return len(self.derivatives)

    def __iter__(self):
        return iter(self.derivatives)

    def __getitem__(self, index: int):
        return self.derivatives[index]

    @staticmethod
    def thesaurize(
            word: str
    ) -> Tuple[A[Set[str], 'synonyms'], A[Set[str], 'antonyms']]:
        synonyms = []
        antonyms = []

        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonyms.append(lemma.name())
                if lemma.antonyms():
                    antonyms.append(lemma.antonyms()[0].name())

        return set(synonyms), set(antonyms)


def make_pun(text: str):
    text = text.replace('-', ' ')
    words = []
    derivatives_count = 0
    for word in word_tokenize(text):
        derivative = DerivativeWord(word)
        words.append(derivative)
        derivatives_count += len(derivative)

    if derivatives_count:
        choice = random.randint(0, derivatives_count-1)
    else:
        choice = 0
    out = []
    for word in words:
        try:
            out.append(word[choice])
            choice = None
        except (IndexError, TypeError):
            out.append(word.word)
            if choice is not None:
                choice -= len(word)

    return ' '.join(out)


a = make_pun('Third Eye Blind')
pass
