#!/usr/bin/env python3
"""Fetch subject-matched images at build time and publish them from this site's own origin."""
from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / "assets" / "images"
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".avif")
OFFICIAL_PAGE = "https://touhou-project.news/shanghai-alice-reprise/en/"
MOF_PAGE = "https://store.steampowered.com/app/1100140/Touhou_Fuujinroku_Mountain_of_Faith/"
COMMUNITY_PAGE = "https://aenigmatrices.github.io/touhou-translations/characters/"
REIMU = "https://touhou-project.news/shanghai-alice-reprise/assets/img/portrait-reimu.BiylHtpy_1VPyDX.webp"
MARISA = "https://touhou-project.news/shanghai-alice-reprise/assets/img/portrait-marisa.B67Swbrj_Z1cf0sQ.webp"
CIRNO = "https://touhou-project.news/shanghai-alice-reprise/assets/img/base-cirno.CUhB2vJK_1bPY3u.webp"
MEILING = "https://touhou-project.news/shanghai-alice-reprise/assets/img/base-meiling.D34IKjE1_2BaJ4.webp"
FLANDRE = "https://touhou-project.news/shanghai-alice-reprise/assets/img/base-flandre.CKaqfwDo_Z2uuf7S.webp"
COVER = "https://touhou-project.news/shanghai-alice-reprise/assets/img/cover-en.BwrTSYxk_Z3mJMl.webp"
SHOT_NEW = "https://touhou-project.news/shanghai-alice-reprise/assets/img/screenshot-new-classic-en.CCEiUnlW_ZBh8uq.webp"
SHOT_SYSTEM = "https://touhou-project.news/shanghai-alice-reprise/assets/img/screenshot-new-system-en.Bt1DWqMz_Z21uUX1.webp"
SHOT_CLASSIC = "https://touhou-project.news/shanghai-alice-reprise/assets/img/screenshot-classic.DogW9W-X_ZGos0F.webp"
TITLE_LOGO = "https://touhou-project.news/shanghai-alice-reprise/assets/img/logo-title-en.BRRxfPpf_ZKQ7cK.webp"
MOON_BG = "https://touhou-project.news/shanghai-alice-reprise/assets/img/bg-moon.S5PItN70_2rjpE2.webp"
FOG_1 = "https://touhou-project.news/shanghai-alice-reprise/assets/img/bg-fog-01.D2ZXdn5G_ZWbWPS.webp"
FOG_3 = "https://touhou-project.news/shanghai-alice-reprise/assets/img/bg-fog-03.DcIEzwCt_ZfSqE0.webp"
FOG_4 = "https://touhou-project.news/shanghai-alice-reprise/assets/img/bg-fog-04.CTd5y_SA_Z1gStYX.webp"
MOF_COVER = "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/1100140/capsule_616x353.jpg?t=1667958836"
MOF_BG = "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/1100140/page_bg_raw.jpg?t=1667958836"
MOF_HEADER = "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/1100140/header.jpg?t=1667958836"
MOF_COMMUNITY = "https://shared.akamai.steamstatic.com/community_assets/images/apps/1100140/802f806ca642360e40cc2405e8df8e93d83083af.jpg"
PMISS_COVER = "https://www.neowing.co.jp/pictures/l/02/03/NEOBK-395940.jpg?v=1"
FORBIDDEN_SCROLLERY = "https://images.yenpress.com/imgs/9780316511971.jpg?w=408&h=612&type=books&s=0e7823442f2a29bc6b0b8147a3b18fc1"
SILENT_SINNER = "https://shop.akbh.jp/cdn/shop/products/9784758060899.jpg?v=1722506128"
REMILIA_ART = "https://aenigmatrices.github.io/touhou-translations/_astro/remilia.DsxaxEe-_Z2t5UPm.webp"
AYA_ART = "https://aenigmatrices.github.io/touhou-translations/_astro/aya.Bs9Y13l-_ZWBqoJ.webp"
KANAKO_ART = "https://i.redd.it/zbb0y9ujn27g1.png"

