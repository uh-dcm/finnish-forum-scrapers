import threading
from difflib import SequenceMatcher

_SPACY_LOCK = threading.Lock()
_SPACY_MODEL = None

_CLITICS = ("kaan", "kään", "kin", "ko", "kö", "pa", "pä", "han", "hän",
            "nsa", "nsä", "mme", "nne", "ni", "si")
_FUZZY_THRESHOLD = 0.8


def _get_spacy_model():
    global _SPACY_MODEL
    if _SPACY_MODEL is None:
        with _SPACY_LOCK:
            if _SPACY_MODEL is None:
                import spacy

                _SPACY_MODEL = spacy.load("fi_core_news_sm")
    return _SPACY_MODEL


def _strip_clitic(word):
    for clitic in _CLITICS:
        if len(word) > len(clitic) + 3 and word.endswith(clitic):
            return word[: -len(clitic)]
    return word


def _lemmatize_word(nlp, word):
    word = word.lower()
    lemma = nlp(word)[0].lemma_
    if lemma != word:
        return lemma
    stripped = _strip_clitic(word)
    if stripped != word:
        lemma = nlp(stripped)[0].lemma_
        if lemma != stripped:
            return lemma
    return lemma


def lemmatize(text, keep_stopwords=False):
    nlp = _get_spacy_model()
    doc = nlp(text)
    lemmas = set()
    for token in doc:
        if token.is_punct or token.is_space:
            continue
        if not keep_stopwords and token.is_stop:
            continue
        lemmas.add(_lemmatize_word(nlp, token.text))
    return lemmas


def matches(query, body):
    if query in body:
        return True
    query_lemmas = lemmatize(query)
    if not query_lemmas:
        return False
    body_lemmas = lemmatize(body)
    if query_lemmas.issubset(body_lemmas):
        return True
    return all(
        any(
            len(q) >= 4
            and SequenceMatcher(None, q, b).ratio() >= _FUZZY_THRESHOLD
            for b in body_lemmas
        )
        for q in query_lemmas
    )


def simple_matches(query, body):
    return query in body
