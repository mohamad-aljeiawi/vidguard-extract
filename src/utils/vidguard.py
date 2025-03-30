import re
import requests
import base64
import binascii
from src.utils.aadecode import decode, extract_json


SUPPORTED_DOMAINS: list[str] = [
    r"shoofflix\.site",
    r"bembed\.net",
    r"vidguard\.to",
    r"vembed\.net",
    r"listeamed\.net",
]


def is_supported_url(url: str) -> bool:
    pattern: re.Pattern = re.compile(
        r"^(https?://)?(www\.)?({})/e/([A-Za-z0-9]+)".format(
            "|".join(SUPPORTED_DOMAINS)
        )
    )
    return re.match(pattern, url) is not None


def extract_video_id(url: str) -> str | None:
    match: re.Match | None = re.search(r"/e/([A-Za-z0-9]+)", url)
    return match.group(1) if match else None


def get_video_url(page_url: str) -> list[dict[str, str]]:
    try:
        if not is_supported_url(page_url):
            raise ValueError("Unsupported video URL")

        video_id: str | None = extract_video_id(page_url)
        if not video_id:
            raise ValueError("Invalid video ID format")

        headers: dict[str, str] = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
            "Referer": page_url,
        }

        response: requests.Response = requests.get(page_url, headers=headers)
        if response.status_code != 200:
            raise ValueError("Failed to fetch page")
        data: str = response.text

        encoded_script: re.Match | None = re.search(
            r'eval\("window\.ADBLOCKER\s*=\s*false;\\n(.+?);"\);</script', data
        )
        if not encoded_script:
            raise ValueError("Encoded script not found")

        decoded_script: str = decode(process_script(encoded_script.group(1)), alt=True)
        json_data: dict[str, str] | None = extract_json(decoded_script)

        if "stream" not in json_data:
            raise ValueError("Stream data missing")

        stream_url: list[dict[str, str]] | str = json_data["stream"]
        if isinstance(stream_url, list):
            valid_streams: list[dict[str, str]] = [
                s for s in stream_url if s.get("URL")
            ]
            if not valid_streams:
                raise ValueError("No valid streams found")
            stream_url: str = max(
                valid_streams, key=lambda x: int(x["Label"].replace("p", ""))
            )["URL"]

        final_url: str = sig_decode(stream_url)
        return final_url

    except Exception as e:
        raise Exception(f"Extraction failed: {str(e)}")


def process_script(script: str) -> str:
    replacements: dict[str, str] = {
        "\\u002b": "+",
        "\\u0027": "'",
        "\\u0022": '"',
        "\\/": "/",
        "\\\\": "\\",
    }
    for k, v in replacements.items():
        script: str = script.replace(k, v)
    return script


def sig_decode(url: str) -> str:
    sig: str = url.split("sig=")[1].split("&")[0]
    t: str = ""
    for v in binascii.unhexlify(sig):
        t += chr((v if isinstance(v, int) else ord(v)) ^ 2)
    t += "=="
    t = list(base64.b64decode(t)[:-5][::-1])
    for i in range(0, len(t) - 1, 2):
        t[i + 1], t[i] = t[i], t[i + 1]
    s: str = ""
    for v in t:
        s += chr(v)
    url: str = url.replace(sig, s[:-5])
    return url
