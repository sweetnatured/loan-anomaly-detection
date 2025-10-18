def test_validate(parsed_loans) -> None:
    validated_issues = []
    xirr_sensitivity = 0.07
    for parsed_loan in parsed_loans:
        validated_issues.append(parsed_loan.validate(xirr_sensitivity))

    assert len(validated_issues) == 72

    error_counter = 0
    for issues_per_loan in validated_issues:
        for loan_id, issues in issues_per_loan.items():
            if len(issues) > 1 or issues[0].severity != 'CLEAN' :
                error_counter = error_counter + 1

    assert error_counter == 41
