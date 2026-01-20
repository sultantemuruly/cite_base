def read_markdown_file(filepath):
    """Reads the content of a Markdown file as a string."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        return text
    except FileNotFoundError:
        return f"Error: The file at {filepath} was not found."
    except Exception as e:
        return f"An error occurred: {e}"
