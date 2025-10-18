import logging
import sys
from types import TracebackType
from typing import Type, Optional, Any
from pathlib import Path

from anomaly_detector.reporter import anomaly_reporter
from anomaly_detector.parser import XLSXLoanParser
import typer

app = typer.Typer(help="loan-anomaly-detector")


def configure_logging(fmt: str, level: str) -> None:
    logging.basicConfig(format=fmt, level=level)
    orig_excepthook = sys.excepthook

    def log_uncaught_exception(exc_type: Type[BaseException], exc_value: BaseException,
                               exc_traceback: Optional[TracebackType]) -> Any:
        logging.fatal("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
        if orig_excepthook is not None:
            orig_excepthook(exc_type, exc_value, exc_traceback)

    sys.excepthook = log_uncaught_exception


@app.command()
def main(
        file_path: str = typer.Option(default=False, envvar="FILE_PATH"),
        output_path: str = typer.Option(default=False, envvar="OUTPUT_PATH"),
        xirr_sensitivity: float = typer.Option(default=0.07, envvar="XIRR_SENSITIVITY"),
        dry_run: bool = typer.Option(default=False, envvar="DRY_RUN"),
        logging_format: str = typer.Option(
            default='[%(asctime)s] [%(threadName)s] %(levelname)s %(name)s - %(message)s',
            envvar='LOGGING_FORMAT'
        ),
        logging_level: str = typer.Option(default='INFO', envvar='LOGGING_LEVEL')
) -> None:
    configure_logging(logging_format, logging_level)

    loan_parser = XLSXLoanParser()
    parsed_loans = loan_parser.parse_for(Path(file_path))
    validated_issues = []
    for parsed_loan in parsed_loans:
        validated_issues.append(parsed_loan.validate(xirr_sensitivity))

    anomaly_reporter(validated_issues, Path(output_path), dry_run)

    typer.echo("Process finished.")


if __name__ == "__main__":
    typer.run(main)
