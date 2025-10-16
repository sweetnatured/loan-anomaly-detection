import csv
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from anomaly_detector.main import app

runner = CliRunner()

loan_file = Path(__file__).absolute().parent / "data" / "loans.xlsx"

def test_main_cli() -> None:

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", prefix="loan_anomalies_output") as tmp_file_io:

        test_options = [
            "--file-path", str(loan_file),
            "--output-path", tmp_file_io.name,
        ]

        result = runner.invoke(app, test_options)  # type: ignore

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

            assert line_count == 483

            assert issues[0]['code'] == 'DEFAULT'
            assert issues[0]['field'] == 'payments'
            assert issues[0]['loan_id'] == '37216892'
            assert issues[0]['message'] == 'Payment expired 112 days'
            assert issues[0]['severity'] == 'ERROR'
            assert issues[0]['value'] == 'payment date: 2023-09-20 00:00:00 -- repayment date:2023-05-31 00:00:00'

            assert issues[447]['code'] == 'NON_COMPLETE_PAYMENTS'
            assert issues[447]['field'] == 'payments'
            assert issues[447]['loan_id'] == '56721442'
            assert issues[447]['message'] == 'Payments column is not consistent'
            assert issues[447]['severity'] == 'ERROR'
            assert issues[447]['value'] == ''

            assert issues[449]['code'] == 'INVALID_DATE'
            assert issues[449]['field'] == 'appraisal_date'
            assert issues[449]['loan_id'] == '97987259'
            assert issues[449]['message'] == 'Date is not valid formatted'
            assert issues[449]['severity'] == 'ERROR'
            assert issues[449]['value'] == ''

            assert issues[230]['code'] == ''
            assert issues[230]['field'] == ''
            assert issues[230]['loan_id'] == '13752758'
            assert issues[230]['message'] == ''
            assert issues[230]['severity'] == 'CLEAN'
            assert issues[230]['value'] == ''

        assert result.exit_code == 0
        assert "Process finished." in result.output
