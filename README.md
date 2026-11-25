# TextMatch — DAA Capstone Project 6

A Streamlit application for comparing two text documents with **from-scratch Naïve, Rabin–Karp, and Knuth–Morris–Pratt (KMP) string matching**. It reports matching contiguous phrases and their locations, a defined word-overlap metric, and measured algorithm runtimes.

> This is string-matching-based similarity analysis. It does not determine intent, detect AI writing, establish authorship, or prove plagiarism. All findings need human review.

## Features

- Upload two UTF-8 `.txt` files or paste text.
- Find exact contiguous shared word phrases (case-insensitive), with original document line and column locations.
- Select the string matcher used for counting exact pattern occurrences.
- Calculate Jaccard similarity over unique, case-folded words, plus directional vocabulary coverage.
- Compare median runtime for three algorithms; download phrase and timing tables as CSV.
- Small sample documents, independent algorithm tests, and viva/report notes.

## Run locally

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit. Upload `.txt` files, or paste content into each document panel. Use the sidebar to change minimum phrase length, selected matcher, and benchmark repetitions. Click **Compare documents**. Try `sample_docs/document_a.txt` and `sample_docs/document_b.txt`.

Run the tests with `python -m unittest discover -s tests -v` (standard library), or `python -m pytest -q` after installing the listed development dependency.

## Project layout

```text
app.py                      Streamlit interface
plagiarism_checker/
  algorithms.py              Naïve, Rabin–Karp, and KMP implementations
  analysis.py                phrase extraction, similarity, and timing
sample_docs/                 demonstration inputs
tests/                       algorithm and analysis tests
report/                      submission-ready report material
requirements.txt             application dependencies
```

## Metric definition

Text is split into word tokens with Unicode-aware tokenization; tokens are case-folded. Punctuation is ignored for phrase matching. Let A and B be the sets of unique normalized words in each document:

`Jaccard similarity = 100 × |A ∩ B| / |A ∪ B|`

Directional coverage is `100 × |A ∩ B| / |A|` for A and correspondingly for B. If both documents have no tokens, Jaccard is 100%; if only one side is empty, it is 0%. This is a transparent vocabulary overlap score, not a probability of plagiarism. Shared phrases are maximal contiguous token runs of at least the chosen word count.

## Algorithms and complexity

The implementation searches Python strings and returns zero-based character offsets (the UI converts these to one-based line and character column). Empty patterns match at every boundary; overlapping matches are retained.

| Algorithm | Main idea | Preprocessing | Search time | Extra space |
|---|---|---:|---:|---:|
| Naïve | Compare pattern at every possible text offset | O(1) | O(nm) worst case | O(1) excluding results |
| Rabin–Karp | Rolling polynomial hash, then verify candidate windows | O(m) | O(n+m) expected; O(nm) worst case with collisions | O(1) excluding results |
| KMP | Prefix/failure table shifts pattern without rechecking known characters | O(m) | O(n) | O(m) |

Here `n` is document character count and `m` is pattern character count. Rabin–Karp verifies candidate windows, so hash collisions cannot create false matches. The phrase-finding analysis uses a rolling-row dynamic program on token sequences and is separate from the three character-level matchers being benchmarked.

## Benchmark interpretation

The interface times exact searches over the normalized token stream from Document A with `time.perf_counter` and reports medians across repeated runs. The direct comparison uses extracted patterns. The scaling view uses a controlled normalized version of up to 20,000 source characters from Document A, repeated to 1×/2×/4× size, with 2/4/8-word patterns. Results depend on machine, Python version, content, and timer noise. Do not treat a small-input ranking as a universal speed claim.

#

## Limitations

Only plain text is accepted; convert PDFs/Word files to text before upload. Formatting and layout are discarded. Exact phrase matching misses paraphrases and translated text. Common or boilerplate phrases can produce overlap. The application gives no source attribution and does not replace instructor review.
