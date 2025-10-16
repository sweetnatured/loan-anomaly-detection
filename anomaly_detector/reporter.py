import csv
from pathlib import Path
from typing import List, Dict

from anomaly_detector.parser import Issue


def anomaly_reporter(validated_issues: List[Dict[int, Issue]], output_path: Path):

    with open("loan_anomalies.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["loan_id", "severity", "field", "message", "value"])
        writer.writeheader()
        for issues_per_loan in validated_issues:
            for loan_id, issues in issues_per_loan.items():
                if issues:
                    for issue in issues:
                        writer.writerow({
                            "loan_id": loan_id,
                            "severity": issue.severity,
                            "field": issue.field,
                            "message": issue.message,
                            "value": issue.value,

                        })
                else:
                    writer.writerow({
                        "loan_id": loan_id,
                        "severity": 'CLEAN',
                        "field": '',
                        "message": '',
                        "value": '',
                    })