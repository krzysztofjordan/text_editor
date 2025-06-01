from setuptools import setup, find_packages

setup(
    name="simple-text-editor",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[],  # tkinter is part of Python's standard library
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "simple-text-editor=editor.main:SimpleTextEditor.main",
        ],
    },
    author="Krzysztof Jordan",
    description="A simple text editor built with Python and Tkinter",
    keywords="text editor, tkinter",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "Topic :: Text Editors",
    ],
)
