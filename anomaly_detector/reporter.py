import csv
import logging
from pathlib import Path
from typing import List, Dict

from anomaly_detector.parser import Issue


def anomaly_reporter(validated_issues: List[Dict[int, List[Issue]]], output_path: Path, dry_run: bool = False) -> None:

    if dry_run:
        for issues_per_loan in validated_issues:
            for loan_id, issues in issues_per_loan.items():
                if issues:
                    for issue in issues:
                        row = {
                            "loan_id": loan_id,
                            "severity": issue.severity,
                            "code": issue.code,
                            "field": issue.field,
                            "message": issue.message,
                            "value": issue.value,

                        }
                        logging.info(f"[DRY-RUN] Would write row: {row}")

        return

    with open(output_path, "w", newline="", encoding="utf-8") as file_io:
        writer = csv.DictWriter(file_io, fieldnames=["loan_id", "severity", "code", "field", "message", "value"])
        writer.writeheader()
        for issues_per_loan in validated_issues:
            for loan_id, issues in issues_per_loan.items():
                if issues:
                    for issue in issues:
                        row = {
                            "loan_id": loan_id,
                            "severity": issue.severity,
                            "code": issue.code,
                            "field": issue.field,
                            "message": issue.message,
                            "value": issue.value,

                        }
                        writer.writerow(row)
