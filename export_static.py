"""
export_static.py

Render the Flask app to static HTML files under `dist/` and copy `static/` assets.

This script imports the Flask `app` from `app.py` and uses the test client
to request each route, then writes the HTML to the appropriate output path
so Netlify can serve the site as a static site.

Usage:
  python export_static.py

Notes:
 - Ensure any dynamic routes (projects, blog posts) are exported by reading
   `portfolio_data.json` and creating the per-item pages.
 - The script will create `dist/` directory and copy `static/` into it.
"""

import os
import shutil
import errno
from pathlib import Path

from app import app
import json

ROOT = Path(__file__).parent
DIST = ROOT / 'dist'

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def write_file(path: Path, content: str):
    ensure_dir(path.parent)
    path.write_text(content, encoding='utf-8')

def fetch_and_write(client, route: str, out_path: Path):
    print(f"Fetching {route} -> {out_path}")
    resp = client.get(route)
    if resp.status_code >= 400:
        print(f"Warning: {route} returned status {resp.status_code}")
    content = resp.get_data(as_text=True)
    write_file(out_path, content)

def main():
    # Remove old dist
    if DIST.exists():
        shutil.rmtree(DIST)
    ensure_dir(DIST)

    # Copy static assets
    static_src = ROOT / 'static'
    static_dst = DIST / 'static'
    if static_src.exists():
        print('Copying static/ to dist/static/')
        shutil.copytree(static_src, static_dst)
    else:
        print('No static/ directory found; skipping asset copy')

    # Load portfolio data to discover dynamic routes
    data_file = ROOT / 'portfolio_data.json'
    if data_file.exists():
        data = json.loads(data_file.read_text(encoding='utf-8'))
    else:
        data = {}

    # Instantiate test client
    client = app.test_client()

    # Routes to export (top-level)
    routes = ['/', '/projects', '/about', '/contact', '/skills', '/certifications', '/education', '/blog']

    # Add project detail pages
    for p in data.get('projects', []):
        pid = p.get('id')
        if pid:
            routes.append(f'/projects/{pid}')

    # Add blog posts by slug
    for a in data.get('articles', []):
        slug = a.get('slug') or a.get('id')
        if slug:
            routes.append(f'/blog/{slug}')

    # Export each route into dist/<route>/index.html (so Netlify serves it correctly)
    for route in sorted(set(routes)):
        if route == '/':
            out = DIST / 'index.html'
        else:
            # strip leading slash
            sub = route.lstrip('/')
            out = DIST / sub / 'index.html'
        fetch_and_write(client, route, out)

    # Also copy robots and favicon if present in root
    for fname in ['robots.txt', 'favicon.ico']:
        fp = ROOT / fname
        if fp.exists():
            shutil.copy(fp, DIST / fname)

    print('Static export complete. Output in dist/')

if __name__ == '__main__':
    main()
