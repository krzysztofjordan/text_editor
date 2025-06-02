"""Tests for the Rope data structure"""

import pytest
from editor.models.rope import Rope


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
