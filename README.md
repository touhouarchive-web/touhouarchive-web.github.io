# TouhouArchive

A responsive, multi-page, canon-conscious Touhou Project reference website. It is an independent fan project and is not affiliated with Team Shanghai Alice.

## Pages

- `index.html` — home and archive lobby
- `pages/introduction.html` — introduction and beginner's guide
- `pages/characters.html` — character directory
- `pages/games.html` — games and incident overview
- `pages/locations.html` — Gensokyo locations
- `pages/spell-cards.html` — spell-card guide
- `pages/music.html` — music reference
- `pages/print-works.html` — official print works
- `pages/chronology.html` — series and in-universe chronology
- `pages/canon.html` — canon policy
- `pages/sources.html` — source register and image credits

## Deploy to GitHub Pages

This repository includes `.github/workflows/deploy.yml`. Once these files are pushed to the `main` branch of the repository `touhouarchive-web/touhouarchive-web.github.io`, GitHub Actions deploys the static website automatically.

1. Use the public repository `touhouarchive-web/touhouarchive-web.github.io` (already created).
2. Upload the contents of this folder to the repository root, preserving `.github/`, `assets/`, and `pages/`.
3. In the repository, open **Settings → Pages** and set **Build and deployment → Source** to **GitHub Actions**.
4. Open **Actions** and wait for **Deploy TouhouArchive to GitHub Pages** to succeed. Future pushes to `main` redeploy automatically.

The intended live URL is `https://touhouarchive-web.github.io/`. It will work after the site files are committed to `main`, the Pages source is set to **GitHub Actions**, and the deployment workflow succeeds.

## Images and performance

Most content images use `loading="lazy"` and `decoding="async"`. Images are referenced from the original websites rather than bundled locally, so an internet connection is needed and external hosts can change availability or block hotlinking. Captions and the source register identify image sources.

## Canon and copyright

Official games, books, manga, and creator statements should be prioritised. Interpretations are labelled as interpretations, and fanon is not presented as confirmed canon. Rights to Touhou characters, games, music, and referenced images belong to their respective creators and rights holders.
