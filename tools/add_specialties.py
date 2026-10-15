#!/usr/bin/env python3
"""Fold one or more specialty-data/*.txt files into data.js.

An acronym+meaning pair that already exists (same acronym spelling and case; meaning compared case/punctuation-insensitively) gets the new
weight (4th field) raised by one: tags are the 1-3 home specialties only, and the weight = how many
lists carry the meaning, used to rank common meanings first. A new meaning is inserted after the last existing line
for that acronym, or appended at the end. Usage: tools/add_specialties.py file.txt ...
"""
import re, sys, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
djs = root / "data.js"
src = djs.read_text()
m = re.search(r"const DICT = `\n(.*?)`", src, re.S)
head, body, tail = src[:m.start(1)], m.group(1), src[m.end(1):]
lines = [l for l in body.split("\n") if l.strip()]
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
rows = [l.split("|") for l in lines]
idx = {(r[0].strip(), norm(r[1])): i for i, r in enumerate(rows)}  # case matters: pt vs PT
last = {}
for i, r in enumerate(rows):
    last[norm(r[0])] = i
added = merged = bad = 0
inserts = {}  # index -> list of new rows to place after it
appends = []
for f in sys.argv[1:]:
    seen = set()
    for ln in pathlib.Path(f).read_text().splitlines():
        p = [x.strip() for x in ln.split("|")]
        if len(p) != 3 or not all(p) or "`" in ln or "\\" in ln:
            if ln.strip(): bad += 1; print("skip:", ln, file=sys.stderr)
            continue
        a, mn, sp = p
        key = (a, norm(mn))
        if not norm(a) or key in seen: continue
        seen.add(key)
        if key in idx:
            i = idx[key]
            if i is None:  # already newly added from another file
                continue
            if isinstance(i, tuple):
                r = i[1]
            else:
                r = rows[i]
            # tags are home specialties only; another list carrying the meaning raises its weight (4th field) instead
            if sp not in r[2].split(", "):
                if len(r) < 4: r.append("1")
                r[3] = str(int(r[3]) + 1); merged += 1
            continue
        r = [a, mn, sp]
        if norm(a) in last:
            inserts.setdefault(last[norm(a)], []).append(r)
        else:
            appends.append(r)
        idx[key] = ("new", r); added += 1
out = []
for i, r in enumerate(rows):
    out.append(r)
    out.extend(inserts.get(i, []))
out.extend(sorted(appends, key=lambda r: r[0].lower()))
djs.write_text(head + "\n".join("|".join(r) for r in out) + "\n" + tail)
print(f"added {added} new meanings, tagged {merged} existing ones, skipped {bad} bad lines; total {len(out)}")