# Each source is a subject-matched replacement for a blocked Touhou Wiki media file.
# Official game/publisher images are preferred; community images are explicitly credited.
IMAGE_ALIASES = {
    "Th06cover.jpg": {
        "url": COVER, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Official cover artwork for Touhou Koumakyou: the Embodiment of Scarlet Devil."
    },
    "Th06screenLayout.jpg": {
        "url": SHOT_NEW, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Gameplay screenshot from the official Touhou Koumakyou: New Classic website."
    },
    "Th10YoukaiMountain.jpg": {
        "url": MOF_BG, "source_page": MOF_PAGE, "credit": "Steam — Mountain of Faith",
        "alt": "Mountain of Faith store artwork, used as a representative visual for Youkai Mountain."
    },
    "Th06Reimu.png": {
        "url": REIMU, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Reimu Hakurei character portrait from the official Touhou Koumakyou: New Classic website."
    },
    "Th06titlescreen.jpg": {
        "url": TITLE_LOGO, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Title logo for the official Touhou Koumakyou: New Classic release."
    },
    "Thgscover.jpg": {
        "url": PMISS_COVER, "source_page": "https://www.neowing.co.jp/product/NEOBK-395940",
        "credit": "Neowing — Perfect Memento in Strict Sense",
        "alt": "Book cover for Perfect Memento in Strict Sense, the official Touhou reference book."
    },
    "Th105Reimu.png": {
        "url": REIMU, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Reimu Hakurei character portrait from the official Touhou Koumakyou: New Classic website."
    },
    "Th06stage1title.jpg": {
        "url": SHOT_CLASSIC, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Gameplay image from the official Touhou Koumakyou: New Classic site, used as stage-context imagery."
    },
    "Th10MoriyaShrineEntrance.jpg": {
        "url": MOF_COMMUNITY, "source_page": MOF_PAGE, "credit": "Steam — Mountain of Faith",
        "alt": "Mountain of Faith game artwork from Steam, used as representative imagery for the Moriya Shrine section."
    },
    "Th06stage2title.jpg": {
        "url": SHOT_SYSTEM, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Official Touhou Koumakyou gameplay screenshot, used as stage-context imagery."
    },
    "Th06stage3title.jpg": {
        "url": SHOT_NEW, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Official Touhou Koumakyou gameplay screenshot, used as soundtrack-related game imagery."
    },
    "FS Tankebon1 cover.jpg": {
        "url": FORBIDDEN_SCROLLERY, "source_page": "https://yenpress.com/titles/9780316511971-forbidden-scrollery-vol-1",
        "credit": "Yen Press — Forbidden Scrollery, Vol. 1",
        "alt": "Publisher cover for Forbidden Scrollery, volume 1, an official Touhou manga."
    },
    "Th06ScarletMoon.jpg": {
        "url": MOON_BG, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Moonlit background art from the official Touhou Koumakyou: New Classic website."
    },
    "Th06SDMInterior.jpg": {
        "url": FOG_4, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Atmospheric mist background from the official Touhou Koumakyou: New Classic website."
    },
    "Th06Marisa.png": {
        "url": MARISA, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Marisa Kirisame character portrait from the official Touhou Koumakyou: New Classic website."
    },
    "Th06SDMEntrance.jpg": {
        "url": FOG_3, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Atmospheric fog background from the official Touhou Koumakyou: New Classic website."
    },
    "Th105Hakugyokurou.jpg": {
        "url": MOON_BG, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Moonlit official Touhou background used as an atmospheric illustration for the Netherworld."
    },
    "Th105BambooForest.jpg": {
        "url": FOG_1, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Misty setting artwork from the official Touhou Koumakyou: New Classic website."
    },
    "Th10cover.jpg": {
        "url": MOF_COVER, "source_page": MOF_PAGE, "credit": "Steam — Mountain of Faith",
        "alt": "Store cover artwork for Touhou Fuujinroku: Mountain of Faith."
    },
    "Th06MistyLake.jpg": {
        "url": FOG_3, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Misty atmospheric background from the official Touhou Koumakyou: New Classic website."
    },
    "Th10YoukaiForest.jpg": {
        "url": MOF_BG, "source_page": MOF_PAGE, "credit": "Steam — Mountain of Faith",
        "alt": "Mountain of Faith store background, used as representative Gensokyo environment imagery."
    },
    "Th06stage4title.jpg": {
        "url": SHOT_SYSTEM, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Official Touhou Koumakyou gameplay screenshot, used as stage-context imagery."
    },
    "Th06stage6title.jpg": {
        "url": SHOT_CLASSIC, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Official Touhou Koumakyou gameplay screenshot, used to evoke a boss-stage setting."
    },
    "Th06Flandre.png": {
        "url": FLANDRE, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Flandre Scarlet character portrait from the official Touhou Koumakyou: New Classic website."
    },
    "Th06Remilia.png": {
        "url": REMILIA_ART, "source_page": "https://aenigmatrices.github.io/touhou-translations/gallery/characters/remilia/",
        "credit": "Touhou Translations — Remilia Scarlet community gallery",
        "alt": "Community illustration of Remilia Scarlet, sourced from the Touhou Translations character gallery."
    },
    "Th06stage5title.jpg": {
        "url": SHOT_NEW, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Official Touhou Koumakyou gameplay screenshot, used as stage-context imagery."
    },
    "Th06SDMLibrary1.jpg": {
        "url": FOG_4, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Atmospheric background art from the official Touhou Koumakyou: New Classic website, used as setting imagery."
    },
    "Th06SDMLibrary2.jpg": {
        "url": FOG_3, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Atmospheric fog background from the official Touhou Koumakyou: New Classic website."
    },
    "Th105Aya.png": {
        "url": AYA_ART, "source_page": "https://aenigmatrices.github.io/touhou-translations/gallery/characters/aya/",
        "credit": "Touhou Translations — Aya Shameimaru community gallery",
        "alt": "Community illustration of Aya Shameimaru, sourced from the Touhou Translations character gallery."
    },
    "Th10KanakoYasaka.png": {
        "url": KANAKO_ART, "source_page": "https://aenigmatrices.github.io/touhou-translations/gallery/characters/kanako/",
        "credit": "Touhou Translations — Kanako Yasaka community gallery",
        "alt": "Community image of Kanako Yasaka from the Touhou Translations character gallery."
    },
    "Th105HakureiShrineBird'sEye.jpg": {
        "url": MOF_COMMUNITY, "source_page": MOF_PAGE, "credit": "Steam — Mountain of Faith",
        "alt": "Mountain of Faith game artwork from Steam, used as representative setting imagery rather than a literal shrine map."
    },
    "Th01Cover.jpg": {
        "url": TITLE_LOGO, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Official Touhou title artwork used as a visual marker in the chronology section."
    },
}
# External publisher/retailer image used in the current HTML already has a real product source.
IMAGE_ALIASES["9784758060899.jpg"] = {
    "url": SILENT_SINNER, "source_page": "https://shop.akbh.jp/en/products/9784758060899",
    "credit": "AKIBA-HOBBY — Silent Sinner in Blue, Vol. 1",
    "alt": "Publisher/retailer cover image for Silent Sinner in Blue, volume 1."
}

