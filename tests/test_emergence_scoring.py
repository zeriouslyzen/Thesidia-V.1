import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


class TestEmergenceScoring(unittest.TestCase):
    def test_compression_score_basic(self):
        from src.metrics.emergence_scoring import score_compression

        pre = "a" * 200
        post = "a" * 100
        s = score_compression(pre, post)
        self.assertEqual(s.pre_chars, 200)
        self.assertEqual(s.post_chars, 100)
        self.assertGreater(s.score, 0.0)

    def test_compression_score_overcompressed(self):
        from src.metrics.emergence_scoring import score_compression

        pre = "a" * 500
        post = "a" * 50  # ratio 0.1
        s = score_compression(pre, post)
        self.assertEqual(s.score, 0.0)


if __name__ == "__main__":
    unittest.main()




