"""Tests for the Rope data structure"""

import pytest
from editor.models.rope import Rope, LeafNode, InternalNode, ROPE_MAX_LEAF, RopeMetrics


def test_empty_rope():
    """Test empty rope initialization"""
    rope = Rope()
    assert len(rope) == 0
    assert rope.get_text() == ""
    assert rope.get_line_count() == 1
    assert rope.get_line(0) == ""


def test_single_line_operations():
    """Test operations on a single line of text"""
    rope = Rope("Hello")

    # Basic properties
    assert len(rope) == 5
    assert rope.get_text() == "Hello"
    assert rope.get_line_count() == 1
    assert rope.get_line(0) == "Hello"

    # Insert in middle of line
    rope = rope.insert(5, " World")
    assert rope.get_text() == "Hello World"
    assert rope.get_line_count() == 1
    assert rope.get_line(0) == "Hello World"

    # Insert at start of line
    rope = rope.insert(0, "Say: ")
    assert rope.get_text() == "Say: Hello World"
    assert rope.get_line_count() == 1
    assert rope.get_line(0) == "Say: Hello World"


def test_multiline_operations():
    """Test operations with multiple lines"""
    rope = Rope("First\nSecond\nThird")

    # Basic properties
    assert len(rope) == 18
    assert rope.get_text() == "First\nSecond\nThird"
    assert rope.get_line_count() == 3
    assert rope.get_line(0) == "First"
    assert rope.get_line(1) == "Second"
    assert rope.get_line(2) == "Third"

    # Insert in middle of "First"
    rope = rope.insert(5, " line")
    assert rope.get_line(0) == "First line"
    assert rope.get_line_count() == 3

    # Insert new line in middle
    rope = rope.insert(10, "\nNew\n")
    assert rope.get_text() == "First line\nNew\n\nSecond\nThird"
    assert rope.get_line_count() == 5
    assert rope.get_line(0) == "First line"
    assert rope.get_line(1) == "New"
    assert rope.get_line(2) == ""
    assert rope.get_line(3) == "Second"
    assert rope.get_line(4) == "Third"


def test_line_spanning_operations():
    """Test operations that span multiple lines"""
    rope = Rope("Hello")
    rope = rope.insert(5, " beautiful")
    rope = rope.insert(14, "\nworld")

    assert rope.get_text() == "Hello beautifu\nworldl"
    assert rope.get_line_count() == 2
    assert rope.get_line(0) == "Hello beautifu"
    assert rope.get_line(1) == "worldl"

    # Insert text that spans a line boundary
    rope = rope.insert(5, " very\nreally")
    assert rope.get_text() == "Hello very\nreally beautifu\nworldl"
    assert rope.get_line_count() == 3
    assert rope.get_line(0) == "Hello very"
    assert rope.get_line(1) == "really beautifu"
    assert rope.get_line(2) == "worldl"


def test_edge_cases():
    """Test edge cases and boundary conditions"""
    rope = Rope("Hello\nWorld")

    # Empty string insertions
    rope = rope.insert(5, "")
    assert rope.get_text() == "Hello\nWorld"

    # Insert at very end
    rope = rope.insert(len(rope), "!")
    assert rope.get_text() == "Hello\nWorld!"

    # Multiple consecutive newlines
    rope = rope.insert(5, "\n\n\n")
    assert rope.get_text() == "Hello\n\n\n\nWorld!"
    assert rope.get_line_count() == 5
    assert rope.get_line(0) == "Hello"
    assert rope.get_line(1) == ""
    assert rope.get_line(2) == ""
    assert rope.get_line(3) == ""
    assert rope.get_line(4) == "World!"

    # Delete across multiple lines
    rope = rope.delete(4, 8)
    assert rope.get_text() == "Hell\nWorld!"
    assert rope.get_line_count() == 2


def test_line_metrics():
    """Test line counting and metrics"""
    # Test with trailing newline
    rope = Rope("Hello\n")
    assert rope.get_line_count() == 2
    assert rope.get_line(0) == "Hello"
    assert rope.get_line(1) == ""

    # Test with multiple trailing newlines
    rope = Rope("Hello\n\n\n")
    assert rope.get_line_count() == 4
    assert rope.get_line(0) == "Hello"
    assert rope.get_line(1) == ""
    assert rope.get_line(2) == ""
    assert rope.get_line(3) == ""


def test_error_handling():
    """Test error conditions"""
    rope = Rope("Hello\nWorld")

    # Invalid indices
    with pytest.raises(IndexError):
        rope.insert(-1, "x")
    with pytest.raises(IndexError):
        rope.insert(12, "x")
    with pytest.raises(IndexError):
        rope.delete(-1, 5)
    with pytest.raises(IndexError):
        rope.delete(5, 12)
    with pytest.raises(IndexError):
        rope.delete(6, 5)
    with pytest.raises(IndexError):
        rope.get_line(-1)
    with pytest.raises(IndexError):
        rope.get_line(2)


