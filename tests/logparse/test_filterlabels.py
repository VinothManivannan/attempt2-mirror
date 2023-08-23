import unittest
from os import path
from cmlpytools.logparse import LogTree

DIR_PATH = path.dirname(path.realpath(__file__))


def read_file(file_path):
    """
    Helper function that reads a file and return the content as a string.
    """
    with open(file_path, "r") as f:
        return f.read()


class TestFilterLabels(unittest.TestCase):
    def test_no_filter(self):
        log_tree = LogTree.from_file(path.join(DIR_PATH, "sample1/input.md"))
        expected = read_file(path.join(DIR_PATH, "sample1/output_all.md"))

        self.assertEqual(expected, log_tree.render_as_string())

    def test_filter_label_none(self):
        log_tree = LogTree.from_file(path.join(DIR_PATH, "sample1/input.md"))
        expected = read_file(path.join(DIR_PATH, "sample1/output_none.md"))

        log_tree.filter_labels([])

        self.assertEqual(expected, log_tree.render_as_string())

    def test_filter_label_foo(self):
        log_tree = LogTree.from_file(path.join(DIR_PATH, "sample1/input.md"))
        expected = read_file(path.join(DIR_PATH, "sample1/output_foo.md"))

        log_tree.filter_labels(["Foo"])

        self.assertEqual(expected, log_tree.render_as_string())

    def test_filter_label_bar(self):
        log_tree = LogTree.from_file(path.join(DIR_PATH, "sample1/input.md"))
        expected = read_file(path.join(DIR_PATH, "sample1/output_bar.md"))

        log_tree.filter_labels(["Bar"])

        self.assertEqual(expected, log_tree.render_as_string())

    def test_filter_label_foo_bar(self):
        log_tree = LogTree.from_file(path.join(DIR_PATH, "sample1/input.md"))
        expected = read_file(path.join(DIR_PATH, "sample1/output_foo_bar.md"))

        log_tree.filter_labels(["Foo", "Bar"])

        self.assertEqual(expected, log_tree.render_as_string())

    def test_filter_label_not_case_sensitive(self):
        log_tree = LogTree.from_file(path.join(DIR_PATH, "sample1/input.md"))
        expected = read_file(path.join(DIR_PATH, "sample1/output_foo.md"))

        log_tree.filter_labels(["FoO"])

        self.assertEqual(expected, log_tree.render_as_string())


if __name__ == '__main__':
    unittest.main()
