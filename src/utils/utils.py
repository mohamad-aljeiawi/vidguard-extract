from urllib.parse import urlparse, ParseResult


def is_valid_url(url_str: str) -> bool:
    try:
        url: ParseResult = urlparse(url_str)
        return all([url.scheme, url.netloc])
    except Exception:
        return False
