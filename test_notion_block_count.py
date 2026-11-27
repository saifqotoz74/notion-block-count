import os, tempfile, unittest, zipfile
import notion_block_count as n

PAGE = "# Title\n\nSome text\nmore text\n\n- a\n- b\n\n```\ncode 1\n\ncode 2\n```\n\n| h1 | h2 |\n| --- | --- |\n| x | y |\n"


class T(unittest.TestCase):
    def test_count(self):
        # page 1 + 2 text + 2 bullets + 1 code + header row + body row = 8 (title line is the page)
        self.assertEqual(n.count_blocks(PAGE), 1 + 2 + 2 + 1 + 1 + 1)

    def test_empty_page(self):
        self.assertEqual(n.count_blocks(""), 1)

    def test_folder_and_zip(self):
        d = tempfile.mkdtemp()
        os.makedirs(os.path.join(d, "Notes"))
        open(os.path.join(d, "Notes", "a.md"), "w").write("# A\ntext\n")
        open(os.path.join(d, "b.md"), "w").write("# B\n")
        open(os.path.join(d, "skip.csv"), "w").write("x,y\n1,2\n")
        s = n.summarize(d)
        self.assertEqual((s["pages"], s["total_blocks"]), (2, 3))
        self.assertEqual(s["by_top_level"][0], ("Notes", 2))
        z = os.path.join(d, "e.zip")
        with zipfile.ZipFile(z, "w") as zz:
            zz.writestr("Notes/a.md", "# A\ntext\n")
        self.assertEqual(n.summarize(z)["total_blocks"], 2)

    def test_nested_zip(self):
        d = tempfile.mkdtemp()
        inner = os.path.join(d, "in.zip")
        with zipfile.ZipFile(inner, "w") as zz:
            zz.writestr("p.md", "# P\nx\ny\n")
        outer = os.path.join(d, "out.zip")
        with zipfile.ZipFile(outer, "w") as zz:
            zz.write(inner, "Export-1.zip")
        self.assertEqual(n.summarize(outer)["total_blocks"], 3)


if __name__ == "__main__":
    unittest.main()
