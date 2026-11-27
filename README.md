# notion-block-count

Estimates how many blocks a Notion workspace uses, from a Markdown export, and shows which top-level pages and pages are biggest. Python 3 standard library only.

**Problem (Reddit):** [Apparently deleting blocks don't reduce your total block usage? How do I find how many blocks I've used?](https://www.reddit.com/r/Notion/comments/1y5iwml/) (r/Notion), alongside [What do you mean 5k blocks?](https://www.reddit.com/r/Notion/comments/1y56kjk/). Posters want to know their block count against the new free plan limit, and the thread reports a limit of 5,000 blocks. Check Notion's own plan page for the current number.

## Use
1. In Notion: Settings > Export > Markdown & CSV, include subpages. Download the zip.
2. Run:
```
python3 notion_block_count.py Export-xxxx.zip
python3 notion_block_count.py Export-xxxx.zip --top 30 --json
```
It counts one block per page plus one per non-empty content line (the title line is the page itself) (a fenced code section is one block; table divider lines are skipped). This is an estimate: Notion's counter may differ, and trashed pages are not in an export, so deleted blocks that still count toward the limit will not show here.

## Test
`python3 -m unittest -v`