# Alternatives keep the workflow resilient if one image host blocks automated downloads.
FALLBACKS = {
    OFFICIAL_PAGE: [COVER, SHOT_NEW, SHOT_SYSTEM, SHOT_CLASSIC, MOON_BG, FOG_1, FOG_3, FOG_4],
    MOF_PAGE: [MOF_COVER, MOF_BG, MOF_HEADER, SHOT_NEW, FOG_1],
    "https://aenigmatrices.github.io/touhou-translations/gallery/characters/remilia/": [REMILIA_ART, FOG_4, MOON_BG],
    "https://aenigmatrices.github.io/touhou-translations/gallery/characters/aya/": [AYA_ART, FOG_3, SHOT_SYSTEM],
    "https://aenigmatrices.github.io/touhou-translations/gallery/characters/kanako/": [KANAKO_ART, MOF_BG, FOG_1],
    "https://www.neowing.co.jp/product/NEOBK-395940": [PMISS_COVER, FORBIDDEN_SCROLLERY, COVER],
    "https://yenpress.com/titles/9780316511971-forbidden-scrollery-vol-1": [FORBIDDEN_SCROLLERY, PMISS_COVER, COVER],
    "https://shop.akbh.jp/en/products/9784758060899": [SILENT_SINNER, FORBIDDEN_SCROLLERY, COVER],
}

