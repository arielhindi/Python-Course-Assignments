"""Produce submission reports for day09 subjects.

Usage:
    python -m day09.report

The script reads `day09/subjects.txt` and `day09/README.md` (for deadlines).
It prints:
- Students who have not submitted each assignment
- Students who submitted late (submission date > deadline)

The file formats are intentionally simple so the script is easy to adapt.
"""
from __future__ import annotations

import os
import re
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

ROOT = os.path.dirname(__file__)
SUBJECTS_PATH = os.path.join(ROOT, "subjects.txt")
README_PATH = os.path.join(ROOT, "README.md")


def parse_deadlines(readme_path: str) -> Dict[str, datetime]:
    """Parse deadlines from the README file.

    Expects lines like: "- Assignment 1 - 2025-11-30 22:00 UTC" or
    "- Assignment 1 (day 1) - 2025-11-30". The date/time part may include an
    optional time and timezone (e.g. "2025-11-01 22:00 UTC" or
    "2026-01-03T18:44:38Z").

    Returns a dict mapping assignment name -> deadline (datetime)
    """
    if not os.path.exists(readme_path):
        return {}
    # capture an assignment line and an ISO-like date/time (date with optional time)
    pattern = re.compile(
        r"^\s*-\s*(?P<assignment>.+?)\s*-\s*(?P<date>\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}(?::\d{2})?)?(?:Z| UTC)?)",
        re.MULTILINE,
    )
    with open(readme_path, "r", encoding="utf-8") as fh:
        txt = fh.read()
    deadlines: Dict[str, datetime] = {}
    for m in pattern.finditer(txt):
        name = m.group("assignment").strip()
        raw = m.group("date").strip()
        # remove any parenthetical notes that might have been included
        raw = re.sub(r"\(.*?\)", "", raw).strip()
        # normalize common timezone markers
        try:
            if raw.endswith("Z"):
                # convert Z to +00:00 for fromisoformat
                dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            else:
                # strip trailing 'UTC' token if present
                if raw.upper().endswith("UTC"):
                    raw = raw[: -3].strip()
                # ensure a T separator for full ISO formats when time exists
                if " " in raw and "T" not in raw and ":" in raw:
                    raw = raw.replace(" ", "T", 1)
                dt = datetime.fromisoformat(raw)
        except Exception:
            # fallback: parse just the date portion
            try:
                date_only = re.search(r"\d{4}-\d{2}-\d{2}", raw)
                if date_only:
                    dt = datetime.fromisoformat(date_only.group(0))
                else:
                    continue
            except Exception:
                continue

        # store primary key as the raw assignment name
        deadlines[name] = dt

        # also add a few normalized keys to improve lookup from subjects file
        # e.g. allow 'Day9', 'Day 9', 'day9' variants when README used
        day_match = re.search(r"day\s*0*(\d+)", name, re.IGNORECASE)
        if day_match:
            num = int(day_match.group(1))
            alt_keys = [f"Day{num:02d}", f"Day {num}", f"Day{num}", f"day{num}"]
            for k in alt_keys:
                if k not in deadlines:
                    deadlines[k] = dt
    return deadlines


