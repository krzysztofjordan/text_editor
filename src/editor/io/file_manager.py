"""
Manages file input/output operations for the text editor.
"""

import sys
from editor.models.text_buffer import TextBuffer


class FileManager:
    """
    Handles saving and loading of text files, interacting with a TextBuffer.
    """

    def __init__(self, text_buffer: TextBuffer):
        """
        Initializes the FileManager with a TextBuffer instance.

        Args:
            text_buffer: The TextBuffer to be used for file operations.
        """
        if not isinstance(text_buffer, TextBuffer):
            raise TypeError("text_buffer must be an instance of TextBuffer")
        self._text_buffer = text_buffer

    def load_from_txt(self, filepath: str):
        """
        Loads text content from the specified file into the associated TextBuffer.

        If the file is read successfully, its content replaces the entire
        content of the TextBuffer via text_buffer.set_content().
        If any error occurs during file operations, an error message is
        printed to stderr, and the TextBuffer remains unchanged.

        Args:
            filepath: The path to the text file to load.
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                file_data = f.read()

            # If file reading was successful, set the buffer content.
            # set_content will handle clearing, cursor reset, and notifications.
            self._text_buffer.set_content(file_data)

        except FileNotFoundError:
            print(f"Error: File not found at {filepath}", file=sys.stderr)
        except (IOError, OSError) as e:
            print(f"Error reading file {filepath}: {e}", file=sys.stderr)
        # No explicit 'else' needed; if try block completes, set_content was called.
        # If an exception occurs, set_content is skipped.

    def save_to_txt(self, filepath: str):
        """
        Saves the content of the associated TextBuffer to the specified text file.

        Args:
            filepath: The path to the file where the content will be saved.
        """
        try:
            content = self._text_buffer.get_all_text()
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
        except (IOError, OSError) as e:
            print(f"Error saving file to {filepath}: {e}", file=sys.stderr)