# Associate each known alias URL with its source page and readable credit.
URL_CREDIT = {}
for fname, m in IMAGE_ALIASES.items():
    URL_CREDIT.setdefault(m["url"], {"source_page": m["source_page"], "credit": m["credit"], "alt": m["alt"]})
for url in [COVER, SHOT_NEW, SHOT_SYSTEM, SHOT_CLASSIC, TITLE_LOGO, MOON_BG, FOG_1, FOG_3, FOG_4]:
    URL_CREDIT.setdefault(url, {"source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site", "alt": "Official Touhou New Classic promotional artwork."})
for url in [MOF_COVER, MOF_BG, MOF_HEADER, MOF_COMMUNITY]:
    URL_CREDIT.setdefault(url, {"source_page": MOF_PAGE, "credit": "Steam — Mountain of Faith", "alt": "Mountain of Faith store artwork."})
URL_CREDIT.setdefault(PMISS_COVER, {"source_page": "https://www.neowing.co.jp/product/NEOBK-395940", "credit": "Neowing", "alt": "Perfect Memento in Strict Sense cover."})
URL_CREDIT.setdefault(FORBIDDEN_SCROLLERY, {"source_page": "https://yenpress.com/titles/9780316511971-forbidden-scrollery-vol-1", "credit": "Yen Press", "alt": "Forbidden Scrollery, volume 1 cover."})
URL_CREDIT.setdefault(SILENT_SINNER, {"source_page": "https://shop.akbh.jp/en/products/9784758060899", "credit": "AKIBA-HOBBY", "alt": "Silent Sinner in Blue, volume 1 cover."})
URL_CREDIT.setdefault(REMILIA_ART, {"source_page": "https://aenigmatrices.github.io/touhou-translations/gallery/characters/remilia/", "credit": "Touhou Translations community gallery", "alt": "Community illustration of Remilia Scarlet."})
URL_CREDIT.setdefault(AYA_ART, {"source_page": "https://aenigmatrices.github.io/touhou-translations/gallery/characters/aya/", "credit": "Touhou Translations community gallery", "alt": "Community illustration of Aya Shameimaru."})
URL_CREDIT.setdefault(KANAKO_ART, {"source_page": "https://aenigmatrices.github.io/touhou-translations/gallery/characters/kanako/", "credit": "Touhou Translations community gallery", "alt": "Community illustration featuring Kanako Yasaka."})

IMG_TAG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE | re.DOTALL)
IMG_SRC_RE = re.compile(r'\bsrc\s*=\s*(["\'])(.*?)\1', re.IGNORECASE | re.DOTALL)
CSS_URL_RE = re.compile(r'url\(\s*(?P<quote>["\']?)(?P<url>https?://[^)"\']+)(?P=quote)\s*\)', re.IGNORECASE)
FILE_LINK_RE = re.compile(r'<a\s+href="https://en\.touhouwiki\.net/wiki/File:([^"]+)"([^>]*)>Touhou Wiki file ↗</a>', re.IGNORECASE)


def wiki_filename(url: str) -> str | None:
    path = unquote(urlsplit(url).path)
    marker = "/Special:FilePath/"
    if marker.lower() not in path.lower():
        return None
    return path[path.lower().index(marker.lower()) + len(marker):].strip("/").replace("_", " ")


def is_external_image(url: str) -> bool:
    if not url.startswith(("https://", "http://")):
        return False
    path = unquote(urlsplit(url).path).lower()
    return path.endswith(IMAGE_EXTENSIONS) or "/special:filepath/" in path