def parse_subjects(subjects_path: str) -> List[Tuple[str, str, Optional[datetime]]]:
    """Parse the subjects file.

    Each non-empty non-comment line is expected to be:
        student,assignment,submission_date
    Where submission_date is optional (empty) or ISO date. Returns list of
    tuples (student, assignment, submission_date_or_None)
    """
    if not os.path.exists(subjects_path):
        raise FileNotFoundError(subjects_path)

    rows: List[Tuple[str, str, Optional[datetime]]] = []
    iso_ts_re = re.compile(r"\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}(?::\d{2})?)?(?:Z|[+-]\d{2}:?\d{2}| UTC)?")

    with open(subjects_path, "r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue

            # prefer tab-separated columns (the file usually comes from a GitHub issues export)
            parts = [p for p in line.split("\t") if p != ""]
            # fallback: split by two-or-more spaces
            if len(parts) < 3:
                parts = [p for p in re.split(r"\s{2,}", line) if p]

            assignment_field = None
            timestamp_str = None
            # Heuristic: the assignment/title is usually the 3rd column and the timestamp is the last
            if parts:
                if len(parts) >= 3:
                    assignment_field = parts[2].strip()
                    # timestamp may be last field
                    timestamp_str = parts[-1].strip()
                elif len(parts) == 2:
                    # maybe 'assignment' and 'timestamp'
                    assignment_field = parts[0].strip()
                    timestamp_str = parts[1].strip()
                else:
                    assignment_field = parts[0].strip()

            # If timestamp_str doesn't look like an ISO timestamp, try to find one anywhere in the line
            if not timestamp_str or not iso_ts_re.search(timestamp_str):
                m = iso_ts_re.search(line)
                timestamp_str = m.group(0) if m else None

            # Default student/assignment parsing: expect a pattern like "<assignment> by <student>"
            student = ""
            assignment = assignment_field or ""
            if assignment:
                m = re.search(r"^(?P<assignment>.+?)\s+by\s+(?P<student>.+)$", assignment, re.IGNORECASE)
                if m:
                    assignment = m.group("assignment").strip()
                    student = m.group("student").strip()
                else:
                    # Some rows use formats like "Day05 and 06 by Name" or include extra text
                    # Try to extract a trailing "by NAME"
                    m2 = re.search(r"by\s+(?P<student>[^\t\n]+)$", assignment, re.IGNORECASE)
                    if m2:
                        student = m2.group("student").strip()
                        assignment = re.sub(r"by\s+[^\t\n]+$", "", assignment, flags=re.IGNORECASE).strip()

            # If student still empty, try to infer from other columns (some files put name earlier)
            if not student and len(parts) >= 4:
                # e.g. parts[3] might contain the student in some exports
                candidate = parts[3].strip()
                if candidate and not iso_ts_re.search(candidate):
                    student = candidate

            # If student still empty, leave as empty string (the report groups by student keys later)

            # parse timestamp
            date: Optional[datetime] = None
            if timestamp_str:
                ts = timestamp_str.strip()
                try:
                    if ts.endswith("Z"):
                        date = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    else:
                        if ts.upper().endswith("UTC"):
                            ts = ts[: -3].strip()
                        if " " in ts and "T" not in ts and ":" in ts:
                            ts = ts.replace(" ", "T", 1)
                        date = datetime.fromisoformat(ts)
                except Exception:
                    # fallback: parse date-only
                    dmatch = re.search(r"\d{4}-\d{2}-\d{2}", ts)
                    if dmatch:
                        try:
                            date = datetime.fromisoformat(dmatch.group(0))
                        except Exception:
                            date = None

                # Normalize student name and assignment keys; some assignment fields list multiple days
                def normalize_student_name(name: str) -> str:
                    if not name:
                        return ""
                    # strip, collapse whitespace, title-case
                    n = re.sub(r"\s+", " ", name.strip())
                    # title() is good enough for most names here
                    return n.title()

                def normalize_assignment_keys(a: str) -> List[str]:
                    if not a:
                        return [""]
                    s = a.strip()
                    # common canonicalization for final project proposal
                    if re.search(r"final\s*project", s, re.IGNORECASE):
                        return ["Final Project Proposal"]
                    # find all day numbers: "Day 05", "Day05", etc.
                    nums = [int(m.group(1)) for m in re.finditer(r"day\s*0*(\d+)", s, re.IGNORECASE)]
                    if nums:
                        # if multiple days listed (e.g. "Day05 and 06"), return each
                        keys = [f"Day{n:02d}" for n in nums]
                        return keys
                    # fallback: return cleaned text as-is (trim and collapse spaces)
                    return [re.sub(r"\s+", " ", s).strip()]

                student_norm = normalize_student_name(student)
                assignment_keys = normalize_assignment_keys(assignment)

                for key in assignment_keys:
                    rows.append((student_norm, key, date))


    return rows


def build_report(subjects_file: str, readme_file: str) -> str:
    """Build a textual report summarizing missing and late submissions."""
    deadlines = parse_deadlines(readme_file)
    rows = parse_subjects(subjects_file)

    # collect set of students and assignments
    students = set()
    assignments = set()
    by_student_assignment: Dict[Tuple[str, str], Optional[datetime]] = {}
    for student, assignment, date in rows:
        students.add(student)
        assignments.add(assignment)
        by_student_assignment[(student, assignment)] = date

    # For any assignment missing for a student, treat as not submitted
    report_lines: List[str] = []
    report_lines.append("Submission report")
    report_lines.append("=================")
    report_lines.append("")

    # Missing submissions per assignment
    report_lines.append("Students missing submissions per assignment:\n")
    for a in sorted(assignments):
        missing = [s for s in sorted(students) if by_student_assignment.get((s, a)) is None]
        report_lines.append(f"- {a}: {len(missing)} missing")
        if missing:
            report_lines.append("  " + ", ".join(missing))
        report_lines.append("")

    # Late submissions
    report_lines.append("Late submissions:\n")
    late_found = False
    for (s, a), date in sorted(by_student_assignment.items()):
        if date is None:
            continue
        deadline = deadlines.get(a)
        if deadline and date.date() > deadline.date():
            late_found = True
            report_lines.append(f"- {s} — {a}: submitted {date.date()} (deadline {deadline.date()})")
    if not late_found:
        report_lines.append("None")

    report_lines.append("")
    # Per-student summary
    report_lines.append("Per-student summary:")
    for s in sorted(students):
        submitted = [a for a in sorted(assignments) if by_student_assignment.get((s, a))]
        missing = [a for a in sorted(assignments) if by_student_assignment.get((s, a)) is None]
        report_lines.append(f"- {s}: submitted {len(submitted)}, missing {len(missing)}")
    report_lines.append("")

    return "\n".join(report_lines)


def main():
    report = build_report(SUBJECTS_PATH, README_PATH)
    print(report)


if __name__ == '__main__':
    main()
