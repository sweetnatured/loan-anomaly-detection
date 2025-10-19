from pathlib import Path
from typing import Iterator

import pytest

from anomaly_detector.parser import LoanRecord, XLSXLoanParser

loan_file = Path(__file__).absolute().parent / "data" / "loans.xlsx"


@pytest.fixture()
def parsed_loans() -> Iterator[LoanRecord]:
    loan_parser = XLSXLoanParser()
    parsed_loans = loan_parser.parse_for(loan_file)
    return parsed_loans
