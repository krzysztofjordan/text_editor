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


def test_get_line_recursive_paths_manually_constructed_rope():
    """Test get_line with manually constructed ropes to hit recursive paths."""

    # Case 1: Line entirely in left child
    # Rope: L0\nL1 | R0\nR1 (where | is node boundary)
    # Lines: "L0", "L1", "R0", "R1"
    leaf_l1 = LeafNode("L0\nL1\n")  # Ensures a newline between L1 and R0
    leaf_r1 = LeafNode("R0\nR1")
    rope1 = Rope(InternalNode(leaf_l1, leaf_r1))
    assert rope1.get_line_count() == 4, "Case 1: Line count"
    assert rope1.get_line(0) == "L0", "Case 1: Get L0"
    assert rope1.get_line(1) == "L1", "Case 1: Get L1"
    # These will test Path 3 with left ending in NL
    assert rope1.get_line(2) == "R0", "Case 1: Get R0 (Path 3 via left ending NL)"
    assert rope1.get_line(3) == "R1", "Case 1: Get R1 (Path 3 via left ending NL)"

    # Case 2: Line spans from left to right (left does NOT end in \n)
    # Rope: L0_part1 | _L0_part2\nR1
    # Lines: "L0_part1_L0_part2", "R1"
    leaf_l2 = LeafNode("L0_part1")
    leaf_r2 = LeafNode("_L0_part2\nR1")
    rope2 = Rope(InternalNode(leaf_l2, leaf_r2))
    assert rope2.get_line_count() == 2, "Case 2: Line count"
    assert rope2.get_line(0) == "L0_part1_L0_part2", "Case 2: Get spanned line"
    # This will test Path 3 with left NOT ending in NL
    assert rope2.get_line(1) == "R1", "Case 2: Get R1 (Path 3 via left not ending NL)"

    # Case 3: Line is last of left, left DOES end in \n (empty line)
    # Rope: L0\nL1\n | R0\nR1 -> effectively L0\nL1\n\nR0\R1 for 5 lines
    # Lines: "L0", "L1", "", "R0", "R1"
    leaf_l3 = LeafNode("L0\nL1\n\n")  # Ends in double newline for empty line test
    leaf_r3 = LeafNode("R0\nR1")
    rope3 = Rope(InternalNode(leaf_l3, leaf_r3))
    assert rope3.get_line_count() == 5, "Case 3: Line count"
    assert rope3.get_line(0) == "L0", "Case 3: Get L0"
    assert rope3.get_line(1) == "L1", "Case 3: Get L1"
    assert rope3.get_line(2) == "", "Case 3: Get empty line from left's trailing NL"
    assert rope3.get_line(3) == "R0", "Case 3: Get R0"
    assert rope3.get_line(4) == "R1", "Case 3: Get R1"

    # Case 4: More complex tree (nested InternalNodes)
    # Structure: ((A\nB | C) | (D\nE | F\nG))
    # Text: A\nBC\nD\nEF\nG
    # Lines:
    # 0: A
    # 1: BC
    # 2: D
    # 3: EF
    # 4: G
    node_a = LeafNode("A\nB")  # lc=2, lll=1 ("B")
    node_b = LeafNode("C")  # lc=1, lll=1 ("C")
    node_c = LeafNode("D\nE")  # lc=2, lll=1 ("E")
    node_d = LeafNode("F\nG")  # lc=2, lll=1 ("G")

    # Metrics recap for InternalNode path logic (simplified):
    # Path 1 (in left): query < left.lc - 1
    # Path 2 (span/last of left): query == left.lc - 1
    # Path 3 (in right): query > left.lc - 1
    #   adj = query - (left.lc - 1)

    # Inner left node: (A\nB | C) -> text "A\nBC", lc=2, lll=2 ("BC")
    inner_left = InternalNode(node_a, node_b)
    # Check inner_left construction:
    # node_a metrics: len=3, lc=2, lll=1 ("B")
    # node_b metrics: len=1, lc=1, lll=1 ("C")
    # Combined (A\nB + C): len=4. Ends in newline? No (B + C). lc = (2-1)+1 = 2.
    # lll = 1+1=2 ("BC")
    assert inner_left.metrics.line_count == 2
    assert inner_left.metrics.last_line_length == 2
    assert inner_left.get_text() == "A\nBC"

    # Inner right node: (D\nE | F\nG) -> text "D\nEF\nG", lc=3, lll=1 ("G")
    inner_right = InternalNode(node_c, node_d)
    # Check inner_right construction:
    # node_c metrics: len=3, lc=2, lll=1 ("E")
    # node_d metrics: len=3, lc=2, lll=1 ("G")
    # Combined (D\nE + F\nG): len=6. Ends in newline? No (E+F).
    # lc = (2-1)+2=3. lll=1 ("G") -> (EF+G)
    #   Line 0: D. Line 1: EF. Line 2: G (EFG if no NL in F)
    #   D\nE + F\nG => D\nEF\nG. lc=3, lll=1 ("G") (Correct)
    assert inner_right.metrics.line_count == 3
    assert inner_right.metrics.last_line_length == 1
    assert inner_right.get_text() == "D\nEF\nG"

    # Root node: (inner_left | inner_right)
    # inner_left: "A\nBC" (lc=2, lll=2)
    # inner_right: "D\nEF\nG" (lc=3, lll=1)
    # Combined: "A\nBC" + "D\nEF\nG" => "A\nBCD\nEF\nG"
    #   lc = (2-1) + 3 = 4. lll=1 ("G")
    #   Line 0: A. Line 1: BCD. Line 2: EF. Line 3: G.
    #   This is WRONG vs structure: A, BC, D, EF, G.
    #   Text concat for RopeMetrics seems too simple.
    #   RopeMetrics.__add__ lc: (slc + olc -1) if no trail NL. This is for TEXT.
    #   Metrics for root_complex based on text "A\nBCD\nEF\nG" is (2-1)+3=4 lines.

    root_complex = InternalNode(inner_left, inner_right)
    rope4 = Rope(root_complex)
    # Expected text: "A\nBC" + "D\nEF\nG" = "A\nBCD\nEF\nG"
    # Expected lines: "A", "BCD", "EF", "G"
    # Expected line_count: 4
    assert rope4.get_text() == "A\nBCD\nEF\nG"
    assert rope4.get_line_count() == 4, "Case 4: Complex tree line count"

    # Test lines for complex tree
    assert rope4.get_line(0) == "A", "Complex tree line 0 (A)"
    # Query idx=0: inner_left.lc-1 = 2-1 = 1. 0 < 1. Path 1 (left).
    #   inner_left gets 0. node_a.lc-1 = 2-1=1. 0 < 1. Path 1 (node_a).
    #     node_a gets 0. Returns "A".

    assert rope4.get_line(1) == "BCD", "Complex tree line 1 (BCD)"
    # Query idx=1: inner_left.lc-1 = 1. 1 == 1. Path 2 (span/last of inner_left).
    #   inner_left gets 1.
    #     node_a.lc-1 = 1. 1 == 1. Path 2 (span/last of node_a).
    #       node_a gets 1. Returns "B".
    #       node_a.lll > 0 (true, it's 1 for "B").
    #       inner_left calls node_b._get_line_recursive(0). Returns "C".
    #       So inner_left._get_line_recursive(1) returns "BC".
    #       This is `line_str` for root call.
    #   inner_left.lll > 0 (true, it's 2 for "BC").
    #   root calls inner_right._get_line_recursive(0).
    #     inner_right gets 0.
    #       node_c.lc-1 = 1. 0 < 1. Path 1 (node_c).
    #         node_c gets 0. Returns "D".
    #   So root concatenates "BC" + "D" = "BCD". Correct.

    assert rope4.get_line(2) == "EF", "Complex tree line 2 (EF)"
    # Query idx=2: inner_left.lc-1 = 1. 2 > 1. Path 3 (right).
    #   adj_idx = 2 - (inner_left.lc-1) = 2 - (2-1) = 1.
    #   inner_right gets 1.
    #     node_c.lc-1 = 1. 1 == 1. Path 2 (span/last of node_c).
    #       node_c gets 1. Returns "E".
    #       node_c.lll > 0 (true, it's 1 for "E").
    #       inner_right calls node_d._get_line_recursive(0). Returns "F".
    #       So inner_right._get_line_recursive(1) returns "EF". Correct.

    assert rope4.get_line(3) == "G", "Complex tree line 3 (G)"
    # Query idx=3: inner_left.lc-1 = 1. 3 > 1. Path 3 (right).
    #   adj_idx = 3 - (inner_left.lc-1) = 3 - (2-1) = 2.
    #   inner_right gets 2.
    #     node_c.lc-1 = 1. 2 > 1. Path 3 (right of node_c).
    #       adj_idx_for_node_d = 2 - (node_c.lc-1) = 2 - (2-1) = 1.
    #       node_d gets 1. Returns "G". Correct.

    # Test with only newlines
    rope_nlnl = Rope(InternalNode(LeafNode("\n"), LeafNode("\n")))
    # Text: "\n\n", lc=3. Lines: "", "", ""
    assert rope_nlnl.get_line_count() == 3, "NLNL: Line count"
    assert rope_nlnl.get_line(0) == "", "NLNL: line 0"
    assert rope_nlnl.get_line(1) == "", "NLNL: line 1"
    assert rope_nlnl.get_line(2) == "", "NLNL: line 2"

    # Test with text then newlines
    # L: "A\nB" (lc2,lll1), R: "\nC" (lc2,lll1)
    # Expected Text: A\nB\nC. Expected Lines: A, B, C. Expected LC = 3.
    # Metrics: (A\nB).lc=2, (\nC).lc=2. Combined LC = (2-1)+2 = 3. Correct.
    # (A\nB).lll = 1 ("B").
    # Path 2 (line 1): B + "" = "B". Path 3 (line 2): "C". Correct.
    rope_text_nl = Rope(InternalNode(LeafNode("A\nB"), LeafNode("\nC")))
    assert rope_text_nl.get_text() == "A\nB\nC"
    assert rope_text_nl.get_line_count() == 3, "TextNL: Line count"
    assert rope_text_nl.get_line(0) == "A", "TextNL: line 0 (A)"
    assert rope_text_nl.get_line(1) == "B", "TextNL: line 1 (B)"
    assert rope_text_nl.get_line(2) == "C", "TextNL: line 2 (C)"
