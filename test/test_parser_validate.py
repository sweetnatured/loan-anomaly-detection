from typing import Iterator

from anomaly_detector.parser import LoanRecord


def test_validate(parsed_loans: Iterator[LoanRecord]) -> None:
    xirr_sensitivity = 0.07
    validated_issues_generator = (parsed_loan.validate(xirr_sensitivity) for parsed_loan in parsed_loans)

    validated_issues = list(validated_issues_generator)
    assert len(list(validated_issues)) == 72

    error_counter = 0
    for issues_per_loan in validated_issues:
        for loan_id, issues in issues_per_loan.items():
            if len(issues) > 1 or issues[0].severity != 'CLEAN':
                error_counter = error_counter + 1

    assert error_counter == 41
