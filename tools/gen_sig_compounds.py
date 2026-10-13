#!/usr/bin/env python3
"""Write specialty-data/dosing-sig-compounds.txt: run-together dosing schedules seen in real orders.

Prescribers glue a frequency to meal timing or PRN (TIDAC, BIDPC, QHSPRN, Q6HPRN). Only forms
that are actually written are listed; any other combination is still read by the schedule
parser in index.html, so it does not need an entry. Search ignores spaces, dots and dashes,
so "TID AC", "T.I.D. A.C." and "tid-ac" all find TIDAC.
Usage: tools/gen_sig_compounds.py && tools/add_specialties.py specialty-data/dosing-sig-compounds.txt
"""
import pathlib
root = pathlib.Path(__file__).resolve().parent.parent
FORMS = [("ACHS", "Before meals and at bedtime"), ("QAC", "Before each meal"), ("QACHS", "Before each meal and at bedtime"),
         ("QDAC", "Once daily before meals"), ("BIDAC", "Twice daily before meals"), ("BIDPC", "Twice daily after meals"),
         ("TIDAC", "Three times daily before meals"), ("TIDPC", "Three times daily after meals"),
         ("QAMAC", "Every morning before meals"), ("TIDACHS", "Three times daily before meals and at bedtime"),
         ("QIDACHS", "Four times daily before meals and at bedtime"),
         ("QDPRN", "Once daily as needed"), ("Daily PRN", "Daily as needed"), ("BIDPRN", "Twice daily as needed"),
         ("TIDPRN", "Three times daily as needed"), ("QIDPRN", "Four times daily as needed"), ("QHSPRN", "At bedtime as needed"),
         ("Q2HPRN", "Every 2 hours as needed"), ("Q3HPRN", "Every 3 hours as needed"), ("Q4HPRN", "Every 4 hours as needed"),
         ("Q6HPRN", "Every 6 hours as needed"), ("Q8HPRN", "Every 8 hours as needed"),
         ("Q4-6HPRN", "Every 4 to 6 hours as needed"), ("Q2-4HPRN", "Every 2 to 4 hours as needed")]
out = root / "specialty-data" / "dosing-sig-compounds.txt"
out.write_text("".join(f"{a}|{m}|Chart Shorthand\n" for a, m in FORMS))
print(f"wrote {len(FORMS)} lines to {out}")
