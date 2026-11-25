from __future__ import annotations
import html
from pathlib import Path
import pandas as pd
import streamlit as st
from plagiarism_checker.algorithms import ALGORITHMS
from plagiarism_checker.analysis import benchmark, benchmark_scaling, find_shared_phrases, location, similarity, tokenize

st.set_page_config(page_title="TextMatch | DAA Capstone", page_icon="🔎", layout="wide")
st.markdown("""<style>
.block-container{max-width:1200px;padding-top:2rem}.hero{padding:1.7rem 2rem;border-radius:18px;background:linear-gradient(120deg,#10233f,#234f78);color:#fff;margin-bottom:1rem}.hero h1{font-size:2.2rem;margin:0}.hero p{color:#d5e6f5;margin:.5rem 0 0}.small-note{color:#667085;font-size:.9rem}
</style><div class="hero"><h1>TextMatch</h1><p>String matching based similarity analysis · DAA Capstone Project 6</p></div>""", unsafe_allow_html=True)
st.caption("Compare two text documents using three from-scratch exact pattern matching algorithms. Results show textual overlap, not intent or proof of plagiarism.")

with st.sidebar:
    st.header("Analysis settings")
    min_words = st.slider("Minimum phrase length (words)", 2, 12, 3)
    algo_name = st.selectbox("Algorithm for phrase search", list(ALGORITHMS))
    repeats = st.slider("Benchmark repetitions", 1, 9, 3, 2)
    st.divider()
    st.markdown("**Similarity metric**\n\nJaccard similarity of unique, case-folded words: shared vocabulary ÷ combined vocabulary.")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Document A")
    up_a = st.file_uploader("Upload .txt", type=["txt"], key="a")
    text_a = up_a.getvalue().decode("utf-8", errors="replace") if up_a else st.text_area("Or paste text", height=210, key="ta", placeholder="Paste the first document here…")
with col2:
    st.subheader("Document B")
    up_b = st.file_uploader("Upload .txt", type=["txt"], key="b")
    text_b = up_b.getvalue().decode("utf-8", errors="replace") if up_b else st.text_area("Or paste text", height=210, key="tb", placeholder="Paste the second document here…")

if st.button("Compare documents", type="primary", use_container_width=True):
    if not text_a.strip() or not text_b.strip():
        st.warning("Add text to both document fields before comparing.")
    else:
        with st.spinner("Comparing documents…"):
            started_patterns = []
            # The phrase finder identifies common runs. Run the selected algorithm
            # against each phrase on both documents to demonstrate the chosen matcher.
            phrases = find_shared_phrases(text_a, text_b, min_words=min_words)
            fn = ALGORITHMS[algo_name]
            normalized_a = " ".join(tokenize(text_a))
            normalized_b = " ".join(tokenize(text_b))
            for row in phrases:
                pattern = row["phrase"]
                row["doc_a_location"] = location(text_a, row["doc_a_offset"])
                row["doc_b_location"] = location(text_b, row["doc_b_offset"])
                row["matcher_occurrences_a"] = len(fn(normalized_a, pattern))
                row["matcher_occurrences_b"] = len(fn(normalized_b, pattern))
                started_patterns.append(pattern)
            scores = similarity(text_a, text_b)
            # Include common words as benchmark patterns if no phrase meets the threshold.
            if not started_patterns:
                common = sorted(set(tokenize(text_a)) & set(tokenize(text_b)))
                started_patterns = common[:20] or ["__no_shared_pattern__"]
            timings = benchmark(normalized_a, started_patterns, repeats=repeats)
            scaling = benchmark_scaling(text_a, repeats=repeats)
        st.session_state["result"] = (text_a, text_b, phrases, scores, timings, scaling, algo_name)

if "result" in st.session_state:
    a, b, phrases, scores, timings, scaling, chosen = st.session_state["result"]
    st.divider()
    st.header("Comparison results")
    metrics = st.columns(4)
    metrics[0].metric("Jaccard similarity", f"{scores['jaccard']:.1f}%")
    metrics[1].metric("Shared unique words", scores["shared_unique_words"])
    metrics[2].metric("Document A covered", f"{scores['a_coverage']:.1f}%")
    metrics[3].metric("Document B covered", f"{scores['b_coverage']:.1f}%")
    st.caption(f"Jaccard uses unique normalized words: {scores['shared_unique_words']} shared ÷ {scores['unique_words_a'] + scores['unique_words_b'] - scores['shared_unique_words']} total unique words. It does not measure authorship or establish misconduct.")
    st.subheader(f"Matching phrases ({len(phrases)})")
    if phrases:
        df = pd.DataFrame(phrases).rename(columns={"phrase":"Matched phrase", "word_count":"Words", "doc_a_location":"Document A location", "doc_b_location":"Document B location", "doc_a_occurrences":"A occurrences", "doc_b_occurrences":"B occurrences", "matcher_occurrences_a":"A matcher hits", "matcher_occurrences_b":"B matcher hits"})
        st.dataframe(df[["Matched phrase","Words","Document A location","Document B location","A occurrences","B occurrences","A matcher hits","B matcher hits"]], width="stretch", hide_index=True)
        st.download_button("Download phrase results (CSV)", df.to_csv(index=False).encode(), "textmatch_results.csv", "text/csv")
        phrase = phrases[0]["phrase"]
        st.markdown("**Longest matched phrase preview**")
        st.code(phrase)
    else:
        st.info("No shared contiguous phrase met the selected minimum length. Vocabulary overlap can still appear in the similarity metric.")
    st.subheader("Algorithm performance")
    bench_df = pd.DataFrame(timings)
    st.caption(f"Pattern search on normalized Document A · {len(' '.join(tokenize(a))):,} characters · {len(phrases) if phrases else 1} patterns")
    st.bar_chart(bench_df.set_index("Algorithm")[["Median time (ms)"]], y_label="Median execution time (ms)")
    st.dataframe(bench_df, width="stretch", hide_index=True)
    st.caption("Timing covers repeated exact pattern searches on Document A; medians reduce noise. The run uses the same phrase patterns for each algorithm. For meaningful scaling analysis, vary both document size and pattern length.")
    st.download_button("Download benchmark (CSV)", bench_df.to_csv(index=False).encode(), "textmatch_benchmark.csv", "text/csv")
    st.markdown("**Scaling comparison: document size × pattern length**")
    if scaling:
        scale_df = pd.DataFrame(scaling)
        for pattern_words in (2, 4, 8):
            part = scale_df[scale_df["Pattern length (words)"] == pattern_words]
            chart = part.pivot(index="Document size (characters)", columns="Algorithm", values="Median time (ms)")
            st.caption(f"Pattern length: {pattern_words} words · normalized, controlled benchmark corpus")
            st.line_chart(chart, y_label="Median time (ms)")
        st.download_button("Download scaling benchmark (CSV)", scale_df.to_csv(index=False).encode(), "textmatch_scaling.csv", "text/csv")
    else:
        st.info("Scaling charts need at least eight words in Document A.")

with st.expander("How to interpret this analysis"):
    st.markdown("""- **Naïve:** checks each possible starting position directly; worst case O(nm) per pattern.
- **Rabin–Karp:** uses a rolling hash to find candidate windows, then verifies characters; expected O(n+m), worst case O(nm).
- **KMP:** preprocesses a prefix table and avoids rechecking matched characters; O(n+m) per pattern.
- **Locations:** one-based line and character column in the original uploaded text. Phrase matching is case-insensitive and token based; the algorithms themselves perform exact character matching.
- **Limitations:** paraphrases, translations, semantic similarity, citations, and source attribution are outside this tool's scope. Results require human review.""")
