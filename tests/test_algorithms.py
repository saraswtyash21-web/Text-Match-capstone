import unittest
from plagiarism_checker.algorithms import naive_search, rabin_karp_search, kmp_search
from plagiarism_checker.analysis import find_shared_phrases, location, similarity


class StringMatchingTests(unittest.TestCase):
    def test_algorithms_overlapping_and_multiple(self):
        expected = [0, 2]
        for search in (naive_search, rabin_karp_search, kmp_search):
            with self.subTest(algorithm=search.__name__):
                self.assertEqual(search("ababa", "aba"), expected)

    def test_algorithms_edge_cases_and_unicode(self):
        for search in (naive_search, rabin_karp_search, kmp_search):
            with self.subTest(algorithm=search.__name__):
                self.assertEqual(search("abc", ""), [0, 1, 2, 3])
                self.assertEqual(search("ab", "long"), [])
                self.assertEqual(search("café café", "café"), [0, 5])

    def test_rabin_karp_collision_is_verified(self):
        self.assertEqual(rabin_karp_search("abcdefgh", "xyz", base=2, mod=3), [])

    def test_similarity_definition(self):
        result = similarity("Cat dog cat", "dog bird")
        self.assertEqual(result["shared_unique_words"], 1)
        self.assertAlmostEqual(result["jaccard"], 100 / 3)
        self.assertEqual(result["a_coverage"], 50)
        self.assertEqual(result["b_coverage"], 50)

    def test_shared_phrase_locations_and_casefolding(self):
        a, b = "First line. Shared phrase here today.", "Other\nshared PHRASE here today!"
        result = find_shared_phrases(a, b, min_words=3)
        self.assertEqual(result[0]["phrase"], "shared phrase here today")
        self.assertEqual(location(a, result[0]["doc_a_offset"]), "Line 1, column 13")
        self.assertEqual(location(b, result[0]["doc_b_offset"]), "Line 2, column 1")


if __name__ == "__main__":
    unittest.main()
