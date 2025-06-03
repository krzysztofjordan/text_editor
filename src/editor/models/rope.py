"""
A Rope data structure for efficient text storage and manipulation.
A tree-based data structure optimized for text editing operations.
"""

from dataclasses import dataclass  # noqa: F401
from typing import Optional


ROPE_MAX_LEAF = 128  # Maximum length of text in a leaf node


@dataclass
class RopeMetrics:
    """Metrics about a rope node including length and line information"""

    length: int  # Total length in characters
    line_count: int
    last_line_length: int

    @staticmethod
    def from_text(text: str) -> "RopeMetrics":
        # Create metrics compatible with len(text.split('\\n'))
        # For example: "a\\nb" -> lines=["a","b"], lc=2, lll=1
        # "" -> lines=[""], lc=1, lll=0
        # "\\n" -> lines=["",""], lc=2, lll=0

        lines = text.split("\n")
        _length = len(text)
        _line_count = len(lines)
        _last_line_length = len(lines[-1])

        return RopeMetrics(
            length=_length,
            line_count=_line_count,
            last_line_length=_last_line_length,
        )

    def __add__(self, other: "RopeMetrics") -> "RopeMetrics":
        """Combine two metrics efficiently using their existing properties."""
        if self.length == 0:
            return other
        if other.length == 0:
            return self

        _length = self.length + other.length
        _line_count: int
        _last_line_length: int

        # Determine if 'self' metrics represent text ending in a newline char.
        # True if last line has 0 length & line_count > 1 (distinguishes from "").
        self_ends_in_newline_char = self.last_line_length == 0 and self.line_count > 1

        if self_ends_in_newline_char:  # e.g. "abc\n" + "def"; "\n" + "def"
            _line_count = (self.line_count - 1) + other.line_count
            _last_line_length = other.last_line_length
        else:  # e.g. "abc" + "def"; "" + "def"
            _line_count = self.line_count + other.line_count - 1
            # If other is one segment (no newlines in it),
            # its last_line_length is its actual length.
            if other.line_count == 1:
                _last_line_length = self.last_line_length + other.length
            else:  # other has newlines within it.
                _last_line_length = other.last_line_length

        return RopeMetrics(
            length=_length,
            line_count=_line_count,
            last_line_length=_last_line_length,
        )


class RopeNode:
    """Base class for rope nodes"""

    def __init__(self):
        self._metrics: Optional[RopeMetrics] = None

    @property
    def metrics(self) -> RopeMetrics:
        """Get cached metrics or compute them"""
        if self._metrics is None:
            self._metrics = self._compute_metrics()
        return self._metrics

    def _compute_metrics(self) -> RopeMetrics:
        """Compute metrics for this node"""
        raise NotImplementedError

    def get_text(self) -> str:
        """Get the text content of this node"""
        raise NotImplementedError

    def split(self, index: int) -> tuple["RopeNode", "RopeNode"]:
        """Split this node at index, returning two new nodes (left, right)"""
        raise NotImplementedError


class LeafNode(RopeNode):
    """Leaf node containing actual text"""

    def __init__(self, text: str):
        super().__init__()
        self.text = text
        # Heuristic for initial very long leaves (currently inactive)
        if len(text) > ROPE_MAX_LEAF * 1.5 and len(text) > 0:
            # This is a simple initial split, Rope._concat_static will handle
            # further. Or, Rope constructor should handle this.
            # For now, keep it simpler by doing nothing here.
            pass

    def _compute_metrics(self) -> RopeMetrics:
        metrics = RopeMetrics.from_text(self.text)
        return metrics

    def get_text(self) -> str:
        return self.text

    def split(self, index: int) -> tuple[RopeNode, RopeNode]:
        if index < 0 or index > self.metrics.length:
            raise IndexError("Split index out of bounds for LeafNode")
        return LeafNode(self.text[:index]), LeafNode(self.text[index:])


class InternalNode(RopeNode):
    """Internal node with left and right children"""

    def __init__(self, left: RopeNode, right: RopeNode):
        super().__init__()
        # Ensure children are not trivial empty leaves that can be
        # optimized away by _concat_static
        if left.metrics.length == 0 and isinstance(left, LeafNode):
            # This scenario should be handled by _concat_static not creating
            # such parents. However, if directly constructed:
            pass  # left child could be LeafNode("") validly
        if right.metrics.length == 0 and isinstance(right, LeafNode):
            pass

        self.left = left
        self.right = right

    def _compute_metrics(self) -> RopeMetrics:
        return self.left.metrics + self.right.metrics

    def get_text(self) -> str:
        return self.left.get_text() + self.right.get_text()

    def split(self, index: int) -> tuple[RopeNode, "RopeNode"]:
        if index < 0 or index > self.metrics.length:
            raise IndexError("Split index out of bounds for InternalNode")

        left_len = self.left.metrics.length
        if index < left_len:
            # Split occurs in the left child
            l_split, r_split = self.left.split(index)
            return l_split, Rope._concat_static(r_split, self.right)
        elif index > left_len:
            # Split occurs in the right child
            l_split, r_split = self.right.split(index - left_len)
            return Rope._concat_static(self.left, l_split), r_split
        else:  # index == left_len, split is exactly between left and right
            return self.left, self.right


