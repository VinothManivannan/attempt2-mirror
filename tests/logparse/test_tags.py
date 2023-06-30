import unittest
from cmlpytools.logparse import LogTree


class TestTags(unittest.TestCase):
    def test_simple_tag_present(self):
        """
        This test checks that a standard tag <major>.<minor>.<patch> can be found in the release notes.
        """
        original = "# 1.2.3 \n- Example change\n"

        log_tree = LogTree(original)

        self.assertEqual(True, log_tree.has_release("1.2.3"))

    def test_simple_tag_present_no_patch(self):
        """
        This test checks that a standard tag <major>.<minor> can be found in the release notes.
        """
        original = "# v2.3 \n- Example change\n"

        log_tree = LogTree(original)

        self.assertEqual(True, log_tree.has_release("2.3"))


if __name__ == '__main__':
    unittest.main()
