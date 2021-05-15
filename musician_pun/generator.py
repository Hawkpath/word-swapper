import random
from typing import List, Optional, Tuple, TypeVar, cast

import gensim.downloader as gensim_api
from gensim.models.keyedvectors import Word2VecKeyedVectors
from nltk import word_tokenize
from nltk.corpus import words as corpus_words
from nltk.tokenize import LegalitySyllableTokenizer

__all__ = (
    'make_pun',
)

V = TypeVar('V')

model: Word2VecKeyedVectors = gensim_api.load("glove-twitter-25")


class SubwordFinder:
    """Find subwords within an existing word"""

    __tokenizer = LegalitySyllableTokenizer(corpus_words.words())

    def __init__(self, word: str):
        self.word = word
        self.syllables: List[str] = self.__tokenizer.tokenize(word)
        self._generate_splits()

    def _generate_splits(self):
        sylls = self.syllables
        self.subwords = []
        for win_len in range(len(sylls), 0, -1):
            for offset in range(len(sylls) - win_len + 1):
                subword = ''.join(sylls[offset:offset+win_len]).lower()
                if subword not in model:
                    continue
                self.subwords.append((
                    sylls[:offset], subword, sylls[offset+win_len:]
                ))

    def __len__(self):
        return len(self.subwords)

    def __iter__(self):
        return iter(self.subwords)

    def __getitem__(self, index: int):
        return self.subwords[index]


def make_pun(text: str, similar_count=10) -> Optional[str]:
    text = text.replace('-', ' ')
    words = [SubwordFinder(w) for w in word_tokenize(text)]

    out = [w.word for w in words]

    splitted = [w for w in words if w.subwords]
    if not splitted:
        return
    # Get a random splittable word
    i, subfinder = random.choice(list(enumerate(splitted)))
    subfinder = cast(SubwordFinder, subfinder)

    # Get a random subword
    subword_start, subword, subword_end = random.choice(subfinder.subwords)

    # Get a list of similar words from the model
    similars: List[Tuple[str, float]] = model.most_similar(
        positive=subword, topn=similar_count
    )
    # Pick a random similar word using their weights
    changed = random.choices(
        population=[i[0] for i in similars],
        weights=[i[1] for i in similars],
        k=1
    )[0]
    # Join the splits of this word together with the random similar word
    changed = ''.join(subword_start + [changed] + subword_end)

    out[i] = changed
    return ' '.join(out)