class Rope:
    """A rope data structure for efficient text storage and manipulation"""

    def __init__(self, data: Optional[RopeNode | str] = None):
        """Initialize rope with optional text or a root node"""
        if data is None:
            self.root = LeafNode("")
        elif isinstance(data, str):
            # For very long initial strings, could build a balanced tree.
            # For now, single LeafNode, subsequent ops will split/balance.
            self.root = LeafNode(data)
        elif isinstance(data, RopeNode):
            self.root = data
        else:
            msg = "Invalid data for Rope constructor: " "must be RopeNode, str, or None"
            raise TypeError(msg)

    def __len__(self) -> int:
        """Get total length of text in rope"""
        return self.root.metrics.length

    def get_text(self) -> str:
        """Get entire text content"""
        return self.root.get_text()

    def get_line_count(self) -> int:
        """Get total number of lines"""
        return self.root.metrics.line_count

    def get_line(self, line_num: int) -> str:
        """Get text of a specific line.

        Currently, this method retrieves the full text and splits it by newlines.
        A future optimization would be to traverse the rope structure directly
        using line metrics for more efficient access.
        """
        # Validate line_num against the metrics-based line count.
        if not (0 <= line_num < self.get_line_count()):
            # For additional robustness, especially during development or if metrics
            # could be suspect, one might double-check against text.split() here.
            # However, for typical operation, trust metrics from self.get_line_count().
            raise IndexError(f"Line number {line_num} out of range.")

        # Efficient line retrieval by traversing the rope is a TODO.
        # For now, using string splitting for simplicity and correctness.
        text = self.get_text()
        lines = text.split("\n")

        # This check ensures that if line_num was valid according to metrics,
        # it should also be valid for the split lines. If not, it implies
        # a discrepancy between metrics and actual text content.
        if line_num >= len(lines):
            # This should ideally not be reached if metrics are accurate.
            # Handling potential edge case for an empty rope giving lines = [""]
            if line_num == 0 and self.root.metrics.length == 0:
                return ""
            # If still out of bounds, it indicates an internal inconsistency.
            raise IndexError(
                f"Metrics/text content mismatch: line {line_num} vs {len(lines)} lines"
            )
        return lines[line_num]

    @staticmethod
    def _concat_static(node1: RopeNode, node2: RopeNode) -> RopeNode:
        """Concatenates two rope nodes, with basic merging/balancing."""
        if node1.metrics.length == 0:  # If node1 is an empty leaf
            return node2
        if node2.metrics.length == 0:  # If node2 is an empty leaf
            return node1

        # Try to merge if both are leaves and total length is within limits
        if isinstance(node1, LeafNode) and isinstance(node2, LeafNode):
            if node1.metrics.length + node2.metrics.length <= ROPE_MAX_LEAF:
                return LeafNode(node1.text + node2.text)

        # Basic rebalancing: if one child is an internal node and the other
        # is a leaf that could be merged deeper. This is where more complex
        # balancing (rotations, depth checks) would go.
        # For now, just create an InternalNode.
        return InternalNode(node1, node2)

    def insert(self, index: int, text_to_insert: str) -> "Rope":
        """Insert text at given index, returning new rope"""
        if index < 0 or index > len(self):  # len(self) uses metrics
            msg = f"Rope insert index {index} out of range for " f"length {len(self)}"
            raise IndexError(msg)

        if not text_to_insert:
            return Rope(self.root)  # New rope with the same root (immutable)

        l_subtree, r_subtree = self.root.split(index)
        m_node = LeafNode(text_to_insert)

        # Concatenate: (L + M) + R
        # This order might be slightly better for some balancing heuristics
        # if L is large.
        temp_root = Rope._concat_static(l_subtree, m_node)
        new_root = Rope._concat_static(temp_root, r_subtree)

        return Rope(new_root)

    def delete(self, start: int, end: int) -> "Rope":
        """Delete text between start and end indices, returning new rope"""
        rope_len = len(self)
        if not (0 <= start <= end <= rope_len):
            msg = (
                f"Rope delete indices ({start},{end}) out of range for "
                f"length {rope_len}"
            )
            raise IndexError(msg)

        if start == end:
            return Rope(self.root)  # New rope with the same root

        # Split into three parts: L, M (to delete), R
        l_subtree, temp_subtree = self.root.split(start)
        # M_deleted is not used
        _, r_subtree = temp_subtree.split(end - start)

        new_root = Rope._concat_static(l_subtree, r_subtree)
        # Ensure root is LeafNode("") if empty
        if new_root.metrics.length == 0 and not isinstance(new_root, LeafNode):
            new_root = LeafNode("")
        elif (
            new_root.metrics.length == 0
            and isinstance(new_root, LeafNode)
            and new_root.text != ""
        ):
            new_root = LeafNode("")

        return Rope(new_root)
