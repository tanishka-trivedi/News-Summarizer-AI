"""
News Summarizer - Core NLP Logic
----------------------------------
This module contains the extractive (TF-IDF based) summarizer and the
optional abstractive (transformer based) summarizer, along with the
URL article-extraction helper.

This is a cleaned-up / bug-fixed version of the original notebook logic:
- Fixed `remove_redundancy` (undefined variable `top_indices`, `true/False`
  typos, and comparing a sentence index against a TF-IDF matrix row).
- Fixed `chunk_text` typo (`raange` -> `range`).
- Added proper input validation / guard clauses so the Flask API never
  crashes on empty or junk input.
- The HuggingFace abstractive pipeline is now lazy-loaded (only created the
  first time it's actually requested) so the app starts up fast and works
  even on machines without the model already downloaded.
"""

import re
import numpy as np
import nltk
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------------------------------------------------
# One-time NLTK data setup
# ---------------------------------------------------------------------------
# def _ensure_nltk_data():
#     for pkg in ("punkt", "punkt_tab"):
#         try:
#             nltk.data.find(f"tokenizers/{pkg}")
#         except LookupError:
#             nltk.download(pkg, quiet=True)

def _ensure_nltk_data():
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt", quiet=True)


_ensure_nltk_data()


# ---------------------------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------------------------
def clean(sentence: str) -> str:
    """Lowercase and strip everything that isn't a letter or whitespace."""
    sentence = sentence.lower()
    # sentence = re.sub(r"[^a-zA-Z\s]", "", sentence)
    sentence = re.sub(r"[^a-zA-Z0-9\s]", "", sentence)
    return sentence


def filter_sentences(sentences):
    """Drop very short sentences, links, and mentions before scoring."""
    filtered = []
    for s in sentences:
        words = s.split()
        if len(words) < 6:
            continue
        if "http" in s or "@" in s:
            continue
        filtered.append(s)
    return filtered


def remove_redundancy(sentences, tfidf_mat, top_ind, threshold=0.7):
    """
    Drop sentences that are highly similar (cosine similarity > threshold)
    to a sentence already selected, keeping the higher-ranked one.

    Fixed version of the original buggy function:
    - uses `top_ind` (the function argument) instead of an undefined
      `top_indices` global.
    - uses proper Python booleans (`True`/`False`) instead of `true`.
    - compares actual TF-IDF row vectors instead of a row vs. an index.
    """
    selected = []
    for idx in sorted(top_ind, reverse=True):
        keep = True
        for s_idx in selected:
            sim = cosine_similarity(tfidf_mat[idx], tfidf_mat[s_idx])[0][0]
            if sim > threshold:
                keep = False
                break
        if keep:
            selected.append(idx)
    return sorted(selected)


# ---------------------------------------------------------------------------
# Extractive summarizer (TF-IDF)
# ---------------------------------------------------------------------------
def summarize_extractive(text: str, num: int = 3, dedupe: bool = True) -> str:
    """
    Pipeline: clean -> tokenize -> vectorize -> score -> rank -> dedupe ->
    reconstruct summary in original sentence order.
    """
    if not text or not text.strip():
        return "Please provide some text to summarize."

    sentences = sent_tokenize(text)
    sentences = filter_sentences(sentences)

    if len(sentences) == 0:
        return "No valid content to summarize."

    if len(sentences) <= num:
        # Not enough sentences to summarize meaningfully - return as is.
        return " ".join(sentences)

    cleaned_sent = [clean(s) for s in sentences]

    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf_mat = vectorizer.fit_transform(cleaned_sent)
    except ValueError:
        return "Unable to compute meaningful summary."

    sent_score = np.asarray(tfidf_mat.sum(axis=1)).flatten()

    if np.max(sent_score) == 0:
        return "Unable to compute meaningful summary."

    max_score = np.max(sent_score)

    if max_score > 0:
        sent_score /= max_score # normalize

    # Reward longer, information-dense sentences slightly
    for i in range(len(sent_score)):
        sent_score[i] *= len(sentences[i].split())

    # Take a slightly larger candidate pool so de-duplication has room to work
    pool_size = min(len(sentences), num * 2)
    top_ind = np.argsort(sent_score)[-pool_size:]

    if dedupe:
        top_ind = remove_redundancy(sentences, tfidf_mat, top_ind, threshold=0.7)

    # Trim back down to the requested number of sentences, keeping the
    # highest scoring ones first, then restore original order.
    top_ind = sorted(top_ind, key=lambda i: sent_score[i], reverse=True)[:num]
    top_ind = sorted(top_ind)

    summary = " ".join([sentences[i] for i in top_ind])
    return summary


# ---------------------------------------------------------------------------
# URL article extraction
# ---------------------------------------------------------------------------
def get_article_text(url: str) -> str:
    """Download and parse an article's main text content from a URL."""
    from newspaper import Article  # imported lazily - optional dependency

    article = Article(url)
    article.download()
    article.parse()
    return article.text


# ---------------------------------------------------------------------------
# Abstractive summarizer (Transformers) - lazy loaded, optional
# ---------------------------------------------------------------------------
_abstractive_pipeline = None


def _get_abstractive_pipeline():
    global _abstractive_pipeline
    if _abstractive_pipeline is None:
        from transformers import pipeline
        _abstractive_pipeline = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    return _abstractive_pipeline


def chunk_text(text: str, max_words: int = 400):
    """Split long text into word-count-limited chunks for the transformer."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):  # fixed: was `raange`
        chunk = " ".join(words[i:i + max_words])
        chunks.append(chunk)
    return chunks


def summarize_abstractive(text: str) -> str:
    """Abstractive summary using a HuggingFace transformer pipeline."""
    if not text or not text.strip():
        return "Please provide some text to summarize."

    model = _get_abstractive_pipeline()
    chunks = chunk_text(text)
    summaries = []

    for chunk in chunks:
        word_count = len(chunk.split())
        if word_count < 10:
            continue
        max_len = min(120, max(30, word_count // 2))
        result = model(chunk, max_length=max_len, min_length=min(20, max_len - 5), do_sample=False)
        summaries.append(result[0]["summary_text"])

    return " ".join(summaries) if summaries else "Unable to generate a summary."
