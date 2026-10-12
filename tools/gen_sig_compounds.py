#!/usr/bin/env python3
"""Generate specialty-data/dosing-sig-compounds.txt: every run-together dosing schedule.

Prescribers glue a frequency to a meal/bedtime timing or to PRN (TIDAC, BIDPC, QHSPRN,
Q6HPRN, QAMAC). Each piece is in the dictionary on its own, but the glued forms were never
listed, so a search for TIDAC found nothing. This builds the whole frequency x timing grid
so no member of the family is left out. One spelling per form is enough: search ignores
spaces, dots and dashes, so "TID AC", "T.I.D. A.C." and "tid-ac" all find TIDAC.
Usage: tools/gen_sig_compounds.py && tools/add_specialties.py specialty-data/dosing-sig-compounds.txt
"""
import pathlib
root = pathlib.Path(__file__).resolve().parent.parent
SPEC = "Chart Shorthand"

DAILY = [("QD", "Once daily"), ("BID", "Twice daily"), ("TID", "Three times daily"),
         ("QID", "Four times daily"), ("QAM", "Every morning"), ("QPM", "Every evening")]
MEAL = [("AC", "before meals"), ("PC", "after meals"), ("WM", "with meals")]
BED = [("ACHS", "before meals and at bedtime"), ("PCHS", "after meals and at bedtime")]
PRN_BASE = DAILY + [("Daily ", "Daily"), ("QHS", "At bedtime"), ("HS", "At bedtime"), ("QOD", "Every other day"),
                    ("ACHS", "Before meals and at bedtime")] + \
           [("Q1H", "Every hour")] + [(f"Q{n}H", f"Every {n} hours") for n in (2, 3, 4, 6, 8, 12, 24)] + \
           [("Q4-6H", "Every 4 to 6 hours"), ("Q6-8H", "Every 6 to 8 hours"), ("Q2-4H", "Every 2 to 4 hours")]

rows = []
add = lambda a, m: rows.append(f"{a}|{m}|{SPEC}")
# timing on its own
add("ACHS", "Before meals and at bedtime")
add("PCHS", "After meals and at bedtime")
add("QAC", "Before each meal")
add("QPC", "After each meal")
add("QACHS", "Before each meal and at bedtime")
add("WM", "With meals")
# frequency + meal timing (TIDAC, BIDPC, QAMAC ...)
for f, fm in DAILY:
    for t, tm in MEAL:
        add(f + t, f"{fm} {tm}")
for f, fm in [("BID", "Twice daily"), ("TID", "Three times daily"), ("QID", "Four times daily")]:
    for t, tm in BED:
        add(f + t, f"{fm} {tm}")
add("QHSAC", "At bedtime and before meals")
# frequency + PRN (Q6HPRN, BIDPRN, QHSPRN ...)
for f, fm in PRN_BASE:
    add(f + "PRN", f"{fm} as needed")
# meal timing + PRN
for t, tm in MEAL:
    add(t + "PRN", f"{tm[0].upper() + tm[1:]} as needed")

out = root / "specialty-data" / "dosing-sig-compounds.txt"
out.write_text("\n".join(dict.fromkeys(rows)) + "\n")
print(f"wrote {len(dict.fromkeys(rows))} lines to {out}")
