#!/usr/bin/env python3
"""Audit data.js against an independent checklist (tests/must-have.txt, `ACRONYM|Meaning`).

Reports two kinds of gap:
  MISSING  the acronym is not in the dictionary under any spelling
  MEANING  the acronym exists, but no stored meaning shares a content word with the checklist meaning
Writes the gaps to tests/gaps.txt in `ACRONYM|Meaning` form so they can be reviewed and added.
"""
import re, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
body = re.search(r"const DICT = `\n(.*?)`", (root / "data.js").read_text(), re.S).group(1)
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
STOP = set("of the and to with for in on a an by per or at from as is".split())
words = lambda s: {w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in STOP and len(w) > 2}
have = {}
for ln in body.splitlines():
    p = ln.split("|")
    if len(p) == 3:
        have.setdefault(norm(p[0]), []).append(p[1])
missing, meaning = [], []
for ln in (root / "tests" / "must-have.txt").read_text().splitlines():
    p = [x.strip() for x in ln.split("|")]
    if len(p) != 2 or not p[0]:
        continue
    a, m = p
    got = have.get(norm(a))
    if not got:
        missing.append(ln)
    elif words(m) and not any(words(m) & words(g) for g in got):
        meaning.append(ln)
(root / "tests" / "gaps.txt").write_text("\n".join(missing + meaning) + "\n")
total = sum(1 for l in (root / "tests" / "must-have.txt").read_text().splitlines() if "|" in l)
print(f"checked {total}: {len(missing)} acronyms missing, {len(meaning)} meanings missing; see tests/gaps.txt")
