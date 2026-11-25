# TextMatch: Plagiarism Detection Using String Matching Algorithms

## Abstract

TextMatch is a Python application that compares two text documents using Naïve Pattern Matching, Rabin–Karp, and Knuth–Morris–Pratt (KMP), implemented directly without a plagiarism detection library. It displays shared contiguous phrases and their locations, a reproducible definition of vocabulary overlap, and measured execution times. The system is intended as an educational demonstration of string matching and similarity analysis. Its output indicates textual overlap only and is not proof of plagiarism.

## Problem statement

Given two text documents, identify matching words or patterns. Implement Naïve, Rabin–Karp, and KMP algorithms and compare their execution time with attention to pattern length and document size.

## Objectives

1. Implement three classical exact string matching algorithms from scratch.
2. Compare two user-provided text documents and report common phrases with locations.
3. Calculate a clear, interpretable similarity metric.
4. Measure algorithm runtimes on common patterns and visualize comparisons.
5. Provide a runnable interface and tests that support demonstration and review.

## Methodology

Input is decoded as UTF-8. For phrase extraction, Unicode-aware word tokens are case-folded; punctuation is treated as a separator. A rolling-row dynamic program identifies maximal common contiguous token runs above the selected phrase length. The original character offsets are retained and converted to one-based line and column positions.

For the matcher demonstration, each extracted phrase is searched in both original texts after case-folding with each selected algorithm. Naïve checks every possible offset. Rabin–Karp updates a polynomial hash for each sliding window and verifies candidate matches character by character. KMP builds a prefix table and uses it to preserve the longest viable partial match after a mismatch.

Similarity is Jaccard overlap of unique normalized words: `100 × shared unique words / union of unique words`. Directional coverage divides shared unique words by each document's unique-word count. This metric is about vocabulary overlap and does not infer copying or intent.

Runtime is measured with a high-resolution monotonic timer and summarized as the median of repeated batches. The same patterns and document input are used for each matcher within a run.

## Complexity analysis

For text length `n` and pattern length `m`, Naïve takes O(nm) worst-case time and O(1) auxiliary space. Rabin–Karp takes O(n+m) expected time, but O(nm) in the worst case if many windows collide, and O(1) rolling state beyond results. KMP preprocesses in O(m), searches in O(n), and stores O(m) prefix data. The phrase-extraction DP takes O(NM) time for token counts N and M and O(M) working memory.

## Results and discussion

The sample scaling run below uses five repetitions on Python 3.9.6 / macOS 27.2 Apple Silicon. The base normalized sample corpus is 342 characters and is repeated to produce larger inputs; measurements are milliseconds and will vary across machines. The interface produces the full 2/4/8-word pattern-length chart for each run. Small inputs may be dominated by interpreter and timer overhead; asymptotic complexity predicts trends, not exact times.

| Document size | Pattern length (characters) | Algorithm | Median time (ms) | Matches |
|---|---:|---|---:|---:|
| 342 | 2 words | Naïve | 0.0214 | 1 |
| 342 | 2 words | Rabin–Karp | 0.0571 | 1 |
| 342 | 2 words | KMP | 0.0139 | 1 |
| 684 | 2 words | Naïve | 0.0450 | 2 |
| 684 | 2 words | Rabin–Karp | 0.1145 | 2 |
| 684 | 2 words | KMP | 0.0272 | 2 |
| 1,368 | 2 words | Naïve | 0.1024 | 4 |
| 1,368 | 2 words | Rabin–Karp | 0.2259 | 4 |
| 1,368 | 2 words | KMP | 0.0505 | 4 |

## Conclusion

TextMatch demonstrates three classical string matching approaches in a usable document-comparison interface. It makes matching spans and runtime comparisons visible and provides a clearly defined token-overlap score. The tool supports algorithm learning and preliminary review; it cannot identify the source of text, detect semantic paraphrases, or determine academic misconduct.

## Viva questions and short answers

**1. What is string matching?** Finding every occurrence of a pattern string inside a larger text string.

**2. Why does Naïve search take O(nm)?** It can compare up to m characters at each of roughly n possible start positions.

**3. What is the Rabin–Karp rolling hash?** A hash of the current length-m window that can be updated in constant time when sliding one character; candidates are verified because hashes can collide.

**4. How does KMP avoid repeated comparisons?** Its prefix table tells how far the pattern can shift while preserving a prefix that already matches the text suffix.

**5. What does KMP's prefix table contain?** For each pattern prefix, the length of its longest proper prefix that is also a suffix.

**6. Why keep overlapping matches?** A valid match may start before the previous match ends; KMP falls back using its prefix table to find these too.

**7. What does Jaccard similarity mean here?** The proportion of distinct normalized words shared relative to all distinct words across both documents.

**8. Why is this not proof of plagiarism?** Matching can come from common phrases, quotations, or coincidence, and the tool does not establish source, intent, or attribution.

**9. Why can measured times differ from complexity predictions?** Inputs may be too small, and interpreter overhead, content, hardware, and timer noise influence measurements.

**10. What are the main limitations?** Plain text only, exact token sequence matching, no paraphrase/translation detection, and no source attribution.

## Reproduction

Install dependencies with `python -m pip install -r requirements.txt`, launch using `streamlit run app.py`, and run checks using `python -m unittest discover -s tests -v`. Demonstration files are in `sample_docs/`.
