import logging
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

logger = logging.getLogger('musician_pun.generator')

V = TypeVar('V')

logger.info('Loading language model')
model: Word2VecKeyedVectors = gensim_api.load("glove-wiki-gigaword-100")
logger.info('Language model successfully loaded')


ignored_words = {
    'the', 'a', 'an', 'in', 'on', 'and'
}


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
        if len(sylls) == 1:
            word = sylls[0].lower()
            if word in model and word not in ignored_words:
                self.subwords = [([], sylls[0], [])]
            return

        for window in range(len(sylls), 1, -1):
            for offset in range(len(sylls) - window + 1):
                subword = ''.join(sylls[offset:offset+window]).lower()
                if subword not in model or subword in ignored_words:
                    continue
                self.subwords.append((
                    sylls[:offset], subword, sylls[offset+window:]
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
    similar_subword = random.choices(
        population=[i[0] for i in similars],
        weights=[i[1] for i in similars],
        k=1
    )[0]
    # Join the splits of this word together with the random similar word
    new_word = ''.join(subword_start + [similar_subword] + subword_end)

    out[i] = new_word
    logger.debug(
        f"{''.join(subword_start)}[{subword}]{''.join(subword_end)} "
        f"{subword} -> {similar_subword}"
    )
    return ' '.join(out)
