import unittest
from cmlpytools.logparse import LogTree


class TestFilterLabels(unittest.TestCase):
    def test_no_eol_at_eof(self):
        """
        This test checks the case where there is no EOL at the end of the file.
        """
        original = "# Release entry\n- Log entry with no eol"
        expected = "# Release entry\n- Log entry with no eol\n"

        log_tree = LogTree(original)

        self.assertEqual(expected, log_tree.render_as_string())

    def test_multiple_eol_at_eof(self):
        """
        This test checks the case where there are several EOL at the end of the file.
        """
        original = "# Release entry\n- Log entry with no eol\n\n\n"
        expected = "# Release entry\n- Log entry with no eol\n"

        log_tree = LogTree(original)

        self.assertEqual(expected, log_tree.render_as_string())

    def test_multiple_eol(self):
        """
        This test checks that if the user used too many EOL in the file, the file still gets parsed properly.
        """
        original = "\n\n# Release entry 1\n\n- Log entry\n\n- Log entry\n\n\n\n# Release entry 2\n\n- Log entry\n"
        expected = "# Release entry 1\n- Log entry\n- Log entry\n\n# Release entry 2\n- Log entry\n"

        log_tree = LogTree(original)

        self.assertEqual(expected, log_tree.render_as_string())

    def test_multiple_lines_entry(self):
        """
        This test checks that if the user uses a log entry over multiple lines, it gets parsed properly.
        """
        original = "- Log entry\n over \n multiple \n lines \n"
        expected = "- Log entry\n over \n multiple \n lines \n"

        log_tree = LogTree(original)

        self.assertEqual(1, len(log_tree.entries))
        self.assertEqual(expected, log_tree.render_as_string())

    def test_simple_text(self):
        """
        This test checks that if the user uses a simple text, it gets parsed properly.
        """
        original = "This is a simple text entry\n"
        expected = "This is a simple text entry\n"

        log_tree = LogTree(original)

        self.assertEqual(expected, log_tree.render_as_string())

    def test_list_multiple_levels(self):
        """
        This test checks that a multi-levels list get parsed as expected. Example:
        - This is a first level list item
          - This is a second level list item
          - This is another second level list item
        """
        original = "- This is a first level list item\n  - This is a second level list item\n  - This is another second level list item\n"
        expected = original

        log_tree = LogTree(original)

        self.assertEqual(3, len(log_tree.entries))
        self.assertEqual(expected, log_tree.render_as_string())


if __name__ == '__main__':
    unittest.main()
