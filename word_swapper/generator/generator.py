import json
import logging
from pathlib import Path
import random
from string import punctuation
from typing import List, Optional, Set, Tuple, TypeVar

import gensim.downloader as gensim_api
from gensim.models.keyedvectors import Word2VecKeyedVectors
from nltk import word_tokenize
from nltk.corpus import words as corpus_words
from nltk.tokenize import LegalitySyllableTokenizer

__all__ = (
    'make_pun',
)

logger = logging.getLogger(__name__)

V = TypeVar('V')


def load_word_set(file_name: str) -> Set[str]:
    file = Path(__file__, '..', file_name)
    if file.exists():
        with file.open() as f:
            out = set(json.load(f))
        logger.info(f"Loaded {file_name} with {len(out)} words")
        return out

    logger.info(f"{file_name} does not exist, it will be ignored")
    return set()


ignored_words = load_word_set('ignored_words.json') | set(punctuation)
bad_words = load_word_set('bad_words.json')

logger.info('Loading language model')
model: Word2VecKeyedVectors = gensim_api.load("glove-wiki-gigaword-100")
logger.info('Language model successfully loaded')


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
                self.subwords = [([], word, [])]
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

    words_with_subwords = [(i, w) for i, w in enumerate(words) if w.subwords]
    if not words_with_subwords:
        return
    # Get a random splittable word
    random_word_idx, random_word = random.choice(words_with_subwords)

    # Get a random subword
    subword_start, subword, subword_end = random.choice(random_word.subwords)

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

    # Hopefully don't say anything super bad...
    if similar_subword.lower() in bad_words:
        logger.debug(f"Really bad word rejected: {similar_subword}")
        return (
            "I generated a really bad word but it was silenced by a "
            "bad words blacklist. I'm using a language model trained from "
            "Wikipedia articles, so it's possible more really bad words may "
            "be unaccounted for. I'm sorry if this happens, it's fully "
            "unintentional."
        )

    # Join the splits of this word together with the random similar word
    new_word = ''.join(subword_start + [similar_subword] + subword_end)

    out[random_word_idx] = new_word
    logger.debug(
        f"{''.join(subword_start)}[{subword}]{''.join(subword_end)} "
        f"{subword} -> {similar_subword}"
    )
    return ' '.join(out)
