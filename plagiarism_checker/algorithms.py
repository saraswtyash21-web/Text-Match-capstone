"""From-scratch exact string matching algorithms with Python character offsets."""
from __future__ import annotations


def naive_search(text: str, pattern: str) -> list[int]:
    """Return all (including overlapping) start offsets using direct comparison."""
    if not pattern:
        return list(range(len(text) + 1))
    return [i for i in range(len(text) - len(pattern) + 1)
            if text[i:i + len(pattern)] == pattern]


def rabin_karp_search(text: str, pattern: str, *, base: int = 256, mod: int = 1_000_000_007) -> list[int]:
    """Return exact matches; rolling hash candidates are verified to avoid collisions."""
    n, m = len(text), len(pattern)
    if m == 0:
        return list(range(n + 1))
    if m > n:
        return []
    high = pow(base, m - 1, mod)
    target = window = 0
    for i in range(m):
        target = (target * base + ord(pattern[i])) % mod
        window = (window * base + ord(text[i])) % mod
    found = []
    for start in range(n - m + 1):
        if window == target and text[start:start + m] == pattern:
            found.append(start)
        if start < n - m:
            window = ((window - ord(text[start]) * high) * base + ord(text[start + m])) % mod
    return found


def _prefix_function(pattern: str) -> list[int]:
    pi = [0] * len(pattern)
    j = 0
    for i in range(1, len(pattern)):
        while j and pattern[i] != pattern[j]:
            j = pi[j - 1]
        if pattern[i] == pattern[j]:
            j += 1
            pi[i] = j
    return pi


def kmp_search(text: str, pattern: str) -> list[int]:
    """Return all (including overlapping) offsets using KMP prefix fallback."""
    if not pattern:
        return list(range(len(text) + 1))
    pi = _prefix_function(pattern)
    found, j = [], 0
    for i, char in enumerate(text):
        while j and char != pattern[j]:
            j = pi[j - 1]
        if char == pattern[j]:
            j += 1
            if j == len(pattern):
                found.append(i - len(pattern) + 1)
                j = pi[j - 1]
    return found


ALGORITHMS = {
    "Naïve": naive_search,
    "Rabin–Karp": rabin_karp_search,
    "KMP": kmp_search,
}
