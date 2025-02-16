from html.parser import HTMLParser
from html import unescape


class TitleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = None
        self.current_tag = None
        self.depth = 0

    def handle_starttag(self, tag, attrs):
        self.depth += 1
        if self.depth == 1:  # Only consider top-level tags
            self.current_tag = tag

    def handle_endtag(self, tag):
        if self.depth == 1:
            self.current_tag = None
        self.depth -= 1

    def handle_data(self, data):
        if not self.title and self.current_tag and data.strip():
            self.title = data.strip()


def extract_title_from_content(content: str) -> str:
    """Extract title from README content using the first heading or any meaningful HTML tag"""
    lines = content.splitlines()

    # First try Markdown heading
    for line in lines:
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()

    # Then try HTML parsing - will capture first non-empty text in any tag
    parser = TitleParser()
    parser.feed(content)
    if parser.title:
        return unescape(parser.title)

    return "Untitled README"
