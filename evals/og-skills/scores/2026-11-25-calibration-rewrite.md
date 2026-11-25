# Scores 2026-11-25: og-country-calibration rewrite

Variants: `old` = Model-tools 5deba93 (skills/calibration-revision before the rewrite); `new` = the
rewrite (7596a61). One fresh agent per variant and scenario set, reading only that variant's skills
folder and `docs/og-lessons/`; one blind grader (answers labelled X/Y in random order per scenario).
Model: Opus 5.5 for answers and grading. S14–S19 were written for this round from the ETH and ZAF
cases behind the new lessons, so they favour `new`; S1–S11 are the earlier set.

| Scenario (max) | old | new |
|---|---|---|
| S1 new country from a sibling (10) | 8 | 9 |
| S2 auditing a calibration (9) | 7 | 8 |
| S5 large net creditor (6) | 6 | 6 |
| S10 borrowed labour supply (5) | 5 | 4 |
| S11 first-year consumption windfall (5) | 4 | 4 |
| S14 two capital-output ratios (5) | 4 | 5 |
| S15 old-age hours at the bound (5) | 3 | 5 |
| S16 transfers per person by age (5) | 2 | 5 |
| S17 reviewing a calibration PR draft (6) | 4 | 6 |
| S18 budget identity with aid (4) | 2 | 3 |
| S19 cross-country outlier (4) | 3 | 4 |
| **Total (64)** | **48** | **59** |

Errors the grader flagged that trace to the old skill: S17 kept the reform table and tested block
(old calibration-pr.md); S18 divided `pb*` by `1 + g` (old fiscal-consistency.md); S16 had no
guidance on `eta`; S10 called the earnings rescale exact with nothing else scaled.

Gaps in `new` acted on: the front page did not name Anderson with `nu` at most 0.2 or the check
before a run (S1 point 7), nor the progressive income-tax form (S2 point 3). Misses judged as answer
choices with the guidance present: S10 point 2, S11 point 5, S18 point 4.

Answers, blind file, key and grades: og-analysis/skill-review/eval-run/ (local).

Note: after scoring, S14's prompt was changed so the PPP ratio is the higher one (3.0 against 2.2), as in the case behind it; the answers above used the earlier numbers.
