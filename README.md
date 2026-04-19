# NEXTON OSS site

This repo is a static GitHub Pages site with:
- English home page at `/`
- French home page at `/index-fr.html`
- Open Graph and Twitter preview metadata
- Structured data via JSON-LD
- `robots.txt`, `sitemap.xml` and `llms.txt`

## Local Development & Updating Content

Content is driven by JSON files in the `data/` directory and generated via a Python script.

1. **Update Repositories**: Add or modify JSON files in the `data/` folder.
2. **Add Images**: Place your square visuals in `assets/images/`.
3. **Build**: Run the build script to generate the HTML files:
   ```bash
   python3 scripts/build.py
   ```

## Publish
Create the repository `nexton-oss.github.io`, push these files, then enable GitHub Pages via the default static deployment (or GitHub Actions if configured).
