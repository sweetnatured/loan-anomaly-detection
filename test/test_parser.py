def test_validate(parsed_loans) -> None:
    validated_issues = []
    for parsed_loan in parsed_loans:
        validated_issues.append(parsed_loan.validate())

    assert len(validated_issues) == 72

    error_counter = 0
    for issues_per_loan in validated_issues:
        for loan_id, issues in issues_per_loan.items():
            if issues:
                error_counter = error_counter + 1

    assert error_counter == 22
