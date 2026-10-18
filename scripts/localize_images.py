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

def download(url: str, destination: Path) -> int:
    request = Request(
        safe_request_url(url),
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; TouhouArchive/1.0)",
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        },
    )
    with urlopen(request, timeout=60) as response:
        data = response.read()
        content_type = response.headers.get("Content-Type", "").lower()
        final_url = response.geturl()
    if not valid_image(data) or "text/html" in content_type:
        raise RuntimeError(
            f"Expected image bytes but received {content_type or 'unknown content'} "
            f"from {final_url} (requested {url}); refusing to publish a broken image."
        )
    if len(data) > 30 * 1024 * 1024:
        raise RuntimeError(f"Image is unexpectedly large ({len(data)} bytes): {url}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    return len(data)

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
        size = download(url, destination)
        total_bytes += size
        print(f"[{index}/{len(sources)}] {metadata['filename']}: {size:,} bytes")
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
