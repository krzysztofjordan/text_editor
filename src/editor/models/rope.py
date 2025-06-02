"""
A Rope data structure for efficient text storage and manipulation.
A tree-based data structure optimized for text editing operations.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class RopeMetrics:
    """Metrics about a rope node including length and line information"""

    length: int  # Total length in characters
    line_count: int  # Number of lines
    last_line_length: int  # Length of the last line

    @staticmethod
    def from_text(text: str) -> "RopeMetrics":
        """Create metrics from a text string"""
        if not text:
            return RopeMetrics(length=0, line_count=1, last_line_length=0)

        length = len(text)
        count = text.count("\n")
        if not text.endswith("\n"):
            count += 1
            last_line_length = len(text.split("\n")[-1])
        else:
            last_line_length = 0

        return RopeMetrics(
            length=length, line_count=count, last_line_length=last_line_length
        )

    def __add__(self, other: "RopeMetrics") -> "RopeMetrics":
        """Combine two metrics, used when concatenating nodes"""
        if self.length == 0:
            return other
        if other.length == 0:
            return self

        # Calculate combined metrics
        total_length = self.length + other.length

        # If the left node ends with a newline (last_line_length == 0),
        # other's first line starts a new line
        if self.last_line_length == 0:
            total_lines = self.line_count + other.line_count
        else:
            # If left node doesn't end with newline, other's first line
            # is concatenated to left's last line
            total_lines = self.line_count + other.line_count - 1

        return RopeMetrics(
            length=total_length,
            line_count=total_lines,
            last_line_length=other.last_line_length,
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


class LeafNode(RopeNode):
    """Leaf node containing actual text"""

    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def _compute_metrics(self) -> RopeMetrics:
        return RopeMetrics.from_text(self.text)


class InternalNode(RopeNode):
    """Internal node with left and right children"""

    def __init__(self, left: RopeNode, right: RopeNode):
        super().__init__()
        self.left = left
        self.right = right

    def _compute_metrics(self) -> RopeMetrics:
        return self.left.metrics + self.right.metrics


class Rope:
    """A rope data structure for efficient text storage and manipulation"""

    def __init__(self, text: str = ""):
        """Initialize rope with optional text"""
        self.root = LeafNode(text)

    def __len__(self) -> int:
        """Get total length of text in rope"""
        return len(self.get_text())

    def get_text(self) -> str:
        """Get entire text content"""
        if isinstance(self.root, LeafNode):
            return self.root.text
        return self._get_text(self.root)

    def _get_text(self, node: RopeNode) -> str:
        """Recursively get text from node"""
        if isinstance(node, LeafNode):
            return node.text
        return self._get_text(node.left) + self._get_text(node.right)

    def get_line_count(self) -> int:
        """Get total number of lines"""
        text = self.get_text()
        if not text:
            return 1
        return len(text.split("\n"))

    def get_line(self, line_num: int) -> str:
        """Get text of specific line"""
        if line_num < 0 or line_num >= self.get_line_count():
            raise IndexError("Line number out of range")

        text = self.get_text()
        lines = text.split("\n")
        return lines[line_num]

    def insert(self, index: int, text_to_insert: str) -> "Rope":
        """Insert text at given index, returning new rope"""
        if index < 0 or index > len(self):
            raise IndexError("Rope index out of range")

        if not text_to_insert:
            return self

        current_text = self.get_text()
        new_text = current_text[:index] + text_to_insert + current_text[index:]

        result = Rope()
        result.root = LeafNode(new_text)
        return result

    def delete(self, start: int, end: int) -> "Rope":
        """Delete text between start and end indices, returning new rope"""
        if start < 0 or end > len(self) or start > end:
            raise IndexError("Invalid rope slice indices")

        if start == end:
            return self

        current_text = self.get_text()
        new_text = current_text[:start] + current_text[end:]

        result = Rope()
        result.root = LeafNode(new_text)
        return result
