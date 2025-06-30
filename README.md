# zotero-search-preview

Zotero is good. The search function of Zotero is good. But it doesn't show the preview of the search result. See:

- https://forums.zotero.org/discussion/104137/feature-request-search-preview
- https://forums.zotero.org/discussion/87897/where-is-the-preview-of-the-search-results
- https://forums.zotero.org/discussion/47283/preview-pdfs-in-full-text-search

So I decide to make my own search tool for Zotero. This tool will show the preview of the search result.

## Features
- Search pdf files by regex
- Annotaions in the pdf files are included in the search
- Highlight the matched text in the preview
- Open the pdf file with default pdf viewer

## Usage

This tool uses `uv` for dependency management. To run the tool, you need to have `uv` installed. You can install it using pip:

```bash
pip install uv
```

Then, you can run the tool using `uv`:

```bash
uv run main.py
```

`uv` will automatically create a virtual environment and install all required dependencies on first run.

Now you can access the application in your web browser: http://127.0.0.1:8088
