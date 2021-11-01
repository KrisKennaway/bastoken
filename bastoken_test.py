import bastoken
import unittest


class TokenizerTests(unittest.TestCase):
    def test_canonicalize_case(self):
        t = bastoken.Tokenizer()
        self.assertEqual('A', t.canonicalize('a'))
        self.assertEqual('A', t.canonicalize('A'))
        self.assertEqual('1', t.canonicalize('1'))

    def test_read_token(self):
        t = bastoken.Tokenizer(allow_lower=True)
        self.assertEqual(([0x97], 4), t.read_token('HOME', 0))
        self.assertEqual(([ord('h')], 1), t.read_token('home', 0))

    def test_read_token_canonicalize(self):
        t = bastoken.Tokenizer(allow_lower=False)
        self.assertEqual(([0x97], 4), t.read_token('home', 0))

    def test_read_token_ambiguous(self):
        t = bastoken.Tokenizer()
        self.assertEqual(([0xc5], 2), t.read_token('AT', 0))
        self.assertEqual(([ord('A'), 0xc1], 3), t.read_token('ATO', 0))
        self.assertEqual(([0xe1], 3), t.read_token('ATN', 0))

    def test_read_token_ambiguous_canonicalize(self):
        t = bastoken.Tokenizer(allow_lower=False)
        self.assertEqual(([0xc5], 2), t.read_token('at', 0))
        self.assertEqual(([ord('A'), 0xc1], 3), t.read_token('ato', 0))
        self.assertEqual(([0xe1], 3), t.read_token('atn', 0))


if __name__ == '__main__':
    unittest.main()
