from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import date, timedelta
from typing import Optional, List, Literal
import math

from datetime import datetime
from openpyxl import load_workbook
from pathlib import Path
import abc

BORROWER_MAP = {
    "borrower id": "borrower_id",
    "birth year": "birth_year",
    "gender": "gender",
    "marital status": "marital_status",
    "children": "children",
    "residential status": "residential_status",
    "education": "education",
    "occupation": "occupation",
    "months at current employer": "months_at_current_employer",
    "employment status": "employment_status",
    "years working total": "years_working_total",
    "borrower income": "borrower_income",
    "borrower liabilities": "borrower_liabilities",
    "spouse income": "spouse_income",
    "spouse liabilities": "spouse_liabilities",
    "family income": "family_income",
    "family liabilities": "family_liabilities",
    "dti": "dti",
}

LOAN_MAP = {
    "loan id": "loan_id",
    "credit score": "credit_score",
    "loan amount": "loan_amount",
    "disbursal date": "disbursal_date",
    "interest rate": "interest_rate",
    "loan term": "loan_term",
    "borrower type": "borrower_type",
    "loan type": "loan_type",
    "expected repayment date": "expected_repayment_date",
    "loan status": "loan_status",
    "purpose": "purpose",
}

REPAYMENT_MAP = {
    "monthly payment": "monthly_payment",
    "outstanding principal": "outstanding_principal",
    "repaid principal": "repaid_principal",
    "outstanding interest": "outstanding_interest",
    "repaid interest": "repaid_interest",
    "repayment date": "repayment_date",
    "last debt payment date": "last_debt_payment_date",
    "arrears": "arrears",
    "delay interest": "delay_interest",
    "days late": "days_late",
    "payments": "payments",
}

COMPANY_MAP = {
    "city": "city",
    "activity": "activity",
    "sector": "sector",
    "product": "product",
    "number of employees": "number_of_employees",
    "annual revenue": "annual_revenue",
    "annual profit": "annual_profit",
    "company type": "company_type",
    "company age (years)": "company_age_years",
    "company description": "company_description",
    "shareholders equity": "shareholders_equity",
}

COLLATERAL_MAP = {
    "appraisal date": "appraisal_date",
    "appraisal provider": "appraisal_provider",
    "collateral description": "collateral_description",
    "collateral market value": "collateral_market_value",
    "collateral name": "collateral_name",
    "collateral owner": "collateral_owner",
    "guarantor title": "guarantor_title",
}


Severity = Literal["ERROR", "WARN", "INFO"]

@dataclass
class Issue:
    code: str
    severity: Severity
    field: Optional[str]
    message: str
    value: Optional[object] = None
    suggestion: Optional[str] = None

@dataclass
class LoanRecord:
    borrower: BorrowerInfo
    loan: LoanInfo
    repayment: RepaymentInfo
    company: Optional[CompanyInfo] = None
    collateral: Optional[CollateralInfo] = None
    issues: List[Issue] = field(default_factory=list, init=False)

@dataclass
class BorrowerInfo:
    borrower_id: int
    birth_year: Optional[int] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    children: Optional[int] = None
    residential_status: Optional[str] = None
    education: Optional[str] = None
    occupation: Optional[str] = None
    months_at_current_employer: Optional[int] = None
    employment_status: Optional[str] = None
    years_working_total: Optional[int] = None
    borrower_income: Optional[float] = None
    borrower_liabilities: Optional[float] = None
    spouse_income: Optional[float] = None
    spouse_liabilities: Optional[float] = None
    family_income: Optional[float] = None
    family_liabilities: Optional[float] = None
    dti: Optional[float] = None

@dataclass
class LoanInfo:
    loan_id: int
    credit_score: Optional[str] = None
    loan_amount: Optional[float] = None
    disbursal_date: Optional[date] = None
    interest_rate: Optional[float] = None
    loan_term: Optional[int] = None
    borrower_type: Optional[str] = None
    loan_type: Optional[str] = None
    expected_repayment_date: Optional[date] = None
    loan_status: Optional[str] = None
    purpose: Optional[str] = None

@dataclass
class RepaymentInfo:
    monthly_payment: Optional[float] = None
    outstanding_principal: Optional[float] = None
    repaid_principal: Optional[float] = None
    outstanding_interest: Optional[float] = None
    repaid_interest: Optional[float] = None
    repayment_date: Optional[date] = None
    last_debt_payment_date: Optional[date] = None
    arrears: Optional[float] = None
    delay_interest: Optional[float] = None
    days_late: Optional[int] = None
    payments: Optional[Dict[str, Any]] = None

