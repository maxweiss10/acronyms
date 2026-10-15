#!/usr/bin/env python3
"""Audit data.js against independent checklists (tests/must-have.txt and tests/notes-checklist.txt, `ACRONYM|Meaning`).

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
# compare hyphenated words both joined and split, so non-contrast = noncontrast and follow-up = follow up
_w = lambda s: {w for w in re.findall(r"[a-z0-9]+", s) if w not in STOP and len(w) > 2}
words = lambda s: _w(s.lower()) | _w(s.lower().replace("-", ""))
have = {}
for ln in body.splitlines():
    p = ln.split("|")
    if len(p) in (3, 4):  # 4th field: how many leading specialty tags are co-equal homes
        have.setdefault(norm(p[0]), []).append(p[1])
missing, meaning = [], []
LISTS = [root / "tests" / f for f in ("must-have.txt", "notes-checklist.txt")]
checklist = [ln for f in LISTS for ln in f.read_text().splitlines() if not ln.startswith("#")]
for ln in checklist:
    p = [x.strip() for x in ln.split("|")]
    if len(p) != 2 or not p[0]:
        continue
    a, m = p
    if not re.search(r"[A-Za-z]", a):  # symbols and bare numbers are out of scope
        continue
    k = norm(a)
    got = have.get(k) or (have.get(k[:-1]) if len(k) > 2 and k.endswith("s") else None)  # site reads plurals
    if not got:
        missing.append(ln)
    elif words(m) and not any(words(m) & words(g) for g in got):
        meaning.append(ln)
(root / "tests" / "gaps.txt").write_text("\n".join(missing + meaning) + "\n")
total = sum(1 for l in checklist if "|" in l)
print(f"checked {total}: {len(missing)} acronyms missing, {len(meaning)} meanings missing; see {root / 'tests' / 'gaps.txt'}")
