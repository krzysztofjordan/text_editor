# Text Editor

This is a simple text editor application.

## Features

- Create, edit, and save text files
- Syntax highlighting for various programming languages
- Search and replace functionality
- Undo and redo actions
- Customizable themes

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/username/text-editor.git
   ```

2. Navigate to the project directory:
   ```bash
   cd text-editor
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python main.py
```

## Setting up Pre-commit Hooks

1. Install pre-commit:
   ```bash
   pip install pre-commit
   ```

2. Install the hooks:
   ```bash
   pre-commit install
   ```

3. Run the hooks manually (optional):
   ```bash
   pre-commit run --all-files
   ```

## Setting up a Local Python Virtual Environment

1. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   ```

2. Activate the virtual environment:
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```

3. Install dependencies (if any):
   ```bash
   pip install -r requirements.txt
   ```

4. Deactivate the virtual environment when done:
   ```bash
   deactivate
   ```