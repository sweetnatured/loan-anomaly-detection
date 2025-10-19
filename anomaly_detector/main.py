import logging
import sys
import time
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

    logging.info(f"Anomaly detection has been started for the file: {file_path}")

    start_time = time.perf_counter()
    loan_parser = XLSXLoanParser()

    parsed_loans = loan_parser.parse_for(Path(file_path))
    validated_issues = (parsed_loan.validate(xirr_sensitivity) for parsed_loan in parsed_loans)
    anomaly_reporter(validated_issues, Path(output_path), dry_run)

    elapsed = time.perf_counter() - start_time
    typer.echo(f"Process finished in {elapsed:.2f} seconds.")


if __name__ == "__main__":
    typer.run(main)
