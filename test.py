from StringIO import StringIO
from sanitycheck import sanity_check, Insane, MissingSection
import unittest


class TestSanityCheck(unittest.TestCase):

    def _make_buf(self, *lines):
        if not lines:
            lines = ['']
        buf = StringIO(buf='\n'.join(lines))
        buf.name = ''
        return buf

    def test_empty_buf_fails(self):
        self.assertRaises(MissingSection, sanity_check, self._make_buf(''))

    def test_empty_versions_fails(self):
        self.assertRaises(MissingSection,
                          sanity_check, self._make_buf('[versions]'))

    def test_package_with_dashes(self):
        buf = self._make_buf('[versions]',
                             'foo-bar = 1.1',
                             'qux-bar = 1.3')
        sanity_check(buf)

    def test_version_with_dashes(self):
        buf = self._make_buf('[versions]',
                             'foo = 1.1-1',
                             'foo = 1.1-2')
        self.assertRaises(Insane, sanity_check, buf)

    def test_version_with_text(self):
        buf = self._make_buf('[versions]',
                             'foo = 1.1-alpha',
                             'foo = 1.1-beta')
        self.assertRaises(Insane, sanity_check, buf)

    def test_package_with_underlines(self):
        buf = self._make_buf('[versions]',
                             'foo_bar = 1.1',
                             'qux_bar = 1.3')
        sanity_check(buf)

    def test_comments_ignored(self):
        buf = self._make_buf('[versions]',
                             '#foo',
                             '#foo = 1.1',
                             'foo = 1.3')
        sanity_check(buf)

    def test_duplicate_version_fails(self):
        buf = self._make_buf('[versions]',
                             'foo = 1.1',
                             'foo = 1.3')
        self.assertRaises(Insane, sanity_check, buf)

    def test_triple_version_fails(self):
        buf = self._make_buf('[versions]',
                             'foo = 1.1',
                             'foo = 1.3',
                             'foo = 1.4')
        self.assertRaises(Insane, sanity_check, buf)


if __name__ == '__main__':
    unittest.main()