@dataclass
class CompanyInfo:
    city: Optional[str] = None
    activity: Optional[str] = None
    sector: Optional[str] = None
    product: Optional[str] = None
    number_of_employees: Optional[int] = None
    annual_revenue: Optional[float] = None
    annual_profit: Optional[float] = None
    company_type: Optional[str] = None
    company_age_years: Optional[int] = None
    company_description: Optional[str] = None
    shareholders_equity: Optional[float] = None

@dataclass
class CollateralInfo:
    appraisal_date: Optional[date] = None
    appraisal_provider: Optional[str] = None
    collateral_description: Optional[str] = None
    collateral_market_value: Optional[float] = None
    collateral_name: Optional[str] = None
    collateral_owner: Optional[str] = None
    guarantor_title: Optional[str] = None




class LoanParser(abc.ABC):
    @abc.abstractmethod
    def parse_for(self, file_names: Iterable[str], for_date: datetime) -> List[LoanRecord]:
        ...

class XLSXLoanParser(LoanParser):

    def __init__(self, dry_run: bool = False):
        self.__dry_run = dry_run

    def parse_for(self, file_path: Path) -> List[LoanRecord]:
        loan_file = load_workbook(file_path, data_only=True, read_only=True).active
        header_cells = next(loan_file.iter_rows(min_row=1, max_row=1))
        headers = [_norm(str(c.value)) if c.value is not None else "" for c in header_cells]
        enumerated_headers = {i: h for i, h in enumerate(headers) if h}

        records: list[LoanRecord] = []

        for row in loan_file.iter_rows(min_row=2, values_only=True):
            row_dict = {enumerated_headers[i]: row[i] for i in enumerated_headers.keys()}

            borrower_kwargs = self.__extract(BORROWER_MAP, row_dict)
            loan_kwargs = self.__extract(LOAN_MAP, row_dict)
            repay_kwargs = self.__extract(REPAYMENT_MAP, row_dict)
            company_kwargs = self.__extract(COMPANY_MAP, row_dict)
            coll_kwargs = self.__extract(COLLATERAL_MAP, row_dict)

            borrower_id = borrower_kwargs.get("borrower_id")
            loan_id = loan_kwargs.get("loan_id")
            if not borrower_id or not loan_id:
                continue

            record = LoanRecord(
                borrower=BorrowerInfo(**borrower_kwargs),
                loan=LoanInfo(**loan_kwargs),
                repayment=RepaymentInfo(**repay_kwargs),
                company=CompanyInfo(**company_kwargs) if any(v is not None for v in company_kwargs.values()) else None,
                collateral=CollateralInfo(**coll_kwargs) if any(v is not None for v in coll_kwargs.values()) else None,
            )
            records.append(record)

        return records

    def __extract(self, fields_map: Dict[str, str], row: Dict[str, Any]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for col_label, field in fields_map.items():
            val = row.get(col_label)
            # tip dönüşümleri:
            if field.endswith("_date"):
                out[field] = _to_date(val)
            elif field in {"loan_amount", "monthly_payment", "outstanding_principal", "repaid_principal",
                           "outstanding_interest", "repaid_interest", "arrears", "delay_interest",
                           "annual_revenue", "annual_profit", "shareholders_equity",
                           "borrower_income", "borrower_liabilities", "spouse_income",
                           "spouse_liabilities", "family_income", "family_liabilities",
                           "collateral_market_value", "dti"}:
                out[field] = _to_float(val)
            elif field in {"credit_score", "loan_term", "days_late", "payments",
                           "children", "months_at_current_employer",
                           "years_working_total", "number_of_employees",
                           "company_age_years", "birth_year"}:
                out[field] = _to_int(val)
            else:
                out[field] = None if val in (None, "") else val
        return out











def _norm(s: str) -> str:
    return s.strip().lower()

def _to_float(x):
    if x in (None, ""): return None
    try:
        if isinstance(x, str): x = x.replace(" ", "").replace(",", ".")
        return float(x)
    except Exception:
        return None

def _to_int(x):
    if x in (None, ""): return None
    try:
        if isinstance(x, float) and x.is_integer(): return int(x)
        return int(str(x).strip())
    except Exception:
        return None

def _to_date(x):
    # openpyxl already returns datetime/date for Excel date cells (data_only=True)
    if x in (None, ""): return None
    if isinstance(x, date): return x
    if isinstance(x, datetime): return x.date()
    # Fallback simple string parse
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(str(x).strip(), fmt).date()
        except ValueError:
            continue
    return None

def load_loan_records_from_excel(path: str, sheet_name: str | None = None) -> list[LoanRecord]:
    wb = load_workbook(path, data_only=True, read_only=True)
    ws = wb[sheet_name] if sheet_name else wb.active

    # Header row
    header_cells = next(ws.iter_rows(min_row=1, max_row=1))
    headers = [_norm(str(c.value)) if c.value is not None else "" for c in header_cells]
    idx2header = {i: h for i, h in enumerate(headers) if h}

    records: list[LoanRecord] = []

    for row in ws.iter_rows(min_row=2, values_only=True):
        row_dict = {idx2header[i]: row[i] for i in idx2header.keys()}

        # Support typo: "collaretal description"
        if "collateral description" not in row_dict and "collaretal description" in row_dict:
            row_dict["collateral description"] = row_dict["collaretal description"]

        # Required IDs
        borrower_id = row_dict.get("borrower id")
        loan_id = row_dict.get("loan id")
        if not borrower_id or not loan_id:
            continue

        borrower = BorrowerInfo(
            borrower_id=int(borrower_id),
            birth_year=_to_int(row_dict.get("birth year")),
            gender=row_dict.get("gender"),
            marital_status=row_dict.get("marital status"),
            children=_to_int(row_dict.get("children")),
            residential_status=row_dict.get("residential status"),
            education=row_dict.get("education"),
            occupation=row_dict.get("occupation"),
            months_at_current_employer=_to_int(row_dict.get("months at current employer")),
            employment_status=row_dict.get("employment status"),
            years_working_total=_to_int(row_dict.get("years working total")),
            borrower_income=_to_float(row_dict.get("borrower income")),
            borrower_liabilities=_to_float(row_dict.get("borrower liabilities")),
            spouse_income=_to_float(row_dict.get("spouse income")),
            spouse_liabilities=_to_float(row_dict.get("spouse liabilities")),
            family_income=_to_float(row_dict.get("family income")),
            family_liabilities=_to_float(row_dict.get("family liabilities")),
            dti=_to_float(row_dict.get("dti")),
        )

        loan = LoanInfo(
            loan_id=int(loan_id),
            credit_score=_to_int(row_dict.get("credit score")),
            loan_amount=_to_float(row_dict.get("loan amount")),
            disbursal_date=_to_date(row_dict.get("disbursal date")),
            interest_rate=_to_float(row_dict.get("interest rate")),
            loan_term=_to_int(row_dict.get("loan term")),
            borrower_type=row_dict.get("borrower type"),
            loan_type=row_dict.get("loan type"),
            expected_repayment_date=_to_date(row_dict.get("expected repayment date")),
            loan_status=row_dict.get("loan status"),
            purpose=row_dict.get("purpose"),
        )

        repayment = RepaymentInfo(
            monthly_payment=_to_float(row_dict.get("monthly payment")),
            outstanding_principal=_to_float(row_dict.get("outstanding principal")),
            repaid_principal=_to_float(row_dict.get("repaid principal")),
            outstanding_interest=_to_float(row_dict.get("outstanding interest")),
            repaid_interest=_to_float(row_dict.get("repaid interest")),
            repayment_date=_to_date(row_dict.get("repayment date")),
            last_debt_payment_date=_to_date(row_dict.get("last debt payment date")),
            arrears=_to_float(row_dict.get("arrears")),
            delay_interest=_to_float(row_dict.get("delay interest")),
            days_late=_to_int(row_dict.get("days late")),
            payments=_to_int(row_dict.get("payments")),
        )

        company = CompanyInfo(
            city=row_dict.get("city"),
            activity=row_dict.get("activity"),
            sector=row_dict.get("sector"),
            product=row_dict.get("product"),
            number_of_employees=_to_int(row_dict.get("number of employees")),
            annual_revenue=_to_float(row_dict.get("annual revenue")),
            annual_profit=_to_float(row_dict.get("annual profit")),
            company_type=row_dict.get("company type"),
            company_age_years=_to_int(row_dict.get("company age (years)")),
            company_description=row_dict.get("company description"),
            shareholders_equity=_to_float(row_dict.get("shareholders equity")),
        )

        collateral = CollateralInfo(
            appraisal_date=_to_date(row_dict.get("appraisal date")),
            appraisal_provider=row_dict.get("appraisal provider"),
            collateral_description=row_dict.get("collateral description"),
            collateral_market_value=_to_float(row_dict.get("collateral market value")),
            collateral_name=row_dict.get("collateral name"),
            collateral_owner=row_dict.get("collateral owner"),
            guarantor_title=row_dict.get("guarantor title"),
        )

        record = LoanRecord(
            borrower=borrower,
            loan=loan,
            repayment=repayment,
            company=company,
            collateral=collateral
        )
        records.append(record)

    return records