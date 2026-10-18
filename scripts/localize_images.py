#!/usr/bin/env python3
"""Fetch external images during the Pages build and rewrite them to same-origin assets."""
from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / "assets" / "images"
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".avif")

IMG_SRC_RE = re.compile(
    r'(?P<prefix><img\b[^>]*?\bsrc\s*=\s*)(?P<quote>["\'])(?P<url>.*?)(?P=quote)',
    re.IGNORECASE | re.DOTALL,
)
CSS_URL_RE = re.compile(
    r'url\(\s*(?P<quote>["\']?)(?P<url>https?://[^)"\']+)(?P=quote)\s*\)',
    re.IGNORECASE,
)

def is_external_image(url: str) -> bool:
    if not url.startswith(("https://", "http://")):
        return False
    path = unquote(urlsplit(url).path).lower()
    return path.endswith(IMAGE_EXTENSIONS) or "/special:filepath/" in path

def valid_image(data: bytes) -> bool:
    head = data[:1024].lstrip().lower()
    return (
        data.startswith(b"\x89PNG\r\n\x1a\n")
        or data.startswith(b"\xff\xd8\xff")
        or data.startswith((b"GIF87a", b"GIF89a"))
        or (data.startswith(b"RIFF") and data[8:12] == b"WEBP")
        or b"<svg" in head[:512]
        or b"ftypavif" in data[:32]
    )

def safe_request_url(url: str) -> str:
    parts = urlsplit(url)
    path = quote(parts.path, safe="/%:@!$&()*+,;=-._~")
    return urlunsplit((parts.scheme, parts.netloc, path, parts.query, ""))

def filename_for(url: str) -> str:
    base = unquote(urlsplit(url).path).rstrip("/").rsplit("/", 1)[-1] or "image"
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", base).strip("-._") or "image"
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:10]
    if not Path(safe).suffix:
        safe += ".img"
    return f"{digest}-{safe}"

def original_file_page(url: str) -> str:
    path = unquote(urlsplit(url).path)
    marker = "/Special:FilePath/"
    if marker.lower() in path.lower():
        filename = path[path.lower().index(marker.lower()) + len(marker):]
        return "https://en.touhouwiki.net/wiki/File:" + quote(filename.replace(" ", "_"), safe="()_-.'")
    return url

def candidate_urls(url: str) -> list[str]:
    """Prefer a direct MediaWiki media URL; Special:FilePath can block image fetches."""
    path = unquote(urlsplit(url).path)
    marker = "/Special:FilePath/"
    if marker.lower() in path.lower():
        name = path[path.lower().index(marker.lower()) + len(marker):].strip("/")
        # MediaWiki normalizes spaces to underscores before computing its MD5 upload path.
        normalized = name.replace(" ", "_")
        digest = hashlib.md5(normalized.encode("utf-8")).hexdigest()
        direct = (
            "https://en.touhouwiki.net/images/"
            + digest[0] + "/" + digest[:2] + "/"
            + quote(normalized, safe="-._()'!")
        )
        # The direct URL is most reliable. Retain Special:FilePath as a fallback.
        return [direct, url]
    return [url]


def referer_candidates(url: str) -> list[str]:
    parts = urlsplit(url)
    host = parts.netloc.lower()
    if "touhouwiki.net" in host:
        path = unquote(parts.path)
        marker = "/Special:FilePath/"
        if marker.lower() in path.lower():
            name = path[path.lower().index(marker.lower()) + len(marker):].strip("/").replace(" ", "_")
        else:
            name = path.rsplit("/", 1)[-1]
        return [
            "https://en.touhouwiki.net/wiki/File:" + quote(name, safe="-._()'!"),
            "https://en.touhouwiki.net/wiki/",
            "https://en.touhouwiki.net/",
        ]
    if host:
        return [f"{parts.scheme}://{parts.netloc}/"]
    return ["https://touhouarchive-web.github.io/"]