def resolve_source(url: str) -> dict[str, str | list[str]]:
    name = wiki_filename(url)
    if name and name in IMAGE_ALIASES:
        result = dict(IMAGE_ALIASES[name])
        result["reference_url"] = url
        result["original_name"] = name
        result["fallback_urls"] = list(FALLBACKS.get(result["source_page"], []))
        return result
    basename = unquote(urlsplit(url).path).rstrip("/").rsplit("/", 1)[-1]
    if basename in IMAGE_ALIASES:
        result = dict(IMAGE_ALIASES[basename])
        result["reference_url"] = url
        result["original_name"] = basename
        result["fallback_urls"] = list(FALLBACKS.get(result["source_page"], []))
        return result
    if name:
        # Any unexpected Wiki redirect must still not reach the blocked host.
        result = dict(IMAGE_ALIASES["Th06SDMInterior.jpg"])
        result["reference_url"] = url
        result["original_name"] = name
        result["alt"] = "Atmospheric Touhou promotional background used as illustrative setting art."
        result["fallback_urls"] = list(FALLBACKS.get(result["source_page"], []))
        return result
    result = {
        "url": url,
        "source_page": url,
        "credit": urlsplit(url).netloc or "External image source",
        "alt": "Touhou-related image hosted by the source shown in the image credits.",
        "reference_url": url,
        "original_name": basename,
        "fallback_urls": [],
    }
    if "shop.akbh.jp" in url:
        result.update(IMAGE_ALIASES["9784758060899.jpg"])
        result["reference_url"] = url
        result["original_name"] = basename
    return result


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


def filename_for(url: str) -> str:
    parts = urlsplit(url)
    base = unquote(parts.path).rstrip("/").rsplit("/", 1)[-1] or "image"
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", base).strip("-._") or "image"
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:10]
    if not Path(safe).suffix:
        safe += ".img"
    return f"{digest}-{safe}"


