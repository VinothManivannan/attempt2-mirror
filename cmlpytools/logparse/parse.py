from builtins import object, bytes
from abc import ABCMeta, abstractmethod
import re
from io import BytesIO
from future.utils import with_metaclass

# Regex used to detect labels in log entries.
LABEL_REGEX = re.compile("\[(\w+)\]")

# Regex used to parse block entries from the markdown input file
# - `(?:^|\n|(?<=\n))` Marks the start of a block which can be either:
#       - `^`       Matches the start of the file
#       - `\n`      Matches the end a line
#       - `(?<=\n)` Matches an end a line which has already been consumed by the previous match
# - `((?: *- |#+ | *\w).*?)` captures the block itself:
#       - `(?: *- |#+ | *\w)` Matches the start of a valid block
#               - ` *- ` Matches the start of a markdown bullet item
#               - `#+ `  Matches the start of a markdown title
#               - ` *\w` Matches the start of a markdown text block
#       - `.*?` Matches any number characters but as little as possible (until a end of block is found)
# - `(?=\n+-|\n+#|\n*$)` Marks the end of a block in a non-capturing way. This can either be:
#       - `\n+ *-` Matches the start of a new markdown bullet item
#       - `\n+#`   Matches the start of a new markdown title
#       - `\n*$`   Matches the end of the file
MK_REGEX = re.compile("(?:^|\n|(?<=\n))((?: *- |#+ | *\w).*?)(?=\n+ *-|\n+#|\n*$)", re.DOTALL)


class Node(with_metaclass(ABCMeta, object)):
    """
    This class exposes some common functions used from LogTree that need to be implemented
    by both types of nodes (LogEntry, ReleaseEntry).
    """

    def __init__(self, text):
        self.text = text

    def render_as_string(self):
        """
        Render node as a python string
        """
        with BytesIO() as stream:
            self.render(stream)
            stream.seek(0)
            return str(stream.read(), encoding="utf-8")

    @abstractmethod
    def render(self, stream):
        """
        Render the current node as text to the provided file stream.
        """
        pass

    @abstractmethod
    def filter_labels(self, keep_labels):
        """
        Remove any content from the current node that does not include at least one of the labels
        specified in `keep_labels`. Labels are not case sensitive. Label `all` is always included.

        `keep_labels` should be a list of labels in lower-case.
        """
        pass

    @abstractmethod
    def is_empty(self):
        """
        Return True if the node has no content and can be discarded, False otherwise.
        """
        pass


class ReleaseEntry(Node):
    """
    A markdown title representing a release entry.
    """

    def __init__(self, text):
        super(ReleaseEntry, self).__init__(text)
        self.log_entries = []

    def add_log(self, log_entry):
        """
        Add a `log_entry` to the current release.
        """
        self.log_entries.append(log_entry)

    def render(self, stream):
        # If this is not the first line,
        if stream.tell() > 0:
            # add a line break to separate title from previous text.
            stream.write(bytes("\n", encoding='utf-8'))
        stream.write(bytes(self.text, encoding='utf-8'))
        stream.write(bytes("\n", encoding='utf-8'))

        for entry in self.log_entries:
            entry.render(stream)

    def filter_labels(self, keep_labels):
        self.log_entries = list([entry for entry in self.log_entries if entry.has_labels(keep_labels)])

    def is_empty(self):
        return len(self.log_entries) == 0


class LogEntry(Node):
    """
    A markdown text block or bullet point item representing a log entry.
    """

    def __init__(self, text):
        super(LogEntry, self).__init__(text)

        # Array containing all the labels present in this entry. All labels are saved in lower-case
        self.labels = [label.lower() for label in re.findall(LABEL_REGEX, self.text)]

    def render(self, stream):
        stream.write(bytes(re.sub(LABEL_REGEX, "", self.text), encoding='utf-8'))
        stream.write(bytes("\n", encoding='utf-8'))

    def has_labels(self, labels):
        """
        This function returns True if any of the `labels` is found in the log entry,
        of if the log entry has the label "all" 
        """
        for found_label in self.labels:
            if found_label == "all":
                return True

            for label in labels:
                if found_label == label:
                    return True

        return False

    def filter_labels(self, keep_labels):
        if not self.has_labels(keep_labels):
            self.text = ""

    def is_empty(self):
        return self.text == ""


class LogTree(Node):
    """
    This class is used to parse a release file to create an abstract tree that can be used to manipulate the content.
    """

    def __init__(self, text):
        """
        Split the text in blocks using markdown formating rules. This uses a regex that can
        recognize the following block types:
        - "### Title name\n"
        - "Text block\n"
        - "- Text block\n"
        """
        # Array containing a list of entries which can either be a log entry or a release name
        # Log entries are only added to this list when they don't belong to any release (at the top of the file)
        # Otherwise they are added as a child of the last release entry found which should be the last item of the list.
        self.entries = []

        mk_blocks = re.findall(MK_REGEX, text)

        for block in mk_blocks:
            if block.startswith("#"):
                # Release entry
                entry = ReleaseEntry(block)
                self.entries.append(entry)
            else:
                # Log entry
                log_entry = LogEntry(block)
                if len(self.entries) > 0 and isinstance(self.entries[-1], ReleaseEntry):
                    # If the last node is a release entry, add the log as a child of this last release.
                    release_entry = self.entries[-1]
                    release_entry.add_log(log_entry)
                else:
                    # Otherwise add it as a simple entry at the root of the tree.
                    self.entries.append(log_entry)

    @staticmethod
    def from_file(file_path):
        """
        Alternative constructor using a file path instead of a string.
        """
        with open(file_path, "r") as f:
            return LogTree(f.read())

    def filter_labels(self, keep_labels):
        """
        Remove all entries that don't contain at least one of the specified labels.
        """
        for entry in self.entries:
            entry.filter_labels([label.lower() for label in keep_labels])

        # Remove empty entries
        self.entries = list([entry for entry in self.entries if not entry.is_empty()])

    def is_empty(self):
        return len(self.entries) == 0

    def render(self, stream):
        """
        Render release notes to a stream
        """
        for entry in self.entries:
            entry.render(stream)

    def find_release(self, release_name):
        """
        Return first release entry matching the named provided from the release notes. Return None if no match was found.
        """
        found = None
        for entry in self.entries:
            if isinstance(entry, ReleaseEntry) and release_name in entry.text:
                found = entry
                break

        return found

    def has_release(self, release_name):
        """
        Return True if the release name was found in the release notes, False otherwise.
        """
        return self.find_release(release_name) is not None