def test_complex_merging():
    """Test complex scenarios where text needs to be merged across nodes"""
    rope = Rope("Hello")
    rope = rope.insert(5, " ")
    rope = rope.insert(6, "World")
    rope = rope.insert(11, "!")

    assert rope.get_text() == "Hello World!"
    assert rope.get_line_count() == 1
    assert rope.get_line(0) == "Hello World!"

    # Insert text that spans nodes
    rope = rope.insert(6, "big ")
    assert rope.get_text() == "Hello big World!"
    assert rope.get_line_count() == 1
    assert rope.get_line(0) == "Hello big World!"

    # Create multiple lines spanning nodes
    rope = rope.insert(6, "\nbeautiful\n")
    assert rope.get_text() == "Hello \nbeautiful\nbig World!"
    assert rope.get_line_count() == 3
    assert rope.get_line(0) == "Hello "
    assert rope.get_line(1) == "beautiful"
    assert rope.get_line(2) == "big World!"


def test_rope_concat_static_behavior():
    """Test the Rope._concat_static method for merging and node creation."""
    # Test merging two small LeafNodes
    leaf1_small = LeafNode("a" * 10)
    leaf2_small = LeafNode("b" * 10)
    merged_small = Rope._concat_static(leaf1_small, leaf2_small)
    assert isinstance(merged_small, LeafNode), "Small leaves should merge"
    assert merged_small.text == "a" * 10 + "b" * 10
    assert merged_small.metrics.length == 20

    # Test non-merging of large LeafNodes
    leaf1_large = LeafNode("a" * ROPE_MAX_LEAF)
    # Ensure total length > ROPE_MAX_LEAF for this test case
    leaf2_also_large = LeafNode("b" * (ROPE_MAX_LEAF // 2))
    merged_large = Rope._concat_static(leaf1_large, leaf2_also_large)
    assert isinstance(
        merged_large, InternalNode
    ), "Large leaves should not merge if sum > ROPE_MAX_LEAF"
    assert merged_large.left == leaf1_large
    assert merged_large.right == leaf2_also_large
    assert merged_large.metrics.length == ROPE_MAX_LEAF + (ROPE_MAX_LEAF // 2)

    # Test concatenation with an empty LeafNode (left)
    empty_leaf = LeafNode("")
    leaf_content = LeafNode("content")
    merged_with_empty_left = Rope._concat_static(empty_leaf, leaf_content)
    assert (
        merged_with_empty_left == leaf_content
    ), "Concat with empty left should return right"

    # Test concatenation with an empty LeafNode (right)
    merged_with_empty_right = Rope._concat_static(leaf_content, empty_leaf)
    assert (
        merged_with_empty_right == leaf_content
    ), "Concat with empty right should return left"

    # Test merging two leaves that sum up to exactly ROPE_MAX_LEAF
    len1 = ROPE_MAX_LEAF // 2
    len2 = ROPE_MAX_LEAF - len1
    leaf_half1 = LeafNode("x" * len1)
    leaf_half2 = LeafNode("y" * len2)
    merged_exact = Rope._concat_static(leaf_half1, leaf_half2)
    assert isinstance(
        merged_exact, LeafNode
    ), "Leaves summing to ROPE_MAX_LEAF should merge"
    assert merged_exact.text == "x" * len1 + "y" * len2
    assert merged_exact.metrics.length == ROPE_MAX_LEAF


def test_rope_deletion_to_empty():
    """Test that deleting all content results in a canonical empty rope."""
    rope = Rope("Some initial text")
    assert len(rope) > 0
    rope = rope.delete(0, len(rope))

    assert len(rope) == 0, "Length should be 0 after full deletion"
    assert rope.get_text() == "", "Text should be empty string"
    assert rope.get_line_count() == 1, "Empty rope should have 1 line"
    assert rope.get_line(0) == "", 'Line 0 of empty rope should be ""'
    assert isinstance(rope.root, LeafNode), "Empty rope root must be LeafNode"
    assert rope.root.text == "", 'Empty rope root text must be ""'

    # Test deleting from a multi-line rope to empty
    rope_multiline = Rope("First line\\nSecond line")
    assert len(rope_multiline) > 0
    rope_multiline = rope_multiline.delete(0, len(rope_multiline))

    assert len(rope_multiline) == 0
    assert rope_multiline.get_text() == ""
    assert rope_multiline.get_line_count() == 1
    assert rope_multiline.get_line(0) == ""
    assert isinstance(rope_multiline.root, LeafNode)
    assert rope_multiline.root.text == ""


def test_rope_deletion_causing_merge():
    """Test deletion that should cause LeafNode merging."""
    # Ensure parts are small enough to merge after deletion, but not before
    # if ROPE_MAX_LEAF is very small. For typical ROPE_MAX_LEAF, this is fine.
    part1 = "a" * (ROPE_MAX_LEAF // 3)
    to_delete = "DELETE_ME"
    part2 = "b" * (ROPE_MAX_LEAF // 3)

    # Create a rope that will likely have part1, to_delete, part2 in
    # separate nodes or at least part1 and (to_delete + part2) initially
    # if to_delete+part2 is small enough. The key is after deleting
    # to_delete, part1 and part2 should merge.
    rope = Rope(part1)
    rope = rope.insert(len(rope), to_delete)
    rope = rope.insert(len(rope), part2)

    # Optional: Check initial structure if it helps debugging,
    # though not strictly necessary for the test
    # print(f"Initial rope text for merge test: {rope.get_text()}")

    # Delete the middle part
    delete_start_index = len(part1)
    delete_end_index = delete_start_index + len(to_delete)
    rope_after_delete = rope.delete(delete_start_index, delete_end_index)

    expected_text = part1 + part2
    assert (
        rope_after_delete.get_text() == expected_text
    ), "Text after deletion is incorrect"
    assert len(rope_after_delete) == len(
        expected_text
    ), "Length after deletion is incorrect"

    # The core assertion: the root should now be a single LeafNode if parts merged
    if len(expected_text) <= ROPE_MAX_LEAF and len(expected_text) > 0:
        assert isinstance(rope_after_delete.root, LeafNode)
        assert (
            rope_after_delete.root.text == expected_text
        ), "Merged LeafNode text incorrect"
    elif len(expected_text) == 0:
        assert isinstance(
            rope_after_delete.root, LeafNode
        ), "Empty result should be LeafNode"
        assert (
            rope_after_delete.root.text == ""
        ), "Empty result LeafNode text should be empty"
    # If expected_text is > ROPE_MAX_LEAF, it might be an InternalNode or
    # a single large Leaf. This specific test focuses on the merge case.


def test_rope_metrics_add_logic():
    """Test the RopeMetrics.__add__ method directly."""

    def _m(text: str) -> RopeMetrics:  # Helper
        return RopeMetrics.from_text(text)

    # Case 1: m1 (ends \n) + m2 (no \n) -> "a\nb"
    m1_ends_nl = _m("a\n")  # len=2, lc=2, lll=0
    m2_no_nl = _m("b")  # len=1, lc=1, lll=1
    res1 = m1_ends_nl + m2_no_nl
    assert res1.length == 3
    assert res1.line_count == 2, f"C1 LC: {res1.line_count}"
    assert res1.last_line_length == 1, f"C1 LLL: {res1.last_line_length}"

    # Case 2: m1 (no \n) + m2 (no \n) -> "ab"
    m1_no_nl = _m("a")  # len=1, lc=1, lll=1
    res2 = m1_no_nl + m2_no_nl
    assert res2.length == 2
    assert res2.line_count == 1, f"C2 LC: {res2.line_count}"
    assert res2.last_line_length == 2, f"C2 LLL: {res2.last_line_length}"

    # Case 3: m1 (no \n) + m2 (ends \n) -> "ab\n"
    m2_ends_nl = _m("b\n")  # len=2, lc=2, lll=0
    res3 = m1_no_nl + m2_ends_nl
    assert res3.length == 3
    assert res3.line_count == 2, f"C3 LC: {res3.line_count}"
    assert res3.last_line_length == 0, f"C3 LLL: {res3.last_line_length}"

    # Case 4: m1 (ends \n) + m2 (ends \n) -> "a\nb\n"
    res4 = m1_ends_nl + m2_ends_nl
    assert res4.length == 4
    assert res4.line_count == 3, f"C4 LC: {res4.line_count}"
    assert res4.last_line_length == 0, f"C4 LLL: {res4.last_line_length}"

    # Case 5: Empty metrics + content
    m_empty = _m("")  # len=0, lc=1, lll=0
    m_content = _m("abc\ndef")  # len=7, lc=2, lll=3
    res5_1 = m_empty + m_content
    assert res5_1.length == m_content.length
    assert res5_1.line_count == m_content.line_count
    assert res5_1.last_line_length == m_content.last_line_length

    # Case 6: Content + empty metrics
    res5_2 = m_content + m_empty
    assert res5_2.length == m_content.length
    assert res5_2.line_count == m_content.line_count
    assert res5_2.last_line_length == m_content.last_line_length

    # Case 7: Metrics from single newline char
    m_nl_only = _m("\n")  # len=1, lc=2, lll=0
    # "\n" + "abc\ndef" -> "\nabc\ndef" (lc=3, lll=3)
    res7_1 = m_nl_only + m_content
    assert res7_1.length == 1 + m_content.length
    assert res7_1.line_count == 1 + m_content.line_count  # lc: (2-1)+2 = 3
    assert res7_1.last_line_length == m_content.last_line_length

    # "abc\ndef" + "\n" -> "abc\ndef\n" (lc=3, lll=0)
    res7_2 = m_content + m_nl_only
    assert res7_2.length == m_content.length + 1
    # lc: (2+2-1) = 3, as m_content does not end in NL
    assert res7_2.line_count == 3, f"C7.2 LC: {res7_2.line_count}"
    assert (
        res7_2.last_line_length == 0
    ), f"C7.2 LLL: {res7_2.last_line_length}"  # m_nl_only is right part
