# day09 — Deadlines

This README contains the deadlines for assignments. The report generator in
this folder reads `subjects.txt` (student submissions) and these deadlines to
produce a short report of missing or late submissions.

Deadlines
---------
- Assignment 1 (day 1) - 2025-11-01 22:00 UTC
  - Amendment (AI disclosure): 2025-11-02 22:00 UTC
- Assignment 2 (day 2) - 2025-11-09 22:00 UTC
- Assignment 3 (day 3) - 2025-11-16 22:00 UTC
- Assignment 4 (day 4) - 2025-11-23 22:00 UTC
- Assignment 5 (day 5) - 2025-11-29 22:00 UTC
 - Assignment 6 (day 6) - 2025-12-06 22:00 UTC
- Assignment 8 (day 8) - 2025-12-30 22:00 UTC
- Assignment (day 9) - 2026-01-10 22:00 (Saturday evening) UTC
- Project proposal deadline - 2026-01-11 22:00 (Sunday evening) UTC
- Project submission deadline - 2026-01-25 22:00 (Sunday evening) UTC

Notes
-----
- Note: Day 7 did not have an assignment during this course.
- `subjects.txt` uses a simple CSV-like format: `student,assignment,submission_date`.
- Empty submission_date means the student hasn't submitted (or it hasn't been
  recorded).

Updater script
--------------
If you'd like to keep `day09/subjects.txt` synced with an upstream copy, there's
an updater script you can run locally: `day09/update_subjects.py`.

Basic usage (updates the local file only):

```bash
python -m day09.update_subjects
```

To fetch from a specific raw URL and create a local git commit (push not
performed automatically):

```bash
python -m day09.update_subjects --url <RAW_URL> --commit --commit-message "Update subjects"
```

Cron example (run nightly at 3:30am):

```cron
30 3 * * * cd /path/to/repo && /usr/bin/python3 -m day09.update_subjects --url <RAW_URL> >> ~/day09_update.log 2>&1
```

The script makes a timestamped backup of the previous file before overwriting.
Use `--no-backup` to skip that behavior.
