"""Tests for the FileManager class"""

import pytest
from unittest.mock import MagicMock  # For older style mocking if needed, but prefer pytest-mock
from editor.models.text_buffer import TextBuffer as BufferClass  # aliased to avoid pytest collection
from editor.io.file_manager import FileManager

# No need for MockObserver here as we will mock TextBuffer methods directly


@pytest.fixture
def mock_text_buffer(mocker):
    """Provides a MagicMock instance for TextBuffer."""
    mock_buffer = mocker.MagicMock(spec=BufferClass)
    return mock_buffer


@pytest.fixture
def file_manager_with_mock_buffer(mock_text_buffer):
    """Provides a FileManager instance initialized with a mocked TextBuffer."""
    return FileManager(mock_text_buffer)


# --- Tests for save_to_txt ---


def test_save_to_txt_success(file_manager_with_mock_buffer, mock_text_buffer, tmp_path):
    """Test successfully saving content to a file using a mock TextBuffer."""
    content_to_save = "Hello from mock TextBuffer!\nThis is a test."
    mock_text_buffer.get_all_text.return_value = content_to_save

    test_file = tmp_path / "output_mock.txt"
    file_manager_with_mock_buffer.save_to_txt(str(test_file))

    # Verify get_all_text was called on the mock
    mock_text_buffer.get_all_text.assert_called_once()

    assert test_file.exists()
    with open(test_file, "r", encoding="utf-8") as f:
        read_content = f.read()
    assert read_content == content_to_save


def test_save_to_txt_os_error(file_manager_with_mock_buffer, mock_text_buffer, tmp_path, capsys):
    """Test save_to_txt with an OS error using a mock TextBuffer."""
    mock_text_buffer.get_all_text.return_value = "Some content"

    # Use tmp_path itself (which is a directory) as the filepath to cause an error
    error_path = str(tmp_path)

    file_manager_with_mock_buffer.save_to_txt(error_path)

    # Verify get_all_text was called
    mock_text_buffer.get_all_text.assert_called_once()

    captured = capsys.readouterr()
    assert "Error saving file to" in captured.err
    assert str(tmp_path) in captured.err  # Check if the path is in the error message


# --- Tests for load_from_txt ---


def test_load_from_txt_success(file_manager_with_mock_buffer, mock_text_buffer, tmp_path):
    """Test successfully loading content and calling set_content on mock TextBuffer."""
    file_content = "Load this into the mock TextBuffer.\nWith a newline."
    test_file = tmp_path / "input_mock.txt"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(file_content)

    file_manager_with_mock_buffer.load_from_txt(str(test_file))

    # Verify set_content was called on the mock with the correct data
    mock_text_buffer.set_content.assert_called_once_with(file_content)


def test_load_from_txt_file_not_found(file_manager_with_mock_buffer, mock_text_buffer, capsys):
    """Test load_from_txt with a non-existent file; set_content should not be called."""
    non_existent_filepath = "this_file_definitely_does_not_exist_XYZ.txt"

    file_manager_with_mock_buffer.load_from_txt(non_existent_filepath)

    # Verify set_content was NOT called
    mock_text_buffer.set_content.assert_not_called()

    captured = capsys.readouterr()
    assert "Error: File not found at" in captured.err
    assert non_existent_filepath in captured.err


def test_load_from_txt_read_io_error(file_manager_with_mock_buffer, mock_text_buffer, tmp_path, capsys, mocker):
    """Test load_from_txt with an IOError during file read; set_content should not be called."""
    error_filepath_str = str(tmp_path / "read_error_mock.txt")
    # Create the file so open() itself doesn't fail with FileNotFoundError
    with open(error_filepath_str, "w", encoding="utf-8") as f_dummy:
        f_dummy.write("dummy content for successful open")

    # Configure the mock for open() to raise error on read
    mock_open_function = mocker.patch("builtins.open", mocker.mock_open())
    mock_open_function.return_value.__enter__.return_value.read.side_effect = IOError("Simulated read error")

    file_manager_with_mock_buffer.load_from_txt(error_filepath_str)

    # Verify set_content was NOT called
    mock_text_buffer.set_content.assert_not_called()

    captured = capsys.readouterr()
    assert "Error reading file" in captured.err  # Matches the error message in FileManager
    assert "Simulated read error" in captured.err
    assert error_filepath_str in captured.err


def test_file_manager_constructor_type_error():
    """Test that FileManager constructor raises TypeError for wrong buffer type."""
    with pytest.raises(TypeError, match="text_buffer must be an instance of TextBuffer"):
        FileManager("not a textbuffer")

    # Should not raise for a valid (even if mock) TextBuffer or a real one
    try:
        # Using unittest.mock for variety, and the aliased TextBuffer
        mock_buffer_unittest = MagicMock(spec=BufferClass)
        FileManager(mock_buffer_unittest)
        FileManager(BufferClass())  # Real TextBuffer instance
    except TypeError:
        pytest.fail("FileManager raised TypeError unexpectedly with a valid TextBuffer or mock.")
