"""Text normalization, phrase extraction, comparison, and benchmarking."""
from __future__ import annotations
import re
import statistics
import time
from collections import Counter
from .algorithms import ALGORITHMS

WORD_RE = re.compile(r"\b[\w’'-]+\b", re.UNICODE)


def tokenize(text: str) -> list[str]:
    return [m.group(0).casefold() for m in WORD_RE.finditer(text)]


def find_shared_phrases(text_a: str, text_b: str, min_words: int = 3, max_phrases: int = 100):
    """Find maximal exact contiguous normalized word runs shared by both documents.

    Locations are one-based line/column positions in original text (character columns).
    Phrases are deduplicated by normalized content; first occurrence on each side is shown.
    """
    tokens_a, tokens_b = tokenize(text_a), tokenize(text_b)
    # Find matching runs in O(n*m) time with a rolling DP row. A run is reported
    # only when neither document has the same token immediately before it.
    prior = [0] * (len(tokens_b) + 1)
    maximal = set()
    for i, token in enumerate(tokens_a):
        current = [0] * (len(tokens_b) + 1)
        for j, other in enumerate(tokens_b):
            if token == other:
                current[j + 1] = prior[j] + 1
                length = current[j + 1]
                if length >= min_words:
                    start_a, start_b = i - length + 1, j - length + 1
                    left_maximal = start_a == 0 or start_b == 0 or tokens_a[start_a - 1] != tokens_b[start_b - 1]
                    right_maximal = i + 1 == len(tokens_a) or j + 1 == len(tokens_b) or tokens_a[i + 1] != tokens_b[j + 1]
                    if left_maximal and right_maximal:
                        maximal.add(tuple(tokens_a[start_a:i + 1]))
        prior = current
    maximal = sorted(maximal, key=lambda s: (-len(s), s))
    # Position lookup via normalized token boundaries.
    def occurrences(text, wanted):
        matches = []
        spans = [(m.group(0).casefold(), m.start(), m.end()) for m in WORD_RE.finditer(text)]
        for i in range(len(spans) - len(wanted) + 1):
            if tuple(x[0] for x in spans[i:i+len(wanted)]) == wanted:
                matches.append(spans[i][1])
        return matches
    rows = []
    for seq in maximal[:max_phrases]:
        starts_a, starts_b = occurrences(text_a, seq), occurrences(text_b, seq)
        if starts_a and starts_b:
            rows.append({"phrase": " ".join(seq), "word_count": len(seq),
                         "doc_a_offset": starts_a[0], "doc_b_offset": starts_b[0],
                         "doc_a_occurrences": len(starts_a), "doc_b_occurrences": len(starts_b)})
    return rows


def location(text: str, offset: int) -> str:
    line = text.count("\n", 0, offset) + 1
    last_newline = text.rfind("\n", 0, offset)
    return f"Line {line}, column {offset - last_newline}"


def similarity(text_a: str, text_b: str) -> dict:
    """Unique normalized-word Jaccard similarity and directional coverage percentages."""
    a, b = set(tokenize(text_a)), set(tokenize(text_b))
    intersection, union = len(a & b), len(a | b)
    return {"jaccard": 100 * intersection / union if union else 100.0,
            "a_coverage": 100 * intersection / len(a) if a else 0.0,
            "b_coverage": 100 * intersection / len(b) if b else 0.0,
            "shared_unique_words": intersection, "unique_words_a": len(a), "unique_words_b": len(b)}


def benchmark(text: str, patterns: list[str], repeats: int = 3) -> list[dict]:
    """Measure isolated matching calls; report median wall-clock time in milliseconds."""
    rows = []
    for label, fn in ALGORITHMS.items():
        durations, count = [], 0
        for _ in range(max(1, repeats)):
            start = time.perf_counter()
            count = sum(len(fn(text, pattern)) for pattern in patterns)
            durations.append((time.perf_counter() - start) * 1000)
        rows.append({"Algorithm": label, "Median time (ms)": statistics.median(durations), "Matches": count})
    return rows


def benchmark_scaling(text: str, repeats: int = 3) -> list[dict]:
    """Compare matcher times across increasing document and pattern lengths.

    Uses up to 20k characters from the submitted document, repeated to make
    1x/2x/4x inputs. Patterns are distinct leading word sequences at 2/4/8 words.
    """
    tokens = tokenize(text[:20_000])
    if len(tokens) < 8:
        return []
    # Controlled normalized corpus keeps token separators consistent and places
    # each pattern near the end of the base copy to require a full scan.
    base_text = " ".join(tokens)
    rows = []
    for word_count in (2, 4, 8):
        pattern = " ".join(tokens[-word_count:])
        for size in (1, 2, 4):
            corpus = (base_text + " ") * size
            for name, fn in ALGORITHMS.items():
                timings = []
                for _ in range(max(1, repeats)):
                    start = time.perf_counter()
                    fn(corpus.casefold(), pattern)
                    timings.append((time.perf_counter() - start) * 1000)
                rows.append({"Pattern length (words)": word_count,
                             "Document size (characters)": len(corpus),
                             "Algorithm": name,
                             "Median time (ms)": statistics.median(timings)})
    return rows