def download_one(url: str, destination: Path, referer: str) -> int:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "Referer": referer,
        },
    )
    with urlopen(request, timeout=45) as response:
        data = response.read()
        content_type = response.headers.get("Content-Type", "").lower()
        final_url = response.geturl()
    if not valid_image(data) or "text/html" in content_type:
        raise RuntimeError(f"Expected image bytes but received {content_type or 'unknown content'} from {final_url}.")
    if len(data) > 30 * 1024 * 1024:
        raise RuntimeError(f"Image is unexpectedly large ({len(data)} bytes): {url}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    return len(data)


def download(source: dict[str, str | list[str]], destination: Path) -> tuple[int, str, dict[str, str]]:
    primary = str(source["url"])
    source_page = str(source["source_page"])
    attempts = [primary]
    attempts.extend(str(u) for u in source.get("fallback_urls", []) if str(u) != primary)
    seen: set[str] = set()
    errors: list[str] = []
    for candidate in attempts:
        if candidate in seen:
            continue
        seen.add(candidate)
        credit = URL_CREDIT.get(candidate, {"source_page": source_page, "credit": str(source["credit"]), "alt": str(source["alt"])})
        parts = urlsplit(candidate)
        referer = str(credit.get("source_page") or (f"{parts.scheme}://{parts.netloc}/"))
        temp_destination = destination.with_name(filename_for(candidate))
        try:
            size = download_one(candidate, temp_destination, referer)
            return size, candidate, {
                "source_page": str(credit["source_page"]),
                "credit": str(credit["credit"]),
                "alt": str(credit["alt"]),
            }
        except Exception as exc:
            errors.append(f"{candidate}: {exc}")
            print(f"  alternate source needed for {candidate}: {exc}")
            time.sleep(0.15)
    raise RuntimeError("All candidate image sources failed: " + " | ".join(errors))


def rewrite_sources_section(content: str) -> str:
    content = content.replace(
        "Image assets are downloaded during the GitHub Pages build and served from this site’s own /assets/images/ path, so visitors’ browsers no longer hotlink to Touhou Wiki or retailer image hosts. Captions and the list below still link back to the original file and source pages.",
        "Displayed images are downloaded during the GitHub Pages build and served from this website’s own /assets/images/ path. A visitor’s browser therefore never hotlinks directly to Touhou Wiki or another image host. Image captions link to the actual source page for the displayed visual."
    )
    content = content.replace(
        "Touhou Wiki’s file pages identify the source and any licensing information provided for each image. Image rights can differ by file, and many assets depict copyrighted Touhou characters or game art. Check the individual file page and applicable rights before reusing an image elsewhere. One book cover on the print-works page remains linked to its retailer listing for accurate bibliographic identification.",
        "The site uses official promotional/game imagery where available, publisher or retailer cover images for print works, and a small number of clearly labelled community illustrations for characters absent from the official promotional materials. Rights remain with the respective creators and publishers; credit links identify the displayed image’s source, and inclusion here does not imply that every image has a blanket reuse licence."
    )
    credits = """<h3>Image sources used</h3><ul class="source-list">
<li><a href="https://touhou-project.news/shanghai-alice-reprise/en/" target="_blank" rel="noopener"><strong>Touhou Koumakyou: New Classic — official site</strong></a><br>Official promotional character portraits, game screenshots, and atmospheric backgrounds.</li>
<li><a href="https://store.steampowered.com/app/1100140/Touhou_Fuujinroku_Mountain_of_Faith/" target="_blank" rel="noopener"><strong>Steam — Touhou Fuujinroku: Mountain of Faith</strong></a><br>Game cover and official store/game imagery used on the games and locations pages.</li>
<li><a href="https://www.neowing.co.jp/product/NEOBK-395940" target="_blank" rel="noopener"><strong>Neowing — Perfect Memento in Strict Sense</strong></a><br>Retail cover image used for bibliographic identification of the official reference book.</li>
<li><a href="https://yenpress.com/titles/9780316511971-forbidden-scrollery-vol-1" target="_blank" rel="noopener"><strong>Yen Press — Forbidden Scrollery, Volume 1</strong></a><br>Publisher cover image for the official Touhou manga.</li>
<li><a href="https://shop.akbh.jp/en/products/9784758060899" target="_blank" rel="noopener"><strong>AKIBA-HOBBY — Silent Sinner in Blue, Volume 1</strong></a><br>Retail cover image used to identify the print work.</li>
<li><a href="https://aenigmatrices.github.io/touhou-translations/gallery/characters/remilia/" target="_blank" rel="noopener"><strong>Touhou Translations — Remilia Scarlet community gallery</strong></a>, <a href="https://aenigmatrices.github.io/touhou-translations/gallery/characters/aya/" target="_blank" rel="noopener"><strong>Aya Shameimaru gallery</strong></a>, and <a href="https://aenigmatrices.github.io/touhou-translations/gallery/characters/kanako/" target="_blank" rel="noopener"><strong>Kanako Yasaka gallery</strong></a><br>Community images are labelled as such and are not presented as official character artwork. Please consult the linked galleries for their creator and usage information.</li>
</ul>"""
    content = re.sub(
        r'<h3>Individual Touhou Wiki image files used</h3><ul class="source-list">.*?</ul>',
        credits,
        content,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return content


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

    references: dict[str, dict[str, str | list[str]]] = {}
    for path in html_css_files:
        content = path.read_text(encoding="utf-8")
        urls: list[str] = []
        if path.suffix.lower() == ".html":
            urls.extend(m.group(2) for tag in IMG_TAG_RE.findall(content) if (m := IMG_SRC_RE.search(tag)))
        urls.extend(m.group("url").strip() for m in CSS_URL_RE.finditer(content))
        for url in urls:
            if is_external_image(url):
                references.setdefault(url, resolve_source(url))

    if not references:
        print("No external image references found; nothing to localize.")
        return

    downloaded: dict[str, dict[str, str | int]] = {}
    total_bytes = 0
    for index, (reference_url, source) in enumerate(references.items(), start=1):
        primary_url = str(source["url"])
        expected_filename = filename_for(primary_url)
        destination = IMAGE_DIR / expected_filename
        if primary_url not in downloaded:
            size, actual_url, actual_credit = download(source, destination)
            actual_filename = filename_for(actual_url)
            # download() writes under a per-source temporary name; consolidate to a predictable output name.
            actual_path = IMAGE_DIR / actual_filename
            final_path = IMAGE_DIR / expected_filename
            if actual_path.exists() and actual_path != final_path:
                final_path.write_bytes(actual_path.read_bytes())
                actual_path.unlink()
            elif not final_path.exists():
                raise RuntimeError(f"Image download did not create the expected local asset for {reference_url}")
            downloaded[primary_url] = {
                "bytes": size,
                "downloaded_from": actual_url,
                "source_page": actual_credit["source_page"],
                "credit": actual_credit["credit"],
                "alt": actual_credit["alt"],
                "asset_path": "/assets/images/" + expected_filename,
            }
            total_bytes += size
            print(f"[{index}/{len(references)}] {source['original_name']}: {size:,} bytes from {actual_url}")
        asset = downloaded[primary_url]
        source["asset_path"] = str(asset["asset_path"])
        source["downloaded_from"] = str(asset["downloaded_from"])
        source["actual_source_page"] = str(asset["source_page"])
        source["actual_credit"] = str(asset["credit"])
        source["actual_alt"] = str(asset["alt"])

    def replace_image_tag(match: re.Match[str]) -> str:
        tag = match.group(0)
        src_match = IMG_SRC_RE.search(tag)
        if not src_match:
            return tag
        original_url = src_match.group(2)
        meta = references.get(original_url)
        if not meta:
            return tag
        quote_char = src_match.group(1)
        local_path = str(meta["asset_path"])
        tag = tag[:src_match.start(2)] + local_path + tag[src_match.end(2):]
        if "actual_alt" in meta:
            alt_text = str(meta["actual_alt"]).replace("&", "&amp;").replace('"', "&quot;")
            if re.search(r'\balt\s*=\s*(["\']).*?\1', tag, re.IGNORECASE | re.DOTALL):
                tag = re.sub(r'\balt\s*=\s*(["\']).*?\1', f'alt="{alt_text}"', tag, count=1, flags=re.IGNORECASE | re.DOTALL)
            else:
                tag = tag[:-1] + f' alt="{alt_text}">'
        credit = str(meta.get("actual_credit", meta["credit"])).replace("&", "&amp;").replace('"', "&quot;")
        if re.search(r'\btitle\s*=\s*(["\']).*?\1', tag, re.IGNORECASE | re.DOTALL):
            tag = re.sub(r'\btitle\s*=\s*(["\']).*?\1', f'title="Image source: {credit}"', tag, count=1, flags=re.IGNORECASE | re.DOTALL)
        else:
            tag = tag[:-1] + f' title="Image source: {credit}">'
        # Remove stale wiki-specific metadata to avoid suggesting a substituted asset is the wiki file.
        tag = re.sub(r'\sdata-wiki-file=(["\']).*?\1', "", tag, flags=re.IGNORECASE | re.DOTALL)
        return tag

    def replace_css_url(match: re.Match[str]) -> str:
        original_url = match.group("url").strip()
        meta = references.get(original_url)
        if not meta:
            return match.group(0)
        quote_char = match.group("quote")
        return "url(" + quote_char + str(meta["asset_path"]) + quote_char + ")"

    for path in html_css_files:
        content = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".html":
            content = IMG_TAG_RE.sub(replace_image_tag, content)
            def replace_file_link(match: re.Match[str]) -> str:
                name = unquote(match.group(1)).replace("_", " ")
                meta = IMAGE_ALIASES.get(name)
                if not meta:
                    return match.group(0)
                href = str(meta["source_page"]).replace("&", "&amp;").replace('"', "&quot;")
                credit = str(meta["credit"]).replace("&", "&amp;")
                return f'<a href="{href}" target="_blank" rel="noopener">{credit} ↗</a>'

            content = FILE_LINK_RE.sub(replace_file_link, content)
            if path.name == "sources.html":
                content = rewrite_sources_section(content)
        content = CSS_URL_RE.sub(replace_css_url, content)
        path.write_text(content, encoding="utf-8")

    manifest = {
        "generated_at_build": True,
        "note": "All displayed images are served from this site; each record lists the actual download host and source page.",
        "images": [
            {
                "reference_url": ref,
                "reference_name": meta.get("original_name"),
                "downloaded_from": meta.get("downloaded_from"),
                "source_page": meta.get("actual_source_page", meta.get("source_page")),
                "credit": meta.get("actual_credit", meta.get("credit")),
                "local_path": meta.get("asset_path"),
            }
            for ref, meta in references.items()
        ],
    }
    (IMAGE_DIR / "image-sources.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Localized {len(references)} image references ({total_bytes:,} total bytes) into same-origin assets.")

if __name__ == "__main__":
    main()
