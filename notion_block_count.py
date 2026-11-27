#!/usr/bin/env python3
"""notion-block-count: estimate how many blocks a Notion workspace uses, from a Markdown export.

Export your workspace from Notion (Settings > Export > Markdown & CSV, include subpages),
then point this at the .zip or the unzipped folder. It counts roughly one block per page title
plus one per non-empty line of content (a fenced code section counts as one block, table
divider lines are skipped). It is an estimate: Notion's own counter may differ, and the export
does not include trashed pages.
"""
import argparse
import json
import os
import sys
import zipfile
import re


def count_blocks(text):
    n = 1  # the page itself (its "# Title" line in the export is this block, not an extra one)
    in_code = False
    first = True
    for line in text.splitlines():
        s = line.strip()
        if first and s:
            first = False
            if s.startswith("# "):
                continue
        if s.startswith("```"):
            if not in_code:
                n += 1
            in_code = not in_code
            continue
        if in_code or not s:
            continue
        if re.fullmatch(r"\|?[\s:|-]+\|?", s) and "-" in s:
            continue  # markdown table divider row
        n += 1
    return n


def iter_pages(path):
    """Yield (relative name, text) for every .md file in a folder or zip (nested zips included)."""
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for f in files:
                p = os.path.join(root, f)
                if f.lower().endswith(".md"):
                    with open(p, encoding="utf-8", errors="replace") as fh:
                        yield os.path.relpath(p, path), fh.read()
                elif f.lower().endswith(".zip"):
                    for item in iter_pages(p):
                        yield item
    else:
        with zipfile.ZipFile(path) as z:
            for name in z.namelist():
                if name.lower().endswith(".md"):
                    yield name, z.read(name).decode("utf-8", errors="replace")
                elif name.lower().endswith(".zip"):
                    import io
                    with zipfile.ZipFile(io.BytesIO(z.read(name))) as inner:
                        for n2 in inner.namelist():
                            if n2.lower().endswith(".md"):
                                yield name + "/" + n2, inner.read(n2).decode("utf-8", errors="replace")


def summarize(path):
    pages = [(name, count_blocks(text)) for name, text in iter_pages(path)]
    by_top = {}
    for name, n in pages:
        top = name.replace("\\", "/").split("/")[0]
        by_top[top] = by_top.get(top, 0) + n
    return {
        "pages": len(pages),
        "total_blocks": sum(n for _, n in pages),
        "by_top_level": sorted(by_top.items(), key=lambda kv: -kv[1]),
        "largest_pages": sorted(pages, key=lambda kv: -kv[1]),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("export", help="Notion Markdown export: .zip or folder")
    ap.add_argument("--top", type=int, default=15, help="how many pages/folders to list")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    s = summarize(a.export)
    if a.json:
        print(json.dumps(s, indent=2))
    else:
        print("pages: %d   estimated blocks: %d" % (s["pages"], s["total_blocks"]))
        print("\nBy top-level folder/page:")
        for k, v in s["by_top_level"][: a.top]:
            print("  %6d  %s" % (v, k))
        print("\nLargest pages:")
        for k, v in s["largest_pages"][: a.top]:
            print("  %6d  %s" % (v, k))
    return 0


if __name__ == "__main__":
    sys.exit(main())
