"""Unit tests for the FI9 reference implementation."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fi9 import FI9
import unittest


class TestFI9(unittest.TestCase):
    def setUp(self):
        self.e = FI9()

    def test_state_count(self):
        self.assertEqual(self.e.N_STATES, 512)

    def test_roundtrip_all_bytes(self):
        for b in range(256):
            state = self.e.encode_byte(b)
            recovered = self.e.decode_byte(state)
            self.assertEqual(recovered, b)

    def test_bijection(self):
        """Every state produces a unique matrix and can be recovered."""
        seen = set()
        for s in range(512):
            m = tuple(tuple(row) for row in self.e.matrix(s))
            self.assertNotIn(m, seen)
            seen.add(m)
            bits = self.e.state_to_bits(s)
            self.assertEqual(self.e.bits_to_state(bits), s)

    def test_text_roundtrip(self):
        msg = "The position of a point is the information."
        states = self.e.encode(msg)
        recovered = self.e.decode_str(states)
        self.assertEqual(recovered, msg)

    def test_empty(self):
        self.assertEqual(self.e.encode(b""), [])
        self.assertEqual(self.e.decode([]), b"")

    def test_protocol_region(self):
        self.assertTrue(self.e.is_protocol_state(256))
        self.assertTrue(self.e.is_protocol_state(511))
        self.assertFalse(self.e.is_protocol_state(255))
        self.assertEqual(self.e.protocol_state(0), 256)
        self.assertEqual(self.e.protocol_state(255), 511)

    def test_token_length(self):
        tok = self.e.make_token("ABC", length=32)
        self.assertEqual(len(tok), 32)
        self.assertEqual(tok[0], ord("A"))
        self.assertEqual(tok[1], ord("B"))
        self.assertEqual(tok[2], ord("C"))
        self.assertEqual(tok[3], 0)

    def test_graphical_hash_length(self):
        states = self.e.graphical_hash("test")
        self.assertEqual(len(states), 32)  # SHA-256 = 32 bytes

    def test_state_0_and_511(self):
        self.assertEqual(self.e.matrix(0), [[0,0,0],[0,0,0],[0,0,0]])
        self.assertEqual(self.e.matrix(511), [[1,1,1],[1,1,1],[1,1,1]])

    def test_native_fi_hash_deterministic(self):
        h1 = self.e.native_fi_hash("hello")
        h2 = self.e.native_fi_hash("hello")
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 32)
        for s in h1:
            self.assertTrue(0 <= s <= 511)

    def test_native_fi_hash_different_inputs(self):
        h1 = self.e.native_fi_hash("hello")
        h2 = self.e.native_fi_hash("hallo")
        self.assertNotEqual(h1, h2)

    def test_native_fi_hash_empty(self):
        h = self.e.native_fi_hash(b"")
        self.assertEqual(len(h), 32)

    def test_native_fi_hash_avalanche_simple(self):
        """Changing one character should change many output symbols."""
        h1 = self.e.native_fi_hash("The position of a point is the information.")
        h2 = self.e.native_fi_hash("The position of a point is the information!")
        diff = sum(1 for a, b in zip(h1, h2) if a != b)
        self.assertGreater(diff, 10)   # expect good diffusion


if __name__ == "__main__":
    unittest.main()
