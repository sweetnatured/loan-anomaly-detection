import csv
import tempfile
from pathlib import Path
from typing import List, Dict

from anomaly_detector.parser import Issue, LoanRecord
from anomaly_detector.reporter import anomaly_reporter

test_output_anomalities = Path(__file__).absolute().parent / "data" / "test_output_anomalities.csv"


def test_reporter(parsed_loans: List[LoanRecord]) -> None:

    validated_issues: List[Dict[int, List[Issue]]] = []
    xirr_sensitivity = 0.07

    for parsed_loan in parsed_loans:
        validated_issues.append(parsed_loan.validate(xirr_sensitivity))

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", prefix="loan_anomalies_output") as tmp_file_io:
        anomaly_reporter(validated_issues, Path(tmp_file_io.name))

        with open(tmp_file_io.name, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            line_count = 0
            issues = []
            for row in csv_reader:
                if line_count == 0:
                    assert 'loan_id, severity, code, field, message, value' == ", ".join(row)
                    line_count += 1

                issues.append(row)
                line_count += 1

            assert line_count == 491

            assert issues[0]['code'] == 'DEFAULT'
            assert issues[0]['field'] == 'payments'
            assert issues[0]['loan_id'] == '37216892'
            assert issues[0]['message'] == 'Payment expired 112 days'
            assert issues[0]['severity'] == 'ERROR'
            assert issues[0]['value'] == 'payment date: 2023-09-20 00:00:00 -- repayment date:2023-05-31 00:00:00'

            assert issues[447]['code'] == 'XIRRDeviation'
            assert issues[447]['field'] == 'payments'
            assert issues[447]['loan_id'] == '14146974'
            assert issues[447]['message'] == 'Interest rate: 0.25 , XIRR: 3.999179878517634e-16, difference: 0.2499999999999996 '
            assert issues[447]['severity'] == 'ERROR'
            assert issues[447]['value'] == ''

            assert issues[457]['code'] == 'INVALID_DATE'
            assert issues[457]['field'] == 'appraisal_date'
            assert issues[457]['loan_id'] == '97987259'
            assert issues[457]['message'] == 'Date is not valid formatted'
            assert issues[457]['severity'] == 'ERROR'
            assert issues[457]['value'] == ''

            assert issues[449]['code'] == ''
            assert issues[449]['field'] == ''
            assert issues[449]['loan_id'] == '94976997'
            assert issues[449]['message'] == ''
            assert issues[449]['severity'] == 'CLEAN'
            assert issues[449]['value'] == ''
