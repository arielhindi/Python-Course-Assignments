from day09 import report
import os


def test_parse_deadlines_and_report(tmp_path, monkeypatch):
    # create a temporary README and subjects file
    readme = tmp_path / "README.md"
    readme.write_text("""
Deadlines
- Assignment 1 - 2025-11-30
- Assignment 2 - 2025-12-01
""")

    subjects = tmp_path / "subjects.txt"
    subjects.write_text("""
Alice,Assignment 1,2025-11-25
Alice,Assignment 2,
Bob,Assignment 1,2025-12-02
""")

    # call build_report with our temp files
    rpt = report.build_report(str(subjects), str(readme))
    assert "Assignment 1" in rpt
    assert "missing" in rpt
    assert "Late submissions" in rpt
