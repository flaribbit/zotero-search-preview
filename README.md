# zotero-search-preview

Zotero is good. The search function of Zotero is good. But it doesn't show the preview of the search result. See:

- https://forums.zotero.org/discussion/104137/feature-request-search-preview
- https://forums.zotero.org/discussion/92598/feature-request-show-preview-of-results-when-searching-within-indexed-content
- https://forums.zotero.org/discussion/87897/where-is-the-preview-of-the-search-results
- https://forums.zotero.org/discussion/47283/preview-pdfs-in-full-text-search

So I decide to make my own search tool for Zotero. This tool will show the preview of the search result.

## Features
- Search pdf files by regex
- Multiple queries separated by `&&`
  - For example: `(DQN|DDPG)&&dual`
- Search in selected collections
- Annotaions in the pdf files are included in the search
- Highlight the matched text in the preview
- Open the pdf file with default pdf viewer

## Usage

First, enable this feature in Zotero 7.

![image](https://github.com/user-attachments/assets/353c1e66-a7cf-470a-8ab0-e414accc40a5)

This application uses `uv` for dependency management. So you need to have `uv` installed. You can install it using pip:

```bash
pip install uv
```

Then, you can run the tool using `uv`:

```bash
uv run main.py
```

`uv` will automatically create a virtual environment and install all required dependencies on first run.

It will show something like below on first run.
```
2025-07-02 10:56:00,928 - INFO - Checking config.json...
2025-07-02 10:56:00,929 - ERROR - Zotero data path does not exist. Please edit config.json.
2025-07-02 10:56:00,929 - ERROR - Hint: It should be something like 'C:/Users/YourUsername/Zotero' on Windows.
```

Just follow the instructions. You can find the data path here:
![image](https://github.com/user-attachments/assets/41aee990-1938-4484-b623-6b6496194032)

Run `main.py` again. Now you can access the application in your web browser: http://127.0.0.1:8088
