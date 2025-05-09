import httpx
import os
import re
import pymupdf
import logging
from urllib.parse import urlparse, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler

CACHE_DIR = ".cache"
PREVIEW_LIMIT = 20
ZOTERO_PATH = "E:/论文"
logger = logging.getLogger(__name__)
client = httpx.Client(base_url="http://127.0.0.1:23119/api/users/0/")


def make_cache(pdf_path: str):
    text = ""
    anno = ""
    doc = pymupdf.open(pdf_path)
    for page in doc:
        textpage = page.get_textpage()
        text += textpage.extractText()
        for a in page.annots():
            content = a.info["content"]
            if content:
                anno += content + "\n"
    return text + "\n\n" + anno


def check_cache(items):
    if not os.path.exists(CACHE_DIR):
        os.mkdir(CACHE_DIR)
    for item in items:
        key = item["key"]
        pdf_path = item["path"]
        title = item["title"]
        cache_path = f"{CACHE_DIR}/{key}.txt"
        if os.path.exists(cache_path) and os.path.getmtime(cache_path) > os.path.getmtime(pdf_path):
            logger.debug(f"Cache for [{key}] {title} is up to date.")
            continue
        logger.info(f"Creating cache for [{key}] {title}...")
        text = make_cache(pdf_path)
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(text)
    logger.info("All caches are created.")


def find_pdf_file(path: str):
    # this method is way more efficient than requiring the Zotero API to get the file lmao
    for e in os.listdir(path):
        if os.path.splitext(e)[1] == ".pdf":
            return f"{path}/{e}"


def get_pdf_files(collection_key: str):
    res = client.get(f"collections/{collection_key}/items")
    ret = []
    for e in res.json():
        if "attachment" not in e["links"]:
            continue
        pdf_key = e["links"]["attachment"]["href"][-8:]
        pdf_path = find_pdf_file(f"{ZOTERO_PATH}/storage/{pdf_key}")
        ret.append(
            {
                "key": e["key"],
                "title": e["data"]["title"],
                "path": pdf_path,
                "publication": e["data"].get("publicationTitle", ""),
            }
        )
    return ret


def get_tags():
    res = client.get("tags")
    return [{"tag": e["tag"], "numItems": e["meta"]["numItems"]} for e in res.json()]


def get_collections():
    res = client.get("collections")
    return [{"key": e["key"], "name": e["data"]["name"], "numItems": e["meta"]["numItems"]} for e in res.json()]


def fulltext_search(rows: list, query: str, ignore_case: bool = False) -> list:
    check_cache(rows)  # Ensure cache is up to date
    res = []
    for row in rows:
        key = row["key"]
        # title = row["title"]
        # pdf_path = row["path"]
        cache_path = f"{CACHE_DIR}/{key}.txt"

        with open(cache_path, "r", encoding="utf-8") as f:
            text = f.read()
            text = text.replace("-\n", "")  # Remove hyphenation
            text = text.replace("\n", " ")  # Replace newlines with spaces
            text = re.sub(r"\s+", " ", text)  # Normalize whitespace
            preview = []
            for match in re.finditer(query, text, re.IGNORECASE if ignore_case else 0):
                b = match.start()
                c = match.end()
                a = max(0, b - 100)
                d = min(len(text), c + 100)
                if len(preview) < PREVIEW_LIMIT:
                    preview.append(text[a:b] + f"<mark>{match.group()}</mark>" + text[c:d])
                else:
                    break
            if preview:
                row["preview"] = preview
                res.append(row)
    logger.debug(f"Found {len(res)} rows matching the query '{query}'")
    return res


def api_root(self: "Handler"):
    html = """<html lang="zh">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>搜索</title>
</head>

<body>
  <form action="/search" method="get">
    <h2>分类</h2>
    <ol>
      {{items}}
    </ol>
    <h2>搜索</h2>
    <input type="text" name="q">
    <label><input type="checkbox" name="i" checked>忽略大小写</label>
  </form>
</body>

</html>"""
    collections = get_collections()
    items = ""
    for e in collections:
        items += "<li><label>"
        items += f'<input type="checkbox" name="c" value="{e["key"]}">{e["name"]} ({e["numItems"]})</label></li>'
    html = html.replace("{{items}}", items)
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    self.wfile.write(html.encode("utf-8"))


def api_search(self: "Handler"):
    html = """<html lang="zh">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>搜索结果</title>
<style>
.action {
  cursor: pointer;
  color: blue;
  text-decoration: underline;
  margin-right: 0.5em;
}
</style>
</head>

<body>
  <h2>搜索结果</h2>
  {{results}}
</body>

</html>"""
    query_dict = parse_qs(self.url.query)
    collections = query_dict.get("c", [])
    query = query_dict.get("q", [])
    ignore_case = True if query_dict.get("i", [""])[0] == "on" else False
    if not query or not collections:
        self.send_response(400)
        self.end_headers()
        return

    # merge all collections
    rows = {}
    for c in collections:
        items = get_pdf_files(c)
        for item in items:
            rows[item["key"]] = item
    rows = list(rows.values())
    logger.info(f"Found {len(rows)} items in selected collections.")

    rows = fulltext_search(rows, query[0], ignore_case)
    results = ""
    for r in rows:
        key = r["key"]
        title = r["title"]
        preview = r["preview"]
        publication = r["publication"]
        path = r["path"]
        results += f'<h3><a class="action" href="zotero://select/library/items/{key}">查看</a><span class="action" onclick="fetch(\'/open?path={path}\')">打开</span>{title}</h3>'
        results += f"<h4>{publication}</h4>"
        results += "<ul>" + "".join(f"<li>{p}</li>" for p in preview) + "</ul>"
    html = html.replace("{{results}}", results)
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()
    self.wfile.write(html.encode("utf-8"))


def api_open_file(self: "Handler"):
    query_dict = parse_qs(self.url.query)
    file_path = query_dict.get("path", None)
    if file_path:
        os.startfile(file_path[0])
    self.send_response(200)
    self.end_headers()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.url = urlparse(self.path)
        path = self.url.path
        if path == "/":
            api_root(self)
        elif path == "/search":
            api_search(self)
        elif path == "/open":
            api_open_file(self)

    def log_message(self, format, *args):
        logger.info(format, *args)


def main():
    address = "127.0.0.1"
    port = 8080
    logger.info(f"Starting server on {address}:{port}")
    logger.info(f">>> http://127.0.0.1:{port}")
    server = HTTPServer((address, port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.WARNING)
    logger.setLevel(logging.INFO)
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s")
    main()