def download(url: str, destination: Path) -> tuple[int, str]:
    last_error: Exception | None = None
    tried: set[tuple[str, str]] = set()
    for candidate in candidate_urls(url):
        for referer in referer_candidates(url):
            if (candidate, referer) in tried:
                continue
            tried.add((candidate, referer))
            request = Request(
                safe_request_url(candidate),
                headers={
                    # Use normal browser image-request headers and a source-page referrer.
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/132.0.0.0 Safari/537.36"
                    ),
                    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
                    "Referer": referer,
                    "Sec-Fetch-Dest": "image",
                    "Sec-Fetch-Mode": "no-cors",
                    "Sec-Fetch-Site": "cross-site",
                },
            )
            try:
                with urlopen(request, timeout=60) as response:
                    data = response.read()
                    content_type = response.headers.get("Content-Type", "").lower()
                    final_url = response.geturl()
                if not valid_image(data) or "text/html" in content_type:
                    raise RuntimeError(
                        f"Expected image bytes but received {content_type or 'unknown content'} "
                        f"from {final_url} (requested {candidate})."
                    )
                if len(data) > 30 * 1024 * 1024:
                    raise RuntimeError(f"Image is unexpectedly large ({len(data)} bytes): {candidate}")
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
                return len(data), candidate
            except Exception as exc:
                last_error = exc
                print(f"  retrying image fetch after {candidate}: {exc}")
                time.sleep(0.2)
    raise RuntimeError(f"Could not download image referenced by {url}. Last error: {last_error}")

def main() -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    html_css_files = [
        p for p in ROOT.rglob("*")
        if p.is_file()
        and p.suffix.lower() in (".html", ".css")
        and "_site" not in p.parts
        and ".git" not in p.parts
        and "assets/images" not in p.as_posix()
    ]

    sources: dict[str, dict[str, str]] = {}
    for path in html_css_files:
        content = path.read_text(encoding="utf-8")
        urls = []
        if path.suffix.lower() == ".html":
            urls.extend(m.group("url") for m in IMG_SRC_RE.finditer(content))
        urls.extend(m.group("url").strip() for m in CSS_URL_RE.finditer(content))
        for url in urls:
            if is_external_image(url):
                sources.setdefault(url, {
                    "source_url": url,
                    "filename": unquote(urlsplit(url).path).rsplit("/", 1)[-1],
                    "source_page": original_file_page(url),
                    "asset_path": "/assets/images/" + filename_for(url),
                })

    if not sources:
        print("No external image references found; nothing to localize.")
        return

    total_bytes = 0
    for index, (url, metadata) in enumerate(sources.items(), start=1):
        destination = ROOT / metadata["asset_path"].lstrip("/")
        size, downloaded_from = download(url, destination)
        metadata["downloaded_from"] = downloaded_from
        total_bytes += size
        print(f"[{index}/{len(sources)}] {metadata['filename']}: {size:,} bytes from {downloaded_from}")
        time.sleep(0.08)

    for path in html_css_files:
        content = path.read_text(encoding="utf-8")

        def replace_img(match: re.Match[str]) -> str:
            url = match.group("url")
            if url in sources:
                return match.group("prefix") + match.group("quote") + sources[url]["asset_path"] + match.group("quote")
            return match.group(0)

        def replace_css_url(match: re.Match[str]) -> str:
            url = match.group("url").strip()
            if url in sources:
                q = match.group("quote")
                return "url(" + q + sources[url]["asset_path"] + q + ")"
            return match.group(0)

        if path.suffix.lower() == ".html":
            content = IMG_SRC_RE.sub(replace_img, content)
        content = CSS_URL_RE.sub(replace_css_url, content)
        path.write_text(content, encoding="utf-8")

    manifest = {
        "generated_at_build": True,
        "note": "Images are served locally by this site; each entry records its original source.",
        "images": list(sources.values()),
    }
    (IMAGE_DIR / "image-sources.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Localized {len(sources)} images ({total_bytes:,} bytes) into the Pages build artifact.")

if __name__ == "__main__":
    main()
