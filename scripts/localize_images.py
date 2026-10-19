#!/usr/bin/env python3
"""Fetch subject-matched images at build time and publish them from this site's own origin."""
from __future__ import annotations

import hashlib
import html
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
EOSD_LB_PAGE = "https://gamesdb.launchbox-app.com/games/images/7337-touhou-06-the-embodiment-of-scarlet-devil"
PCB_LB_PAGE = "https://gamesdb.launchbox-app.com/games/images/7341-touhou-07-perfect-cherry-blossom"
IN_LB_PAGE = "https://gamesdb.launchbox-app.com/games/images/7347-touhou-08-imperishable-night"
PC98_LB_PAGE = "https://gamesdb.launchbox-app.com/games/images/72360-touhou-01-the-highly-responsive-to-prayers"
MOF_LB_PAGE = "https://gamesdb.launchbox-app.com/games/images/7363-touhou-10-mountain-of-faith"
EOSD_COVER = "https://images.launchbox-app.com/8669e740-a842-45ca-8de6-d33fef9d765b.jpg"
EOSD_GAMEPLAY = "https://images.launchbox-app.com/a5fe3f9e-74ed-45c9-8b47-b4c7d445ca42.png"
EOSD_GAMEPLAY_ALT = "https://images.launchbox-app.com/0877ceaa-5c69-4b68-a31b-460e9706879d.jpg"
EOSD_GAMESELECT = "https://images.launchbox-app.com/3c8c7bf7-ab39-434f-89c1-c0f15297bc6b.png"
EOSD_BG_1 = "https://images.launchbox-app.com/fa2f9c66-2f13-4635-99d9-a7c07c140cdb.jpg"
EOSD_GAMEOVER = "https://images.launchbox-app.com/108f181f-01d2-4bf4-b147-3033f86d7a80.png"
EOSD_BG_2 = "https://images.launchbox-app.com/12a38156-8dbf-435d-8f3b-07931d943e3c.png"
EOSD_TITLE = "https://images.launchbox-app.com/4293464b-03ef-4acc-9782-2cefc1d724bb.png"
PCB_COVER = "https://images.launchbox-app.com/b16b0e15-aa40-466c-933e-b32a334703e9.jpg"
PCB_GAMEPLAY = "https://images.launchbox-app.com/b0bbe39f-cd11-4124-b85b-81f779064819.jpg"
PCB_BG = "https://images.launchbox-app.com/2375b680-83fc-44cf-980b-03a2b20730b4.jpg"
IN_COVER = "https://images.launchbox-app.com/b148dcbf-19a9-4d7d-937e-8c5ee85522b2.jpg"
IN_GAMEPLAY = "https://images.launchbox-app.com/cb6adb01-2500-45fb-a7ed-b668b23d8596.jpg"
IN_BG = "https://images.launchbox-app.com/3f215b25-d781-4aac-9798-4eb5a4272110.jpg"
PC98_COVER = "https://images.launchbox-app.com/r2_edfdd1dc-9837-4062-ade8-ee267097c3c1.png"
PC98_GAMEPLAY = "https://images.launchbox-app.com/f6a6647b-0ca8-4336-b331-92be51622ad8.png"
MOF_LB_COVER = "https://images.launchbox-app.com/de77b746-5bd3-4e59-b25a-287ebb80fa05.jpg"
MOF_LB_GAMEPLAY = "https://images.launchbox-app.com/501440fd-ec5b-4313-aedc-0ece45e15d0a.jpg"
MOF_LB_BG = "https://images.launchbox-app.com/fd02b35c-1c38-4885-b2c4-5bab08ff8e4c.jpg"
SA_BG = "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1100150/page_bg_raw.jpg?t=1668044738"
UFO_BG = "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1100160/page_bg_raw.jpg?t=1668044181"
TD_BG = "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/1043230/page_bg_raw.jpg?t=1667959374"
DDC_BG = "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/1043240/page_bg_raw.jpg?t=1667958801"
UM_GAMEPLAY = "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/1566410/ss_15d15f3a77af97854472272613889fbef273f158.1920x1080.jpg?t=1621839528"
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
        "url": EOSD_COVER, "source_page": EOSD_LB_PAGE, "credit": "LaunchBox Games Database — Touhou 6: Embodiment of Scarlet Devil",
        "alt": "Original Japanese box-front artwork for Touhou 6: Embodiment of Scarlet Devil."
    },
    "Th06screenLayout.jpg": {
        "url": EOSD_GAMEPLAY, "source_page": EOSD_LB_PAGE, "credit": "LaunchBox Games Database — Touhou 6: Embodiment of Scarlet Devil",
        "alt": "Gameplay screenshot of Touhou 6: Embodiment of Scarlet Devil."
    },
    "Th10YoukaiMountain.jpg": {
        "url": MOF_LB_BG, "source_page": MOF_LB_PAGE, "credit": "LaunchBox Games Database — Touhou 10: Mountain of Faith",
        "alt": "Background artwork associated with Touhou 10: Mountain of Faith, used to illustrate Youkai Mountain."
    },
    "Th06Reimu.png": {
        "url": REIMU, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Reimu Hakurei character portrait from the official Touhou Koumakyou: New Classic website."
    },
    "Th06titlescreen.jpg": {
        "url": EOSD_TITLE, "source_page": EOSD_LB_PAGE, "credit": "LaunchBox Games Database — Touhou 6: Embodiment of Scarlet Devil",
        "alt": "Title-screen image from Touhou 6: Embodiment of Scarlet Devil."
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
        "url": EOSD_GAMEPLAY_ALT, "source_page": EOSD_LB_PAGE, "credit": "LaunchBox Games Database — Touhou 6: Embodiment of Scarlet Devil",
        "alt": "Gameplay screenshot from Touhou 6: Embodiment of Scarlet Devil."
    },
    "Th10MoriyaShrineEntrance.jpg": {
        "url": MOF_BG, "source_page": MOF_PAGE, "credit": "Steam — Mountain of Faith",
        "alt": "Official Mountain of Faith landscape artwork used as representative Gensokyo setting imagery."
    },
    "Th06stage2title.jpg": {
        "url": EOSD_GAMEPLAY, "source_page": EOSD_LB_PAGE, "credit": "LaunchBox Games Database — Touhou 6: Embodiment of Scarlet Devil",
        "alt": "Gameplay screenshot from Touhou 6: Embodiment of Scarlet Devil, showing danmaku patterns rather than a title logo."
    },
    "Th06stage3title.jpg": {
        "url": "https://images.launchbox-app.com/1da13c92-9a5d-4bc7-8328-9432948f9e64.png",
        "source_page": EOSD_LB_PAGE, "credit": "LaunchBox Games Database — Touhou 6: Embodiment of Scarlet Devil",
        "alt": "Disc artwork associated with Touhou 6: Embodiment of Scarlet Devil, reserved for the music-and-themes collection."
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
        "url": EOSD_BG_2, "source_page": EOSD_LB_PAGE, "credit": "LaunchBox Games Database — Touhou 6 artwork",
        "alt": "Community-contributed background artwork associated with Touhou 6, used for atmosphere rather than as a verified floor plan."
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
        "url": PCB_COVER, "source_page": PCB_LB_PAGE, "credit": "LaunchBox Games Database — Touhou 7: Perfect Cherry Blossom",
        "alt": "Original box-front artwork for Touhou 7: Perfect Cherry Blossom."
    },
    "Th105BambooForest.jpg": {
        "url": IN_COVER, "source_page": IN_LB_PAGE, "credit": "LaunchBox Games Database — Touhou 8: Imperishable Night",
        "alt": "Original box-front artwork for Touhou 8: Imperishable Night."
    },
    "Th10cover.jpg": {
        "url": MOF_LB_COVER, "source_page": MOF_LB_PAGE, "credit": "LaunchBox Games Database — Touhou 10: Mountain of Faith",
        "alt": "Original Japanese box-front artwork for Touhou 10: Mountain of Faith."
    },
    "Th06MistyLake.jpg": {
        "url": MOON_BG, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Moonlit and misty atmospheric background from the official Touhou Koumakyou: New Classic website, used to evoke the Misty Lake."
    },
    "Th10YoukaiForest.jpg": {
        "url": MOF_BG, "source_page": MOF_PAGE, "credit": "Steam — Mountain of Faith",
        "alt": "Official Mountain of Faith store background artwork, used as representative Gensokyo scenery."
    },
    "Th06stage4title.jpg": {
        "url": EOSD_GAMEOVER, "source_page": EOSD_LB_PAGE, "credit": "LaunchBox Games Database — Touhou 6: Embodiment of Scarlet Devil",
        "alt": "Game-over screen from Touhou 6: Embodiment of Scarlet Devil, used to illustrate game-state terminology."
    },
    "Th06stage6title.jpg": {
        "url": SHOT_CLASSIC, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Classic-mode gameplay screenshot from the official Touhou Koumakyou: New Classic website."
    },
    "Th06Cirno.png": {
        "url": CIRNO, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Cirno character portrait from the official Touhou Koumakyou: New Classic website."
    },
    "Th06Meiling.png": {
        "url": MEILING, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Hong Meiling character portrait from the official Touhou Koumakyou: New Classic website."
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
        "url": EOSD_TITLE, "source_page": EOSD_LB_PAGE, "credit": "LaunchBox Games Database — Touhou 6: Embodiment of Scarlet Devil",
        "alt": "Title-screen image from Touhou 6: Embodiment of Scarlet Devil, used for game-history context."
    },
    "Th06SDMLibrary1.jpg": {
        "url": FOG_4, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Atmospheric background art from the official Touhou Koumakyou: New Classic website, used as setting imagery."
    },
    "Th06SDMLibrary2.jpg": {
        "url": FOG_1, "source_page": OFFICIAL_PAGE, "credit": "Official Touhou New Classic site",
        "alt": "Distinct misty background art from the official Touhou Koumakyou: New Classic website."
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
        "alt": "Mountain of Faith game artwork used as illustrative Gensokyo scenery rather than a literal shrine map."
    },
    "Th01Cover.jpg": {
        "url": PC98_COVER, "source_page": PC98_LB_PAGE, "credit": "LaunchBox Games Database — Touhou 1: Highly Responsive to Prayers",
        "alt": "Japanese box-front artwork for Touhou 1: Highly Responsive to Prayers, the first Touhou game."
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
    EOSD_LB_PAGE: [EOSD_COVER, EOSD_GAMEPLAY, EOSD_GAMEPLAY_ALT, EOSD_TITLE, EOSD_GAMESELECT],
    PCB_LB_PAGE: [PCB_COVER, PCB_GAMEPLAY, PCB_BG],
    IN_LB_PAGE: [IN_COVER, IN_GAMEPLAY, IN_BG],
    PC98_LB_PAGE: [PC98_COVER, PC98_GAMEPLAY],
    MOF_LB_PAGE: [MOF_LB_COVER, MOF_LB_GAMEPLAY, MOF_LB_BG],
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
for url in [EOSD_COVER, EOSD_GAMEPLAY, EOSD_GAMEPLAY_ALT, EOSD_GAMESELECT, EOSD_BG_1, EOSD_GAMEOVER, EOSD_BG_2, EOSD_TITLE]:
    URL_CREDIT.setdefault(url, {"source_page": EOSD_LB_PAGE, "credit": "LaunchBox Games Database — Touhou 6: Embodiment of Scarlet Devil", "alt": "Touhou 6 game artwork or screenshot."})
for url in [PCB_COVER, PCB_GAMEPLAY, PCB_BG]:
    URL_CREDIT.setdefault(url, {"source_page": PCB_LB_PAGE, "credit": "LaunchBox Games Database — Touhou 7: Perfect Cherry Blossom", "alt": "Touhou 7 game artwork."})
for url in [IN_COVER, IN_GAMEPLAY, IN_BG]:
    URL_CREDIT.setdefault(url, {"source_page": IN_LB_PAGE, "credit": "LaunchBox Games Database — Touhou 8: Imperishable Night", "alt": "Touhou 8 game artwork."})
for url in [PC98_COVER, PC98_GAMEPLAY]:
    URL_CREDIT.setdefault(url, {"source_page": PC98_LB_PAGE, "credit": "LaunchBox Games Database — Touhou 1: Highly Responsive to Prayers", "alt": "PC-98-era Touhou game artwork."})
for url in [MOF_LB_COVER, MOF_LB_GAMEPLAY, MOF_LB_BG]:
    URL_CREDIT.setdefault(url, {"source_page": MOF_LB_PAGE, "credit": "LaunchBox Games Database — Touhou 10: Mountain of Faith", "alt": "Touhou 10 game artwork."})



# A researched pool of distinct, subject-matched images gathered from each game's
# LaunchBox media gallery, official Steam store pages, official Touhou promotional
# material, and publisher/retailer book listings. A selected URL is used only once
# outside the character portraits, preventing duplicated non-character artwork.
DIVERSE_IMAGE_CATALOG: list[dict[str, str]] = []
_CATALOG_IMAGE_KEYS: set[str] = set()


def _image_identity(url: str) -> str:
    parts = urlsplit(url)
    return parts.netloc.lower() + unquote(parts.path)


def register_game_gallery(game: str, title: str, page: str, images: list[tuple[str, str]]) -> None:
    for url, label in images:
        identity = _image_identity(url)
        if identity in _CATALOG_IMAGE_KEYS:
            continue
        _CATALOG_IMAGE_KEYS.add(identity)
        lower_label = label.lower()
        if "screenshot" in lower_label:
            kind = "screenshot"
            alt = f"{label} from {title}."
        elif "fanart - background" in lower_label:
            kind = "background"
            alt = f"Community-contributed background artwork catalogued for {title}."
        elif "clear logo" in lower_label:
            kind = "logo"
            alt = f"Game logo artwork for {title}."
        elif "disc" in lower_label:
            kind = "disc"
            alt = f"Disc artwork for {title}."
        elif "box" in lower_label:
            kind = "cover"
            alt = f"Game packaging artwork for {title}."
        elif "banner" in lower_label:
            kind = "background"
            alt = f"Banner artwork for {title}."
        else:
            kind = "artwork"
            alt = f"Game artwork catalogued for {title}."
        record = {
            "url": url, "source_page": page,
            "credit": f"LaunchBox Games Database — {title}",
            "game": game, "kind": kind, "alt": alt,
            "label": label, "title": title,
        }
        DIVERSE_IMAGE_CATALOG.append(record)
        URL_CREDIT[url] = {
            "source_page": page, "credit": record["credit"], "alt": alt
        }


def register_custom_image(url: str, page: str, credit: str, game: str, kind: str, alt: str) -> None:
    identity = _image_identity(url)
    if identity in _CATALOG_IMAGE_KEYS:
        return
    _CATALOG_IMAGE_KEYS.add(identity)
    record = {
        "url": url, "source_page": page, "credit": credit,
        "game": game, "kind": kind, "alt": alt,
        "label": kind, "title": credit,
    }
    DIVERSE_IMAGE_CATALOG.append(record)
    URL_CREDIT[url] = {"source_page": page, "credit": credit, "alt": alt}


register_game_gallery("th01", "Touhou 1: Highly Responsive to Prayers",
    "https://gamesdb.launchbox-app.com/games/images/72360-touhou-01-the-highly-responsive-to-prayers", [
    (PC98_COVER, "Box - Front (Japan)"), (PC98_GAMEPLAY, "Screenshot - Gameplay (World)"),
    ("https://images.launchbox-app.com/7ffb213e-7532-44a7-afdc-b6edaed8afa5.png", "Fanart - Background"),
    ("https://images.launchbox-app.com/376c2162-6416-4095-b351-decd11073032.png", "Box - 3D"),
    ("https://images.launchbox-app.com/d54f1a2d-767a-438a-ae2a-3cf10615ba52.png", "Fanart - Box - Front"),
    ("https://images.launchbox-app.com/df3d8eca-408d-4abe-8e1d-a7c5b53626ee.png", "Clear Logo"),
    ("https://images.launchbox-app.com/39a45dac-81ee-4075-8717-9ab9fbf71c32.jpg", "Screenshot - Game Title"),
    ("https://images.launchbox-app.com/97d47218-3b70-42dc-8e98-c9d2845e3496.png", "Screenshot - Gameplay"),
])
register_game_gallery("th02", "Touhou 2: The Story of Eastern Wonderland",
    "https://gamesdb.launchbox-app.com/games/images/75780-touhou-02-the-story-of-eastern-wonderland", [
    ("https://images.launchbox-app.com/r2_f362b8ea-e9c5-4cd4-9aa9-f8ee2237b6c6.png", "Box - Front (Japan)"),
    ("https://images.launchbox-app.com/40336462-1c4f-4d7f-b6ce-ead01d3d9144.jpg", "Fanart - Background"),
    ("https://images.launchbox-app.com/0363e6f7-8295-472b-8faf-5bc8577f7790.png", "Box - 3D"),
    ("https://images.launchbox-app.com/ccf7d764-4975-4c7c-b4f7-95aefc79f01c.png", "Fanart - Disc"),
    ("https://images.launchbox-app.com/2f83cfed-bede-47c0-ac59-242ebe86ffe1.png", "Clear Logo (World)"),
    ("https://images.launchbox-app.com/d67b9edd-d9a2-47b1-9289-6ff3f6061d24.jpg", "Screenshot - Gameplay"),
    ("https://images.launchbox-app.com/1f85d319-4765-4a38-9d83-d561703dd66e.jpg", "Fanart - Box - Front"),
    ("https://images.launchbox-app.com/3b48af0f-d574-4e52-8933-429cdabd184c.jpg", "Screenshot - Game Title"),
    ("https://images.launchbox-app.com/159fda35-062e-4693-afdd-ad89f3b836e7.png", "Clear Logo"),
    ("https://images.launchbox-app.com/9cde24eb-155a-47ff-b229-e96ecf5b6fad.jpg", "Fanart - Box - Front"),
])
register_game_gallery("th03", "Touhou 3: Phantasmagoria of Dim.Dream",
    "https://gamesdb.launchbox-app.com/games/images/75781-touhou-03-phantasmagoria-of-dimdream", [
    ("https://images.launchbox-app.com/r2_8471b6ea-d2f2-4600-88da-7482f0e83de1.png", "Box - Front (Japan)"),
    ("https://images.launchbox-app.com/9d54534e-995a-4e8b-a836-99e0b567b826.png", "Clear Logo"),
    ("https://images.launchbox-app.com/18d5e2df-758b-4d27-98c0-aab27fcd66e6.png", "Box - 3D"),
    ("https://images.launchbox-app.com/fa63b590-db7a-41a1-86e8-8626423f7389.jpg", "Fanart - Box - Front"),
    ("https://images.launchbox-app.com/b82e64ae-6f7d-48ac-9db5-f3b801fdc55c.png", "Clear Logo (World)"),
    ("https://images.launchbox-app.com/f00788d1-0691-434a-99a2-99d2f778bba6.jpg", "Fanart - Background"),
    ("https://images.launchbox-app.com/7af044e3-b58d-49b7-af24-3837153eb2e4.png", "Disc"),
    ("https://images.launchbox-app.com/5017632e-b98a-4e6a-8ef6-2f8c5983c73c.png", "Fanart - Box - Front"),
    ("https://images.launchbox-app.com/9d43dc89-7857-4f79-8bee-fe9567154c85.png", "Clear Logo (World)"),
    ("https://images.launchbox-app.com/f2681c2d-0a5f-4150-8d32-aed10d157547.png", "Screenshot - Gameplay (Japan)"),
    ("https://images.launchbox-app.com/9c0b2f68-279b-4741-8796-e5cf9638902d.png", "Screenshot - Game Title (Japan)"),
])
register_game_gallery("th04", "Touhou 4: Lotus Land Story",
    "https://gamesdb.launchbox-app.com/games/images/75782-touhou-04-lotus-land-story", [
    ("https://images.launchbox-app.com/r2_1c489ae8-691a-4f9e-b146-b22b43a9ff96.png", "Box - Front (Japan)"),
    ("https://images.launchbox-app.com/b93ce9fb-4f10-49dc-8d5b-907496c063f5.jpg", "Fanart - Background"),
    ("https://images.launchbox-app.com/73c2dce6-d6fc-414b-8c1b-dd51713059dd.png", "Disc"),
    ("https://images.launchbox-app.com/4da11e0d-c419-4df4-83bc-00fb8bf36b05.jpg", "Fanart - Box - Front"),
    ("https://images.launchbox-app.com/21cbb711-ee12-40de-b5d6-cb9f4590b426.png", "Clear Logo (Japan)"),
    ("https://images.launchbox-app.com/5ae92120-6b83-4b73-90b7-1d95df5aaa96.png", "Screenshot - Gameplay"),
    ("https://images.launchbox-app.com/1fc2640f-fcad-4b0b-9e78-e209001222e1.png", "Screenshot - Game Title"),
    ("https://images.launchbox-app.com/ccf1aa42-55ae-4e30-84a2-f4912208c591.png", "Clear Logo (Japan)"),
    ("https://images.launchbox-app.com/3ed38ed1-0565-4a37-87c7-edb8a268d5cb.png", "Box - 3D"),
    ("https://images.launchbox-app.com/60081925-92a7-4348-9816-cb5845d49abe.png", "Fanart - Box - Front"),
])
register_game_gallery("th05", "Touhou 5: Mystic Square",
    "https://gamesdb.launchbox-app.com/games/images/75783-touhou-05-mystic-square", [
    ("https://images.launchbox-app.com/r2_fc7d778b-d67a-4e1a-b42e-460ab98d411f.png", "Box - Front (Japan)"),
    ("https://images.launchbox-app.com/d7793dc7-8b6c-4947-8acd-40284dd9ab4a.png", "Fanart - Background"),
    ("https://images.launchbox-app.com/3a9bd4b9-c9e5-4ad2-9ba8-d475a4f8ecc3.png", "Disc"),
    ("https://images.launchbox-app.com/37615073-baec-4942-945e-52ffeb0091d2.png", "Fanart - Box - Front"),
    ("https://images.launchbox-app.com/d69abd07-c39f-40c7-b3c4-9ed46539b90c.png", "Clear Logo (World)"),
    ("https://images.launchbox-app.com/c983a6d2-4fb0-43c5-9844-475318d3cdbe.png", "Screenshot - Gameplay"),
    ("https://images.launchbox-app.com/6d2f391e-ca4a-4b67-b0ff-a29788a42a3e.png", "Screenshot - Game Select"),
    ("https://images.launchbox-app.com/16910fd9-e885-4e9a-be8c-8b8a375e2979.png", "Clear Logo"),
    ("https://images.launchbox-app.com/71d1c053-77c9-4b76-940c-4d2ce2fc2113.png", "Box - 3D"),
    ("https://images.launchbox-app.com/2d684c91-3a99-4b5c-bb90-819a2e58bae2.png", "Fanart - Box - Front"),
    ("https://images.launchbox-app.com/95a76c34-24eb-45f1-979c-9dd9ede6f2b1.jpg", "Screenshot - Game Title"),
])
register_game_gallery("th06", "Touhou 6: Embodiment of Scarlet Devil",
    EOSD_LB_PAGE, [
    (EOSD_COVER, "Box - Front (Japan)"),
    ("https://images.launchbox-app.com/f84901d7-9ba7-44fe-979f-1cd79ef1d941.png", "Clear Logo (World)"),
    (EOSD_GAMEPLAY, "Screenshot - Gameplay (Japan)"),
    (EOSD_GAMEPLAY_ALT, "Screenshot - Gameplay"),
    ("https://images.launchbox-app.com/1da13c92-9a5d-4bc7-8328-9432948f9e64.png", "Disc (World)"),
    (EOSD_GAMESELECT, "Clear Logo (Game Select Graphic)"),
    ("https://images.launchbox-app.com/6e456ffd-bf5b-4560-a5d2-8a6b425613d1.jpg", "Box - Spine (Japan)"),
    ("https://images.launchbox-app.com/306ef84c-41af-4e6f-8563-3438d807c890.jpg", "Box - Back (Japan)"),
    (EOSD_BG_1, "Fanart - Background (World)"),
    (EOSD_GAMEOVER, "Screenshot - Game Over (Japan)"),
    ("https://images.launchbox-app.com/5da9a32f-4df7-4261-ad4e-522a65ec6e7e.jpg", "Clear Logo (World)"),
    (EOSD_BG_2, "Fanart - Background (World)"),
    (EOSD_TITLE, "Screenshot - Game Title (Japan)"),
])
register_game_gallery("th07", "Touhou 7: Perfect Cherry Blossom",
    PCB_LB_PAGE, [
    (PCB_COVER, "Box - Front"),
    ("https://images.launchbox-app.com/8cd7c38e-6234-4329-8209-fedb53d5ccbc.png", "Clear Logo (World)"),
    (PCB_GAMEPLAY, "Screenshot - Gameplay"),
    ("https://images.launchbox-app.com/7fc1f60e-d20c-4439-be9e-06fe5f3e8230.jpg", "Box - Back (Japan)"),
    (PCB_BG, "Fanart - Background"),
    ("https://images.launchbox-app.com/179242cc-62a1-42f5-8ec4-e3200c65e048.jpg", "Disc (World)"),
    ("https://images.launchbox-app.com/3f5bd783-f3be-411b-9066-6e140f648a88.jpg", "Clear Logo (World)"),
    ("https://images.launchbox-app.com/393f9894-3bfb-4c5d-8230-a15a889ae137.png", "Fanart - Background"),
    ("https://images.launchbox-app.com/3b126a2b-6153-4a66-b615-e58eeb3dab46.png", "Box - Spine (Japan)"),
])
register_game_gallery("th08", "Touhou 8: Imperishable Night",
    IN_LB_PAGE, [
    (IN_COVER, "Box - Front"),
    ("https://images.launchbox-app.com/c445d03d-da65-44d7-94bc-331efe527ce6.png", "Clear Logo (World)"),
    (IN_GAMEPLAY, "Screenshot - Gameplay"),
    ("https://images.launchbox-app.com/r2_def09171-30ce-48b0-9ea5-cfcaf4c3b3d2.jpg", "Box - Spine (Japan)"),
    ("https://images.launchbox-app.com/r2_a535007e-225b-4ca8-a181-0a13864b346e.jpg", "Box - Back (Japan)"),
    (IN_BG, "Fanart - Background"),
    ("https://images.launchbox-app.com/bc84f681-3ee3-476d-9a4e-86688f1689ba.jpg", "Clear Logo (World)"),
    ("https://images.launchbox-app.com/cc985d03-e1ed-4b2a-862f-2d3df105bcc8.png", "Disc (World)"),
])
register_game_gallery("th09", "Touhou 9: Phantasmagoria of Flower View",
    "https://gamesdb.launchbox-app.com/games/images/7352-touhou-09-phantasmagoria-of-flower-view", [
    ("https://images.launchbox-app.com/f13f52a0-b6cb-46fa-8328-1f7298062df6.png", "Box - Front (World)"),
    ("https://images.launchbox-app.com/eb6edcbf-e335-45f1-8488-beb60b0d84e4.png", "Clear Logo (World)"),
    ("https://images.launchbox-app.com/b113889b-6fb0-48fd-9b94-8f927dfab69f.jpg", "Screenshot - Gameplay"),
    ("https://images.launchbox-app.com/e4473ad7-980a-49cf-b4f4-6d1a82fe2494.jpg", "Box - Back (Japan)"),
    ("https://images.launchbox-app.com/r2_2c20686d-11eb-4054-9004-d45322edd20f.jpg", "Fanart - Background (World)"),
    ("https://images.launchbox-app.com/ef6e9850-463f-499d-9800-cdea07c511e6.png", "Disc (Japan)"),
    ("https://images.launchbox-app.com/50a19648-6d61-4abc-bc3c-6cca5aea9f4c.jpg", "Clear Logo (World)"),
    ("https://images.launchbox-app.com/852e2a6d-9080-4e42-bd75-f23744f9ff4c.png", "Fanart - Background"),
    ("https://images.launchbox-app.com/f61073df-7220-404e-919a-2f2033235dd2.png", "Box - Spine (Japan)"),
])
register_game_gallery("th10", "Touhou 10: Mountain of Faith",
    MOF_LB_PAGE, [
    (MOF_LB_COVER, "Box - Front (Japan)"),
    ("https://images.launchbox-app.com/1b4e1ae8-3e05-4c96-aad5-ec08502d14dd.png", "Clear Logo (World)"),
    (MOF_LB_GAMEPLAY, "Screenshot - Gameplay"),
    ("https://images.launchbox-app.com/72bfd9ca-a729-40ef-b94a-cc2f2becbd16.png", "Disc (Japan)"),
    ("https://images.launchbox-app.com/r2_7bb06148-68f2-48d0-ba90-d7c64c28d457.jpg", "Box - Back (Japan)"),
    (MOF_LB_BG, "Fanart - Background"),
    ("https://images.launchbox-app.com/5ed6c12b-5d00-4b7e-840d-5b5c0681f190.jpg", "Box - Spine (Japan)"),
    ("https://images.launchbox-app.com/r2_85219efc-1854-4105-bac7-cca14ba5021c.jpg", "Clear Logo (World)"),
    ("https://images.launchbox-app.com/9629bfc6-e2a9-41db-8a1e-068f817ed586.png", "Screenshot - Gameplay"),
])
register_game_gallery("th11", "Touhou 11: Subterranean Animism",
    "https://gamesdb.launchbox-app.com/games/images/7365-touhou-11-subterranean-animism", [
    ("https://images.launchbox-app.com/2a7d7a65-4b98-4771-a18b-29ef85d24dc4.jpg", "Box - Front (Japan)"),
    ("https://images.launchbox-app.com/ed51dbbd-a68b-4818-ad34-fb74e851345d.png", "Clear Logo (Japan)"),
    ("https://images.launchbox-app.com/192c70c9-039f-4f39-acf3-7ff621646183.jpg", "Screenshot - Gameplay"),
    ("https://images.launchbox-app.com/r2_8973029a-691b-4592-95c7-51cc9d763066.png", "Disc (Japan)"),
    ("https://images.launchbox-app.com/r2_6152dd91-4a6f-40f2-b32f-d84f22ed0ff2.jpg", "Box - Back (Japan)"),
    ("https://images.launchbox-app.com/31d1e925-0304-4260-8cbd-706f37235df3.jpg", "Fanart - Background"),
    ("https://images.launchbox-app.com/a32a22a5-5b9f-4c96-b7d2-3ebc12b08005.jpg", "Box - Spine (Japan)"),
    ("https://images.launchbox-app.com/r2_8e1c0e54-41b1-4a3a-9f20-dc765603b576.jpg", "Clear Logo (Japan)"),
])
register_game_gallery("th12", "Touhou 12: Undefined Fantastic Object",
    "https://gamesdb.launchbox-app.com/games/images/7366-touhou-12-undefined-fantastic-object", [
    ("https://images.launchbox-app.com/a40d949e-136e-4ac5-98f1-38b94f58fe56.jpg", "Box - Front (World)"),
    ("https://images.launchbox-app.com/a5add165-84af-49e5-bd6d-100606f81c3e.png", "Clear Logo"),
    ("https://images.launchbox-app.com/e6df00a4-a4f4-484e-b134-e7b840430290.jpg", "Screenshot - Gameplay"),
    ("https://images.launchbox-app.com/6eacf4ac-e6af-48f1-aea6-06ac70054ad3.jpg", "Screenshot - Gameplay"),
    ("https://images.launchbox-app.com/r2_5e9ba65a-ccac-494d-bb9d-0ef7ae20840a.png", "Box - Back (Japan)"),
    ("https://images.launchbox-app.com/dba94e49-f464-46f8-adbb-ba7bcd6a1ccc.jpg", "Fanart - Background"),
    ("https://images.launchbox-app.com/c0ee32fa-d5fb-4955-8ae8-21739389ab23.jpg", "Disc (Japan)"),
    ("https://images.launchbox-app.com/r2_005c9e9a-8a5d-4dcd-af17-c8bb598da2cf.png", "Clear Logo (World)"),
])
register_game_gallery("th13", "Touhou 13: Ten Desires",
    "https://gamesdb.launchbox-app.com/games/images/7371-touhou-13-ten-desires", [
    ("https://images.launchbox-app.com/df5259c7-2df7-4d64-9f23-7db53e44df3a.jpg", "Box - Front"),
    ("https://images.launchbox-app.com/66ff1f67-265d-4fc1-8c08-7c4398c68724.jpg", "Fanart - Background"),
    ("https://images.launchbox-app.com/ce5b770d-67e7-4cf3-9a4f-6357ad99c920.jpg", "Screenshot - Gameplay"),
    ("https://images.launchbox-app.com/4a20b9b9-c2ee-419a-8a13-f98599f0674d.png", "Clear Logo (World)"),
    ("https://images.launchbox-app.com/d0ceab18-5ab6-4033-9f9c-7b6214db9e7c.jpg", "Fanart - Background"),
    ("https://images.launchbox-app.com/15830020-346f-4129-85f8-bbe210aa1e73.jpg", "Screenshot - Gameplay"),
    ("https://images.launchbox-app.com/a95f5a80-ae22-4bec-995f-9e2e0cadfb75.jpg", "Screenshot - Gameplay"),
])
register_game_gallery("th14", "Touhou 14: Double Dealing Character",
    "https://gamesdb.launchbox-app.com/games/images/24476-touhou-14-double-dealing-character", [
    ("https://images.launchbox-app.com/2f967582-78ee-4b06-8943-080d0f1555d9.jpg", "Box - Front"),
    ("https://images.launchbox-app.com/54bcaa61-f7a3-4de9-aabd-bdf7d194d9cb.jpg", "Fanart - Background"),
    ("https://images.launchbox-app.com/ab2ac598-9b96-4602-9028-7283d658a623.png", "Clear Logo"),
    ("https://images.launchbox-app.com/0fafc98f-1465-411b-933b-156813130076.jpg", "Screenshot - Gameplay"),
    ("https://images.launchbox-app.com/c93fb1c1-4876-4c82-9da9-eeba294cfb5a.jpg", "Fanart - Background (World)"),
])
register_game_gallery("th15", "Touhou 15: Legacy of Lunatic Kingdom",
    "https://gamesdb.launchbox-app.com/games/images/31253-touhou-15-legacy-of-lunatic-kingdom", [
    ("https://images.launchbox-app.com/abddfd82-544e-4e86-9f0a-48965b434752.jpg", "Box - Front"),
    ("https://images.launchbox-app.com/d9012ecb-60ae-4e71-81eb-5dcfa062ecd8.jpg", "Screenshot - Gameplay"),
    ("https://images.launchbox-app.com/a6c44234-bd64-4802-b16a-937db32f1366.png", "Clear Logo"),
    ("https://images.launchbox-app.com/3316e14c-33b3-4763-a5a6-89963f209d5f.jpg", "Fanart - Background (World)"),
])
register_game_gallery("th16", "Touhou 16: Hidden Star in Four Seasons",
    "https://gamesdb.launchbox-app.com/games/images/84947-touhou-16-hidden-star-in-four-seasons", [
    ("https://images.launchbox-app.com/74dcb163-38f2-4542-9964-6f1a45b43408.jpg", "Box - Front (Japan)"),
    ("https://images.launchbox-app.com/463ae839-4393-4719-965f-c819b74193eb.jpg", "Fanart - Background"),
    ("https://images.launchbox-app.com/37d97647-6e12-4f5a-a7da-1278ac18cc63.png", "Clear Logo"),
    ("https://images.launchbox-app.com/8f49ffa7-a471-4350-b9bf-2558b152128d.jpg", "Screenshot - Game Title"),
    ("https://images.launchbox-app.com/ae222db7-b2ce-46cc-a0ac-c1f271253974.png", "Fanart - Background"),
])
register_game_gallery("th17", "Touhou 17: Wily Beast and Weakest Creature",
    "https://gamesdb.launchbox-app.com/games/images/117033-touhou-17-wily-beast-and-weakest-creature", [
    ("https://images.launchbox-app.com/c2d7a263-2410-4ce1-b04e-bb04bf696747.jpg", "Box - Front (Japan)"),
    ("https://images.launchbox-app.com/59ae4d43-a763-4700-833f-e60c510cc2c1.png", "Screenshot - Gameplay"),
    ("https://images.launchbox-app.com/97c97026-c082-44db-affa-d30c523eabfa.jpg", "Banner"),
    ("https://images.launchbox-app.com/62b21a6c-2ef1-4f4f-89e6-470771a835d8.png", "Clear Logo (Japan)"),
    ("https://images.launchbox-app.com/6c0c264a-3b9b-4451-b154-68c3ed310792.png", "Screenshot - Game Title"),
    ("https://images.launchbox-app.com/0103ec1b-5507-4c83-b9dc-cb2f3e85a848.png", "Fanart - Background"),
    ("https://images.launchbox-app.com/3ffc2b49-0a69-4d12-abf6-2010fc5eb9ed.jpg", "Screenshot - Gameplay"),
])
register_game_gallery("th18", "Touhou 18: Unconnected Marketeers",
    "https://gamesdb.launchbox-app.com/games/images/151407-touhou-18-unconnected-marketeers", [
    ("https://images.launchbox-app.com/e48b6f94-e3bb-4ebf-b4ac-e40710cad170.jpg", "Box - Front (Japan)"),
    ("https://images.launchbox-app.com/d661f383-4f38-4034-8a27-fd558e3dc7fe.jpg", "Screenshot - Gameplay (Japan)"),
    ("https://images.launchbox-app.com/86da4998-b0c8-4b0f-95dd-40abdcc728f5.jpg", "Clear Logo (Japan)"),
    ("https://images.launchbox-app.com/60139dc0-3d20-405d-9552-8fac41760544.png", "Screenshot - Game Title (Japan)"),
    ("https://images.launchbox-app.com/3de03654-a136-4da2-9667-772af39eddf1.jpg", "Screenshot - Gameplay (Japan)"),
    ("https://images.launchbox-app.com/beedb004-2a65-460a-97b1-bf6e1b2bbed4.png", "Screenshot - Gameplay (Japan)"),
    ("https://images.launchbox-app.com/5ec4fd11-26e4-49da-84e5-ce35a2460c36.jpg", "Screenshot - Gameplay (Japan)"),
])

# Individual print-work covers from their publisher/retailer pages keep bibliography
# cards distinct as well as being a better fit than reusing game art.
register_custom_image(PMISS_COVER, "https://www.neowing.co.jp/product/NEOBK-395940",
    "Neowing — Perfect Memento in Strict Sense", "print", "cover",
    "Cover of Perfect Memento in Strict Sense, an official Touhou reference book.")
register_custom_image(FORBIDDEN_SCROLLERY, "https://yenpress.com/titles/9780316511971-forbidden-scrollery-vol-1",
    "Yen Press — Forbidden Scrollery, Vol. 1", "print", "cover",
    "Publisher cover for Forbidden Scrollery, volume 1.")
register_custom_image("https://images.yenpress.com/imgs/9780316512008.jpg?w=408&h=612&type=books&s=876b2917f3191483c6d19bba743f8452",
    "https://yenpress.com/titles/9780316512008-forbidden-scrollery-vol-2",
    "Yen Press — Forbidden Scrollery, Vol. 2", "print", "cover",
    "Publisher cover for Forbidden Scrollery, volume 2.")
register_custom_image("https://images.yenpress.com/imgs/9780316512015.jpg?w=285&h=422&type=books&s=701d506b9563326056ce3133a8252411",
    "https://yenpress.com/series/forbidden-scrollery", "Yen Press — Forbidden Scrollery, Vol. 3",
    "print", "cover", "Publisher cover for Forbidden Scrollery, volume 3.")
register_custom_image("https://images.yenpress.com/imgs/9780316512039.jpg?w=285&h=422&type=books&s=8d2060290f2b4eb5e1df7d79d2f70c1c",
    "https://yenpress.com/series/forbidden-scrollery", "Yen Press — Forbidden Scrollery, Vol. 4",
    "print", "cover", "Publisher cover for Forbidden Scrollery, volume 4.")
register_custom_image("https://images.yenpress.com/imgs/9780316512084.jpg?w=285&h=422&type=books&s=905b389fd900e24bd0eb3f884c734bee",
    "https://yenpress.com/series/forbidden-scrollery", "Yen Press — Forbidden Scrollery, Vol. 5",
    "print", "cover", "Publisher cover for Forbidden Scrollery, volume 5.")
register_custom_image("https://images.yenpress.com/imgs/9780316512091.jpg?w=285&h=422&type=books&s=0c564290b8756033095b51c7a17c746d",
    "https://yenpress.com/series/forbidden-scrollery", "Yen Press — Forbidden Scrollery, Vol. 6",
    "print", "cover", "Publisher cover for Forbidden Scrollery, volume 6.")
register_custom_image("https://shop.akbh.jp/cdn/shop/products/9784758012317.jpg?v=1722506606&width=800",
    "https://shop.akbh.jp/en/products/9784758012317",
    "AKIBA-HOBBY — Symposium of Post-mysticism", "print", "cover",
    "Retail cover for Symposium of Post-mysticism, an official Touhou reference book.")
register_custom_image(SILENT_SINNER, "https://shop.akbh.jp/en/products/9784758060899",
    "AKIBA-HOBBY — Silent Sinner in Blue, Vol. 1", "print", "cover",
    "Retail cover for Silent Sinner in Blue, volume 1.")

# Official visuals remain in the source pool, but each one is assigned to at most
# one non-character image slot.
for _url, _label, _kind, _alt in [
    (COVER, "Touhou New Classic — official cover", "cover", "Official Touhou Koumakyou: New Classic cover artwork."),
    (SHOT_NEW, "Touhou New Classic — gameplay screenshot", "screenshot", "Official Touhou New Classic gameplay screenshot."),
    (SHOT_SYSTEM, "Touhou New Classic — system screenshot", "screenshot", "Official Touhou New Classic gameplay/system screenshot."),
    (SHOT_CLASSIC, "Touhou New Classic — classic screenshot", "screenshot", "Official Touhou New Classic classic-mode screenshot."),
    (TITLE_LOGO, "Touhou New Classic — title logo", "logo", "Official Touhou New Classic title artwork."),
    (MOON_BG, "Touhou New Classic — moon background", "background", "Moonlit atmospheric artwork from the official Touhou New Classic site."),
    (FOG_1, "Touhou New Classic — mist background", "background", "Atmospheric background artwork from the official Touhou New Classic site."),
    (FOG_3, "Touhou New Classic — mist background", "background", "Atmospheric background artwork from the official Touhou New Classic site."),
    (FOG_4, "Touhou New Classic — mist background", "background", "Atmospheric background artwork from the official Touhou New Classic site."),
    (MOF_BG, "Steam — Mountain of Faith", "background", "Official Mountain of Faith store background artwork."),
    (MOF_HEADER, "Steam — Mountain of Faith", "cover", "Official Mountain of Faith header artwork."),
    (MOF_COMMUNITY, "Steam — Mountain of Faith", "artwork", "Mountain of Faith community artwork hosted on Steam."),
]:
    register_custom_image(_url, OFFICIAL_PAGE if _url in [COVER, SHOT_NEW, SHOT_SYSTEM, SHOT_CLASSIC, TITLE_LOGO, MOON_BG, FOG_1, FOG_3, FOG_4] else MOF_PAGE,
        _label, "th06" if _url in [COVER, SHOT_NEW, SHOT_SYSTEM, SHOT_CLASSIC, TITLE_LOGO, MOON_BG, FOG_1, FOG_3, FOG_4] else "th10",
        _kind, _alt)


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
    # Contextual source overrides (for a single page/card) are pre-registered here.
    if url in URL_CREDIT:
        metadata = dict(URL_CREDIT[url])
        metadata.update({
            "url": url,
            "source_page": str(metadata["source_page"]),
            "reference_url": url,
            "original_name": unquote(urlsplit(url).path).rstrip("/").rsplit("/", 1)[-1],
            "fallback_urls": list(FALLBACKS.get(str(metadata["source_page"]), [])),
        })
        return metadata
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
        "Touhou Wiki's file pages identify the source and any licensing information provided for each image. Image rights can differ by file, and many assets depict copyrighted Touhou characters or game art. Check the individual file page and applicable rights before reusing an image elsewhere. One book cover on the print-works page remains linked to its retailer listing for accurate bibliographic identification.",
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



PAGE_CONTEXT_OVERRIDES = {
    "pages/locations.html": [
        {
            "heading": "Outside World & the Barrier",
            "old_filename": "Th105BambooForest.jpg",
            "new_url": IN_BG,
            "source_page": IN_LB_PAGE,
            "credit": "LaunchBox Games Database — Touhou 8: Imperishable Night",
            "alt": "Night-sky background artwork associated with Touhou 8: Imperishable Night, used as an atmospheric illustration for the boundary between Gensokyo and the Outside World.",
        }
    ],
    "pages/chronology.html": [
        {
            "heading": "",
            "container": "figure",
            "old_filename": "Th06screenLayout.jpg",
            "new_url": PC98_GAMEPLAY,
            "source_page": PC98_LB_PAGE,
            "credit": "LaunchBox Games Database — Touhou 1: Highly Responsive to Prayers",
            "alt": "PC-98-era gameplay screenshot from Touhou 1: Highly Responsive to Prayers, used to introduce release history.",
        }
    ],
    "pages/music.html": [
        {
            "heading": "Shanghai Teahouse ~ Chinese Tea",
            "old_filename": "Th06stage3title.jpg",
            "new_url": MEILING,
            "source_page": OFFICIAL_PAGE,
            "credit": "Official Touhou New Classic site",
            "alt": "Hong Meiling character portrait from the official Touhou Koumakyou: New Classic website, matching the Shanghai Teahouse theme card.",
        }
    ],
}


def apply_context_overrides(relative_path: str, content: str) -> str:
    for override in PAGE_CONTEXT_OVERRIDES.get(relative_path, []):
        old_url = "https://en.touhouwiki.net/wiki/Special:FilePath/" + quote(
            override["old_filename"], safe="()'!._-"
        )
        new_url = str(override["new_url"])
        source_page = str(override["source_page"])
        credit = str(override["credit"])
        alt = str(override["alt"])
        # Ensure direct-URL references inherit exact source metadata when localized.
        URL_CREDIT[new_url] = {
            "source_page": source_page,
            "credit": credit,
            "alt": alt,
        }
        def replace_container(match: re.Match[str]) -> str:
            container = match.group(0)
            heading = str(override.get("heading", ""))
            if heading and heading not in html.unescape(container):
                return container
            if old_url not in container:
                return container
            container = container.replace(old_url, new_url)
            container = re.sub(
                r'\balt\s*=\s*(["\']).*?\1',
                lambda m: 'alt="' + alt.replace("&", "&amp;").replace('"', "&quot;") + '"',
                container,
                count=1,
                flags=re.IGNORECASE | re.DOTALL,
            )
            # Keep the source link aligned with the image actually displayed.
            image_source_link = re.compile(
                r'<a\s+href="https://en\.touhouwiki\.net/wiki/File:[^"]+"[^>]*>Touhou Wiki file ↗</a>',
                re.IGNORECASE,
            )
            container = image_source_link.sub(
                '<a href="' + source_page + '" target="_blank" rel="noopener">' + credit + ' ↗</a>',
                container,
                count=1,
            )
            return container
        if override.get("container") == "figure":
            content = re.sub(r'<figure\b[\s\S]*?</figure>', replace_container, content, count=1, flags=re.IGNORECASE)
        else:
            content = re.sub(
                r'<article\b[^>]*class="[^"]*archive-card[^"]*"[^>]*>[\s\S]*?</article>',
                replace_container,
                content,
                flags=re.IGNORECASE,
            )
    return content



CHARACTER_FILES = {
    "Th06Reimu.png", "Th105Reimu.png", "Th06Marisa.png",
    "Th06Cirno.png", "Th06Meiling.png", "Th06Flandre.png",
    "Th06Remilia.png", "Th105Aya.png", "Th10KanakoYasaka.png",
}
CARD_OR_FIGURE_RE = re.compile(
    r'<article\b[^>]*class=["\'][^"\']*\barchive-card\b[^"\']*["\'][^>]*>[\s\S]*?</article>|<a\b[^>]*class=["\'][^"\']*\barchive-card\b[^"\']*["\'][^>]*>[\s\S]*?</a>|<figure\b[\s\S]*?</figure>',
    re.IGNORECASE,
)
SOURCE_ANCHOR_RE = re.compile(
    r'<a\s+href="https://en\.touhouwiki\.net/wiki/File:[^"]+"[^>]*>[\s\S]*?</a>',
    re.IGNORECASE,
)
GAME_CONTEXT_RULES = [
    (("highly responsive to prayers", "pc-98", "pc98 era"), ("th01", "th02", "th03", "th04", "th05")),
    (("story of eastern wonderland", "eastern wonderland"), ("th02",)),
    (("phantasmagoria of dim", "dim.dream"), ("th03",)),
    (("lotus land story",), ("th04",)),
    (("mystic square",), ("th05",)),
    (("embodiment of scarlet devil", "scarlet devil mansion", "scarlet mist", "misty lake", "eosd"), ("th06",)),
    (("perfect cherry blossom", "hakugyokurou", "netherworld", "missing spring"), ("th07",)),
    (("imperishable night", "bamboo forest", "eientei"), ("th08",)),
    (("phantasmagoria of flower view", "flower view"), ("th09",)),
    (("mountain of faith", "moriya shrine", "youkai mountain"), ("th10",)),
    (("subterranean animism", "hell", "underground", "geyser"), ("th11",)),
    (("undefined fantastic object", "treasure ship", "ufo"), ("th12",)),
    (("ten desires", "divine spirit"), ("th13",)),
    (("double dealing character", "miracle mallet", "tsukumogami"), ("th14",)),
    (("legacy of lunatic kingdom", "lunarian", "lunatic kingdom"), ("th15",)),
    (("hidden star in four seasons", "four seasons", "seasonal"), ("th16",)),
    (("wily beast", "beast spirits", "animal spirits"), ("th17",)),
    (("unconnected marketeers", "ability cards", "mysterious cards"), ("th18",)),
    (("perfect memento", "forbidden scrollery", "print works", "bohemian archive", "symposium of post-mysticism", "silent sinner"), ("print",)),
]


def is_character_reference(url: str) -> bool:
    name = wiki_filename(url)
    return bool(name and name in CHARACTER_FILES)


def _context_game(context: str, relative_path: str) -> tuple[str, ...]:
    lower = html.unescape(re.sub(r"<[^>]+>", " ", context)).lower()
    for phrases, games in GAME_CONTEXT_RULES:
        if any(phrase in lower for phrase in phrases):
            return games
    basename = Path(relative_path).name.lower()
    if "chronology" in basename:
        return ("th01", "th02", "th03", "th04", "th05", "th06", "th07", "th08", "th10", "th15", "th16", "th18")
    if "print-works" in basename or "sources" in basename:
        return ("print", "th10", "th13", "th06")
    if "locations" in basename:
        return ("th10", "th06", "th07", "th08", "th16", "th09")
    if "spell-cards" in basename or "music" in basename:
        return ("th06", "th09", "th10", "th12", "th18")
    if "games" in basename:
        return ("th06", "th07", "th08", "th10", "th12", "th15", "th16", "th18")
    return ("th06", "th10", "th07", "th08", "th12", "th13", "th16", "th18", "th01", "th04", "th09")


def _context_kind(context: str, is_css_background: bool = False) -> tuple[str, ...]:
    lower = html.unescape(re.sub(r"<[^>]+>", " ", context)).lower()

    # A CSS background should look like scenery, not a disc, logo, or book jacket.
    if is_css_background:
        return ("background", "artwork", "screenshot")

    # Match section meaning before broad words such as "stage" or "cover".
    if any(k in lower for k in (
        "print works", "book cover", "manga", "official book", "reference book",
        "perfect memento", "forbidden scrollery", "silent sinner",
        "bohemian archive", "symposium of post-mysticism", "wild and horned hermit",
        "lotus eater",
    )):
        return ("cover",)

    if any(k in lower for k in (
        "music & themes", "music and themes", "soundtrack", "original tracks",
        "listening notes", "character theme", "stage theme", "track title",
    )):
        # Disc art belongs here if available; gameplay/scenery is a safe fallback.
        return ("disc", "screenshot", "background", "artwork")

    if any(k in lower for k in (
        "spell cards", "spell-card", "spell card", "danmaku", "boss pattern",
        "projectile", "bullet pattern", "game interface", "attack pattern",
    )):
        return ("screenshot", "background", "artwork")

    if any(k in lower for k in (
        "places of gensokyo", "location", "shrine", "forest", "lake", "mansion",
        "barrier", "gensokyo", "moon", "mountain", "setting", "village",
    )):
        return ("background", "artwork", "screenshot")

    if any(k in lower for k in (
        "games & incidents", "game release", "release history", "title screen",
        "first touhou game", "cover artwork", "game packaging",
    )):
        return ("cover", "screenshot", "background", "artwork")

    # Never silently substitute a game logo or an unrelated physical disc.
    return ("background", "screenshot", "cover", "artwork")

def choose_distinct_image(context: str, relative_path: str, used_assets: set[str], background: bool = False) -> dict[str, str]:
    if not DIVERSE_IMAGE_CATALOG:
        raise RuntimeError("The diverse image catalogue is empty.")

    clean_context = html.unescape(re.sub(r"<[^>]+>", " ", context)).lower()
    desired_games = _context_game(context, relative_path)
    desired_kinds = _context_kind(context, background)
    basename = Path(relative_path).name.lower()

    # Page routes are a second guard in case a card description is too short.
    if "print-works" in basename:
        desired_kinds = ("cover",)
    elif "spell-cards" in basename:
        desired_kinds = ("screenshot", "background", "artwork")
    elif "locations" in basename:
        desired_kinds = ("background", "artwork", "screenshot")
    elif "music" in basename:
        desired_kinds = ("disc", "screenshot", "background", "artwork")
    elif "games" in basename:
        desired_kinds = ("cover", "screenshot", "background", "artwork")

    preferred_headings = re.findall(r"<h[1-4][^>]*>(.*?)</h[1-4]>", context, flags=re.IGNORECASE | re.DOTALL)
    display_context = " — ".join(re.sub(r"<[^>]+>", "", html.unescape(x)).strip() for x in preferred_headings[:2])
    if not display_context:
        display_context = Path(relative_path).stem.replace("-", " ").title()

    used_print_section = (
        "print-works" in basename
        or any(term in clean_context for term in (
            "print works", "perfect memento", "forbidden scrollery", "silent sinner in blue",
            "bohemian archive", "symposium of post-mysticism", "wild and horned hermit",
            "lotus eater",
        ))
    )

    available = [
        candidate for candidate in DIVERSE_IMAGE_CATALOG
        if _image_identity(candidate["url"]) not in used_assets
    ]

    # No game cover, logo, or disc is allowed to leak into a location/spell-card
    # slot merely because the better matching pictures have already been used.
    eligible = [candidate for candidate in available if candidate["kind"] in desired_kinds]
    spell_context = (
        "spell-cards" in basename
        or any(term in clean_context for term in (
            "spell cards", "spell-card", "spell card", "danmaku", "boss pattern",
            "projectile", "bullet pattern", "attack pattern",
        ))
    )
    if spell_context:
        # Menus, game-over panels and title screens are not spell-card visuals.
        eligible = [
            candidate for candidate in eligible
            if not (
                candidate["kind"] == "screenshot"
                and any(term in str(candidate.get("label", "")).lower()
                        for term in ("game select", "game title", "game over", "title screen"))
            )
        ]
    if used_print_section:
        eligible = [
            candidate for candidate in eligible
            if candidate["game"] == "print" and candidate["kind"] == "cover"
        ]

    if not eligible:
        section = "print-work covers" if used_print_section else ", ".join(desired_kinds)
        raise RuntimeError(
            f"No unused, section-appropriate image remains for {relative_path} ({display_context}); "
            f"required media type: {section}. Add more researched matching assets instead of using an unrelated image."
        )

    topic_phrases = (
        "perfect memento in strict sense", "perfect memento", "forbidden scrollery",
        "silent sinner in blue", "symposium of post-mysticism", "bohemian archive in japanese red",
        "bohemian archive", "wild and horned hermit", "lotus eater",
        "highly responsive to prayers", "story of eastern wonderland",
        "phantasmagoria of dim.dream", "lotus land story", "mystic square",
        "embodiment of scarlet devil", "perfect cherry blossom", "imperishable night",
        "phantasmagoria of flower view", "mountain of faith", "subterranean animism",
        "undefined fantastic object", "ten desires", "double dealing character",
        "legacy of lunatic kingdom", "hidden star in four seasons",
        "wily beast and weakest creature", "unconnected marketeers",
    )

    def score(candidate: dict[str, str]) -> tuple[int, int, int]:
        game_score = (
            (len(desired_games) - desired_games.index(candidate["game"])) * 100
            if candidate["game"] in desired_games else 0
        )
        kind_score = (
            (len(desired_kinds) - desired_kinds.index(candidate["kind"])) * 12
            if candidate["kind"] in desired_kinds else 0
        )
        candidate_text = " ".join(
            str(candidate.get(key, "")) for key in ("title", "label", "credit", "alt", "game")
        ).lower()
        topic_score = max(
            (1200 for phrase in topic_phrases
             if phrase in clean_context and phrase in candidate_text),
            default=0,
        )
        quality_score = 3 if candidate["kind"] in ("cover", "screenshot", "background", "artwork") else 0
        return (topic_score + game_score, kind_score, quality_score)

    chosen = max(eligible, key=score)
    used_assets.add(_image_identity(chosen["url"]))
    source_page = chosen["source_page"]
    context_alt = chosen["alt"]
    credit = chosen["credit"]
    URL_CREDIT[chosen["url"]] = {
        "source_page": source_page, "credit": credit, "alt": context_alt
    }
    return {
        **chosen,
        "context": display_context,
        "context_alt": context_alt,
    }

def attribute_image_container(
    container: str,
    source_page: str,
    credit: str,
    alt_text: str,
    replacement_url: str | None = None,
) -> str:
    match = IMG_TAG_RE.search(container)
    if not match:
        return container
    tag = match.group(0)
    src_match = IMG_SRC_RE.search(tag)
    if not src_match:
        return container

    if replacement_url:
        tag = tag[:src_match.start(2)] + replacement_url + tag[src_match.end(2):]
    alt = alt_text.replace("&", "&amp;").replace('"', "&quot;")
    safe_credit = credit.replace("&", "&amp;").replace('"', "&quot;")
    safe_source = source_page.replace("&", "&amp;").replace('"', "&quot;")
    tag = re.sub(r'\balt\s*=\s*(["\']).*?\1', f'alt="{alt}"', tag, count=1, flags=re.IGNORECASE | re.DOTALL)
    tag = re.sub(r'\btitle\s*=\s*(["\']).*?\1', f'title="Image source: {safe_credit}"', tag, count=1, flags=re.IGNORECASE | re.DOTALL)
    if not re.search(r'\btitle\s*=', tag, flags=re.IGNORECASE):
        tag = tag[:-1] + f' title="Image source: {safe_credit}">'
    # Delete old Wiki-specific metadata and responsive source links so no stale
    # attribution or blocked image variant can override the actual displayed asset.
    tag = re.sub(r'\sdata-wiki-file=(["\']).*?\1', "", tag, flags=re.IGNORECASE | re.DOTALL)
    tag = re.sub(r'\s+srcset=(["\']).*?\1', "", tag, flags=re.IGNORECASE | re.DOTALL)
    container = container[:match.start()] + tag + container[match.end():]

    source_link = f'<a href="{safe_source}" target="_blank" rel="noopener">{safe_credit} ↗</a>'
    if re.search(r'<figcaption\b', container, flags=re.IGNORECASE):
        container = re.sub(
            r'<figcaption\b[^>]*>[\s\S]*?</figcaption>',
            '<figcaption class="caption">Image source · ' + source_link + '</figcaption>',
            container,
            count=1,
            flags=re.IGNORECASE,
        )
    else:
        def replace_source_anchor(_match: re.Match[str]) -> str:
            return source_link
        container = SOURCE_ANCHOR_RE.sub(replace_source_anchor, container, count=1)

    if re.search(r'<span\b[^>]*class=["\'][^"\']*\bsmall-source\b[^"\']*["\'][^>]*>', container, flags=re.IGNORECASE):
        container = re.sub(
            r'<span\b[^>]*class=["\'][^"\']*\bsmall-source\b[^"\']*["\'][^>]*>[\s\S]*?</span>',
            '<span class="small-source">Image source: ' + source_link + '</span>',
            container,
            count=1,
            flags=re.IGNORECASE,
        )
    return container


def diversify_image_container(container: str, relative_path: str, used_assets: set[str]) -> str:
    match = IMG_TAG_RE.search(container)
    if not match:
        return container
    tag = match.group(0)
    src_match = IMG_SRC_RE.search(tag)
    if not src_match:
        return container
    original_url = src_match.group(2)
    if not is_external_image(original_url):
        return container

    # Character portraits may repeat by request and keep their character-specific source.
    if is_character_reference(original_url):
        name = wiki_filename(original_url)
        metadata = IMAGE_ALIASES.get(name or "")
        if metadata:
            return attribute_image_container(
                container,
                str(metadata["source_page"]),
                str(metadata["credit"]),
                str(metadata["alt"]),
            )
        return container

    clean_context = html.unescape(re.sub(r"<[^>]+>", " ", container)).lower()
    is_print_context = (
        "print-works" in Path(relative_path).name.lower()
        or any(term in clean_context for term in (
            "print works", "perfect memento", "forbidden scrollery", "silent sinner in blue",
            "bohemian archive", "symposium of post-mysticism", "wild and horned hermit", "lotus eater",
        ))
    )
    allowed_kinds = _context_kind(container)
    if "print-works" in Path(relative_path).name.lower():
        allowed_kinds = ("cover",)

    catalog_by_identity = {_image_identity(item["url"]): item for item in DIVERSE_IMAGE_CATALOG}

    def can_keep(candidate: dict[str, str] | None) -> bool:
        if not candidate:
            return False
        if _image_identity(candidate["url"]) in used_assets:
            return False
        if candidate["kind"] not in allowed_kinds:
            return False
        if is_print_context and not (candidate["game"] == "print" and candidate["kind"] == "cover"):
            return False
        spell_context = (
            "spell-cards" in Path(relative_path).name.lower()
            or any(term in clean_context for term in (
                "spell cards", "spell-card", "spell card", "danmaku", "boss pattern",
                "projectile", "bullet pattern", "attack pattern",
            ))
        )
        if spell_context and candidate["kind"] == "screenshot":
            label = str(candidate.get("label", "")).lower()
            if any(term in label for term in ("game select", "game title", "game over", "title screen")):
                return False
        return True

    # First honour a known Touhou Wiki filename's carefully reviewed replacement.
    # The image is reserved globally, so the same non-character image cannot appear twice.
    name = wiki_filename(original_url)
    alias = IMAGE_ALIASES.get(name or "")
    if alias:
        preferred = catalog_by_identity.get(_image_identity(str(alias["url"])))
        if can_keep(preferred):
            used_assets.add(_image_identity(preferred["url"]))
            return attribute_image_container(
                container,
                str(preferred["source_page"]),
                str(preferred["credit"]),
                str(preferred["alt"]),
                replacement_url=str(preferred["url"]),
            )

    # Already-curated direct URLs (publisher covers, official art, researched gallery
    # images) keep their intended role and source instead of being randomly remapped.
    direct_candidate = catalog_by_identity.get(_image_identity(original_url))
    if can_keep(direct_candidate):
        used_assets.add(_image_identity(original_url))
        return attribute_image_container(
            container,
            str(direct_candidate["source_page"]),
            str(direct_candidate["credit"]),
            str(direct_candidate["alt"]),
        )

    selected = choose_distinct_image(container, relative_path, used_assets, background=False)
    return attribute_image_container(
        container,
        str(selected["source_page"]),
        str(selected["credit"]),
        str(selected["alt"]),
        replacement_url=str(selected["url"]),
    )

def diversify_page_images(relative_path: str, content: str, used_assets: set[str]) -> str:
    # Cards and hero figures get a source-specific credit link, alt text and image.
    content = CARD_OR_FIGURE_RE.sub(
        lambda m: diversify_image_container(m.group(0), relative_path, used_assets),
        content,
    )
    # Handle any remaining image tags not inside a card or figure.
    def replace_orphan_img(match: re.Match[str]) -> str:
        tag = match.group(0)
        src_match = IMG_SRC_RE.search(tag)
        if not src_match:
            return tag
        old_url = src_match.group(2)
        if not is_external_image(old_url) or is_character_reference(old_url):
            return tag
        selected = choose_distinct_image(tag + " " + content[max(0, match.start()-500):match.start()], relative_path, used_assets)
        url = selected["url"]
        alt = selected["context_alt"].replace("&", "&amp;").replace('"', "&quot;")
        credit = selected["credit"].replace("&", "&amp;").replace('"', "&quot;")
        tag = tag[:src_match.start(2)] + url + tag[src_match.end(2):]
        tag = re.sub(r'\balt\s*=\s*(["\']).*?\1', f'alt="{alt}"', tag, count=1, flags=re.IGNORECASE | re.DOTALL)
        tag = re.sub(r'\sdata-wiki-file=(["\']).*?\1', "", tag, flags=re.IGNORECASE | re.DOTALL)
        tag = re.sub(r'\s+srcset=(["\']).*?\1', "", tag, flags=re.IGNORECASE | re.DOTALL)
        return tag
    content = IMG_TAG_RE.sub(replace_orphan_img, content)

    # Every CSS hero/background URL is assigned a fresh image too; no card image
    # or second page may reuse the same background asset.
    def replace_css_background(match: re.Match[str]) -> str:
        old_url = match.group("url").strip()
        if not is_external_image(old_url):
            return match.group(0)
        context = content[max(0, match.start()-1800):min(len(content), match.end()+1800)]
        selected = choose_distinct_image(context, relative_path, used_assets, background=True)
        quote_char = match.group("quote")
        return "url(" + quote_char + selected["url"] + quote_char + ")"
    content = CSS_URL_RE.sub(replace_css_background, content)
    return content



def main() -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    html_css_files = sorted([
        p for p in ROOT.rglob("*")
        if p.is_file()
        and p.suffix.lower() in (".html", ".css")
        and "_site" not in p.parts
        and ".git" not in p.parts
        and "assets/images" not in p.as_posix()
    ], key=lambda p: p.relative_to(ROOT).as_posix())

    references: dict[str, dict[str, str | list[str]]] = {}
    used_noncharacter_assets: set[str] = set()
    for path in html_css_files:
        content = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".html":
            relative_path = path.relative_to(ROOT).as_posix()
            content = apply_context_overrides(relative_path, content)
            content = diversify_page_images(relative_path, content, used_noncharacter_assets)
            path.write_text(content, encoding="utf-8")
        elif path.suffix.lower() == ".css":
            relative_path = path.relative_to(ROOT).as_posix()
            content = diversify_page_images(relative_path, content, used_noncharacter_assets)
            path.write_text(content, encoding="utf-8")
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

    # Repair all card/figure credits from the final localized asset metadata, AFTER
    # src has been rewritten. This keeps source links and captions accurate.
    local_credit_map: dict[str, dict[str, str]] = {}
    for source_meta in references.values():
        asset_path = source_meta.get("asset_path")
        if not asset_path:
            continue
        local_credit_map[str(asset_path)] = {
            "source_page": str(source_meta.get("actual_source_page", source_meta.get("source_page", ""))),
            "credit": str(source_meta.get("actual_credit", source_meta.get("credit", "Image source"))),
            "alt": str(source_meta.get("actual_alt", source_meta.get("alt", "Touhou image"))),
        }

    def repair_final_image_credit(match: re.Match[str]) -> str:
        container = match.group(0)
        img = IMG_TAG_RE.search(container)
        if not img:
            return container
        src_match = IMG_SRC_RE.search(img.group(0))
        if not src_match:
            return container
        metadata = local_credit_map.get(src_match.group(2))
        if not metadata:
            return container
        source_page = metadata["source_page"].replace("&", "&amp;").replace('"', "&quot;")
        credit = metadata["credit"].replace("&", "&amp;").replace('"', "&quot;")
        source_link = f'<a href="{source_page}" target="_blank" rel="noopener">{credit} ↗</a>'

        if re.search(r'<figcaption\b', container, flags=re.IGNORECASE):
            container = re.sub(
                r'<figcaption\b[^>]*>[\s\S]*?</figcaption>',
                '<figcaption class="caption">Image source · ' + source_link + '</figcaption>',
                container,
                count=1,
                flags=re.IGNORECASE,
            )
        if re.search(r'<span\b[^>]*class=["\'][^"\']*\bsmall-source\b[^"\']*["\'][^>]*>', container, flags=re.IGNORECASE):
            container = re.sub(
                r'<span\b[^>]*class=["\'][^"\']*\bsmall-source\b[^"\']*["\'][^>]*>[\s\S]*?</span>',
                '<span class="small-source">Image source: ' + source_link + '</span>',
                container,
                count=1,
                flags=re.IGNORECASE,
            )
        return container

    for path in html_css_files:
        content = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".html":
            content = IMG_TAG_RE.sub(replace_image_tag, content)
            content = CARD_OR_FIGURE_RE.sub(repair_final_image_credit, content)
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
