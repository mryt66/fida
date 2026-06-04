#!/usr/bin/env python3
"""Extract useful assets (images, layouts, code) from a .har file.

Organizes output by category:
  extracted/
    images/    - all images, deduplicated by URL
    html/      - HTML pages (original + with rewritten asset paths)
    css/       - stylesheets
    js/        - scripts
    fonts/     - woff2/woff/ttf
    data/      - JSON API responses
    manifests/ - index of every entry (url, mime, size, status)
"""
import base64
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).parent
HAR_PATH = ROOT / "fida_sklepm.har"
OUT_DIR = ROOT / "extracted"


def sanitize_name(name: str) -> str:
    name = unquote(name)
    name = re.sub(r'[<>:"/\\|?*]+', '_', name)
    return name[:200] or 'index'


def short_hash(b: bytes) -> str:
    import hashlib
    return hashlib.sha1(b).hexdigest()[:10]


def main():
    if not HAR_PATH.exists():
        print(f"HAR file not found: {HAR_PATH}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(HAR_PATH.read_bytes())
    entries = data.get('log', {}).get('entries', [])
    print(f"Loaded {len(entries)} entries from {HAR_PATH.name}")

    cats = {
        'image/':  OUT_DIR / 'images',
        'text/html': OUT_DIR / 'html',
        'text/css': OUT_DIR / 'css',
        'text/javascript': OUT_DIR / 'js',
        'application/javascript': OUT_DIR / 'js',
        'application/json': OUT_DIR / 'data',
        'font/':   OUT_DIR / 'fonts',
        'image/svg': OUT_DIR / 'images' / 'svg',
    }
    for p in cats.values():
        p.mkdir(parents=True, exist_ok=True)

    seen_bytes = {}
    seen_url = {}
    stats = defaultdict(lambda: {'count': 0, 'bytes': 0, 'skipped_dup': 0, 'skipped_404': 0})
    manifest = []

    for idx, e in enumerate(entries):
        req = e.get('request', {})
        resp = e.get('response', {})
        url = req.get('url', '')
        status = resp.get('status', 0)
        content = resp.get('content', {})
        mime = (content.get('mimeType') or '').split(';')[0].strip()
        size = content.get('size', 0) or 0
        text = content.get('text')
        encoding = content.get('encoding', '')

        # decode payload
        payload: bytes
        if text is None:
            payload = b''
        elif encoding == 'base64':
            try:
                payload = base64.b64decode(text)
            except Exception:
                payload = text.encode('utf-8', errors='replace')
        else:
            payload = text.encode('utf-8', errors='replace')

        # pick category
        if mime.startswith('image/'):
            cat = 'images' if not mime.startswith('image/svg') else 'images/svg'
            out_dir = cats['image/'] if not mime.startswith('image/svg') else cats['image/svg']
        elif mime in cats:
            cat = mime
            out_dir = cats[mime]
        elif mime.startswith('font/'):
            cat = 'fonts'
            out_dir = cats['font/']
        else:
            cat = mime or 'unknown'
            out_dir = OUT_DIR / 'other' / (cat.replace('/', '_') or 'unknown')
            out_dir.mkdir(parents=True, exist_ok=True)

        stats[cat]['count'] += 1
        stats[cat]['bytes'] += size

        if status != 200 and status != 204:
            stats[cat]['skipped_404'] += 1
            manifest.append({
                'idx': idx, 'url': url, 'status': status,
                'mime': mime, 'size': size, 'category': cat, 'saved': None,
            })
            continue

        if not payload:
            manifest.append({
                'idx': idx, 'url': url, 'status': status,
                'mime': mime, 'size': size, 'category': cat,
                'saved': None,
                'note': 'response body not captured in HAR (metadata only)',
            })
            continue

        # dedupe by content hash
        h = short_hash(payload)
        if h in seen_bytes:
            stats[cat]['skipped_dup'] += 1
            manifest.append({
                'idx': idx, 'url': url, 'status': status,
                'mime': mime, 'size': size, 'category': cat,
                'saved': str(seen_bytes[h].relative_to(OUT_DIR)),
                'duplicate_of': seen_bytes[h].name,
            })
            continue

        # build filename
        u = urlparse(url)
        path_parts = [p for p in u.path.split('/') if p]
        fname = sanitize_name(path_parts[-1]) if path_parts else 'index'
        # add mime ext if missing
        ext = mime.split('/')[-1].replace('svg+xml', 'svg').replace('javascript', 'js')
        if '.' not in fname or fname.rsplit('.', 1)[-1] != ext:
            fname = f"{fname}.{ext}"
        fname = f"{idx:03d}_{h}_{fname}"
        out_path = out_dir / fname
        out_path.write_bytes(payload)
        seen_bytes[h] = out_path
        seen_url[url] = out_path

        manifest.append({
            'idx': idx, 'url': url, 'status': status,
            'mime': mime, 'size': size, 'category': cat,
            'saved': str(out_path.relative_to(OUT_DIR)),
        })

    # write manifests
    (OUT_DIR / 'manifests').mkdir(exist_ok=True)
    (OUT_DIR / 'manifests' / 'all.json').write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False)
    )

    by_cat = defaultdict(list)
    for m in manifest:
        by_cat[m['category']].append(m)
    for cat, items in by_cat.items():
        (OUT_DIR / 'manifests' / f'{cat.replace("/", "_")}.json').write_text(
            json.dumps(items, indent=2, ensure_ascii=False)
        )

    # human summary
    no_body = sum(1 for m in manifest if m.get('note') == 'response body not captured in HAR (metadata only)')
    print('\n' + '=' * 60)
    print(f"{'Category':<22} {'Files':>6} {'Bytes':>12} {'Dup':>6} {'Skip':>6}")
    print('-' * 60)
    for cat, s in sorted(stats.items(), key=lambda x: -x[1]['bytes']):
        print(f"{cat:<22} {s['count']:>6} {s['bytes']:>12,} "
              f"{s['skipped_dup']:>6} {s['skipped_404']:>6}")
    print('=' * 60)
    print(f"\nOutput: {OUT_DIR}")
    print(f"Total saved:    {len(seen_bytes):>5} files  "
          f"({sum(s['bytes'] for s in stats.values())/1024/1024:.2f} MB referenced)")
    print(f"Total dedup'd:  {len(manifest)-len(seen_bytes)-sum(s['skipped_404'] for s in stats.values()):>3} entries")
    print(f"Metadata-only:  {no_body:>5} entries (URLs in manifests/, bodies not in HAR)")

    # write a flat URL list for re-fetching
    urls_for_refetch = sorted({
        m['url'] for m in manifest
        if m.get('note') == 'response body not captured in HAR (metadata only)'
    })
    (OUT_DIR / 'manifests' / 'refetch_urls.txt').write_text(
        '\n'.join(urls_for_refetch) + '\n'
    )
    print(f"Re-fetch list:  {OUT_DIR / 'manifests' / 'refetch_urls.txt'}")


if __name__ == '__main__':
    main()
