"""Natural language expectations for DataFrame validation.

This module exposes :func:`expect_df`, a lightweight validator that turns
human-friendly Analysta style phrases into column expectations and row rules.
The parser aims to be permissive while still producing structured results that
describe which expectations passed or failed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Callable, Iterable

import numpy as np
import pandas as pd


@dataclass
class ColumnExpectation:
    """Column-level expectation derived from natural language.

    Parameters
    ----------
    name:
        Column name.
    unique:
        Whether the column should contain unique values.
    dtype:
        Expected data type category (``"integer"``, ``"float"``, ``"string"``,
        or ``"datetime"``).
    fmt:
        Expected ``strftime`` format for datetime/text parsing.
    allowed_values:
        Optional allowed set of values.
    regex:
        Optional regular expression pattern that values must match.
    allow_nulls:
        Whether nulls are allowed. ``None`` means no explicit expectation.
    """

    name: str
    unique: bool = False
    dtype: str | None = None
    fmt: str | None = None
    allowed_values: set[str] | None = None
    regex: str | None = None
    allow_nulls: bool | None = None


@dataclass
class ColumnResult:
    column: str
    passed: bool
    diagnostics: list[str] = field(default_factory=list)


@dataclass
class RowRule:
    description: str
    expression: str


@dataclass
class RowRuleResult:
    description: str
    passed: bool
    failing_indices: list[int] = field(default_factory=list)
    message: str | None = None


@dataclass
class ExpectationReport:
    passed: bool
    column_results: list[ColumnResult] = field(default_factory=list)
    row_results: list[RowRuleResult] = field(default_factory=list)
    custom_results: list[RowRuleResult] = field(default_factory=list)

    def to_human_readable(self) -> str:
        """Return a readable, multi-line report of the validation results."""

        status = "PASSED" if self.passed else "FAILED"
        lines = [f"Expectation report: {status}"]

        if self.column_results:
            lines.append("Columns:")
            for result in self.column_results:
                result_status = "PASS" if result.passed else "FAIL"
                details = f" -> {' | '.join(result.diagnostics)}" if result.diagnostics else ""
                lines.append(f"- {result.column}: {result_status}{details}")

        if self.row_results:
            lines.append("Row rules:")
            for result in self.row_results:
                result_status = "PASS" if result.passed else "FAIL"
                details = f" -> {result.message}" if result.message else ""
                lines.append(f"- {result.description}: {result_status}{details}")

        if self.custom_results:
            lines.append("Custom validators:")
            for result in self.custom_results:
                result_status = "PASS" if result.passed else "FAIL"
                details = f" -> {result.message}" if result.message else ""
                lines.append(f"- {result.description}: {result_status}{details}")

        return "\n".join(lines)

    def __str__(self) -> str:  # pragma: no cover - alias for readability
        return self.to_human_readable()


def expect_df(
    df: pd.DataFrame,
    expectations: str | Iterable[str],
    /,
    *,
    row_rules: Iterable[str] | None = None,
    validators: Iterable[RowRuleResult | tuple[str, Callable[[pd.DataFrame], object]] | Callable[[pd.DataFrame], object]]
    | None = None,
) -> ExpectationReport:
    """Validate a DataFrame against Analysta-style expectations.

    Examples
    --------
    >>> import pandas as pd
    >>> data = pd.DataFrame({"id": [1, 1], "status": ["ok", "bad"]})
    >>> report = expect_df(
    ...     data,
    ...     [
    ...         "expect column id to be unique and not null",
    ...         "column status: allowed values {ok, pending}",
    ...     ],
    ... )
    >>> report.passed
    False
    """

    column_expectations, parsed_row_rules = _parse_expectations(expectations)
    if row_rules:
        parsed_row_rules.extend(_parse_row_rules(row_rules))

    custom_results: list[RowRuleResult] = []
    if validators:
        for validator in validators:
            custom_results.append(_run_validator(df, validator))

    column_results: list[ColumnResult] = []
    for expectation in column_expectations:
        column_results.append(_validate_column(df, expectation))

    row_results: list[RowRuleResult] = []
    for rule in parsed_row_rules:
        row_results.append(_validate_row_rule(df, rule))

    passed = all(result.passed for result in column_results + row_results + custom_results)
    return ExpectationReport(
        passed=passed,
        column_results=column_results,
        row_results=row_results,
        custom_results=custom_results,
    )


def _parse_expectations(
    expectations: str | Iterable[str],
) -> tuple[list[ColumnExpectation], list[RowRule]]:
    if isinstance(expectations, str):
        lines = [line.strip() for line in expectations.splitlines() if line.strip()]
    else:
        lines = [str(item).strip() for item in expectations if str(item).strip()]

    column_expectations: list[ColumnExpectation] = []
    row_rules: list[RowRule] = []

    for line in lines:
        lowered = line.lower()
        if lowered.startswith(("rows must", "every row must", "expect rows")):
            row_rules.extend(_parse_row_rules([line]))
            continue

        column_match = re.search(
            r"(?:expect\s+)?column\s+(?P<name>[\w .-]+?)(?:\s*(?:to|:)?\s+)(?P<body>.+)",
            line,
            flags=re.IGNORECASE,
        )
        if column_match:
            name = column_match.group("name").strip()
            body = column_match.group("body").strip()
        elif ":" in line:
            name, body = [segment.strip() for segment in line.split(":", maxsplit=1)]
            name = name.replace("column", "", 1).strip()
        else:
            # If we cannot parse the column name, ignore the expectation.
            continue

        expectation = _parse_column_body(name, body)
        column_expectations.append(expectation)

    return column_expectations, row_rules


def _parse_column_body(name: str, body: str) -> ColumnExpectation:
    expectation = ColumnExpectation(name=name)

    allowed_from_full_body = _extract_allowed_values(body)
    if allowed_from_full_body:
        expectation.allowed_values = allowed_from_full_body

    tokens = re.split(r"[,;]|\band\b", body, flags=re.IGNORECASE)
    for raw_token in tokens:
        token = raw_token.strip()
        lowered = token.lower()
        if not token:
            continue
        if "unique" in lowered:
            expectation.unique = True
            continue
        if any(phrase in lowered for phrase in ("not null", "no null", "non-null")):
            expectation.allow_nulls = False
            continue
        if "allow null" in lowered:
            expectation.allow_nulls = True
            continue
        dtype = _extract_dtype(lowered)
        if dtype is not None:
            expectation.dtype = dtype
        fmt = _extract_format(token)
        if fmt is not None:
            expectation.fmt = fmt
        if expectation.allowed_values is None:
            allowed = _extract_allowed_values(token)
            if allowed:
                expectation.allowed_values = allowed
        regex = _extract_regex(token)
        if regex is not None:
            expectation.regex = regex

    return expectation


def _extract_dtype(token: str) -> str | None:
    if any(word in token for word in ("integer", "int")):
        return "integer"
    if any(word in token for word in ("float", "double", "numeric")):
        return "float"
    if any(word in token for word in ("string", "text")):
        return "string"
    if "datetime" in token or "date" in token:
        return "datetime"
    return None


def _extract_format(token: str) -> str | None:
    match = re.search(r"format\s+(.+)", token, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def _extract_allowed_values(token: str) -> set[str] | None:
    match = re.search(r"allowed values?[^\w]*(.+)", token, flags=re.IGNORECASE)
    if not match:
        match = re.search(r"values?\s+in\s+(.+)", token, flags=re.IGNORECASE)
    if not match:
        return None

    values_part = match.group(1).strip()
    values_part = re.split(r";|\band\b", values_part, maxsplit=1, flags=re.IGNORECASE)[0].strip()
    values_part = values_part.strip("{}[]()")
    raw_values = [part.strip() for part in values_part.split("or")]
    values: list[str] = []
    for raw in raw_values:
        if not raw:
            continue
        values.extend([segment.strip().strip("'\"") for segment in raw.split(",") if segment.strip()])

    if values:
        return set(values)
    return None


def _extract_regex(token: str) -> str | None:
    match = re.search(r"regex\s+(.+)", token, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"match(?:es)?\s+(.+)", token, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def _parse_row_rules(rules: Iterable[str]) -> list[RowRule]:
    parsed: list[RowRule] = []
    for rule in rules:
        if not rule:
            continue
        text = rule.strip()
        lowered = text.lower()
        if "satisfy" in lowered:
            expression = text.split("satisfy", maxsplit=1)[1].strip()
        elif "must" in lowered:
            expression = text.split("must", maxsplit=1)[1].strip()
        else:
            expression = text
        parsed.append(RowRule(description=text, expression=expression))
    return parsed


def _validate_column(df: pd.DataFrame, expectation: ColumnExpectation) -> ColumnResult:
    diagnostics: list[str] = []

    if expectation.name not in df.columns:
        diagnostics.append("column missing")
        return ColumnResult(column=expectation.name, passed=False, diagnostics=diagnostics)

    series = df[expectation.name]

    if expectation.allow_nulls is False:
        null_mask = series.isna()
        if null_mask.any():
            indices = list(series.index[null_mask])
            diagnostics.append(f"nulls forbidden; rows {indices}")

    if expectation.unique:
        duplicates = series[series.duplicated(keep=False)]
        if not duplicates.empty:
            duplicate_indices = list(duplicates.index)
            samples = duplicates.head(5).tolist()
            diagnostics.append(
                f"expected unique values; duplicate rows {duplicate_indices}; samples: {samples}"
            )

    if expectation.dtype:
        dtype_diagnostics = _dtype_diagnostics(series, expectation)
        diagnostics.extend(dtype_diagnostics)

    if expectation.allowed_values:
        invalid_mask = series.notna() & ~series.astype(str).isin(expectation.allowed_values)
        if invalid_mask.any():
            invalid = series[invalid_mask]
            diagnostics.append(
                f"unexpected values; rows {list(invalid.index)}; samples: {invalid.astype(str).head(5).tolist()}"
            )

    if expectation.regex:
        pattern = re.compile(expectation.regex)
        str_values = series.dropna().astype(str)
        invalid_mask = ~str_values.map(lambda value: bool(pattern.fullmatch(value)))
        if invalid_mask.any():
            invalid = str_values[invalid_mask]
            diagnostics.append(
                f"regex mismatch /{expectation.regex}/; rows {list(invalid.index)}; samples: {invalid.head(5).tolist()}"
            )

    passed = not diagnostics
    return ColumnResult(column=expectation.name, passed=passed, diagnostics=diagnostics)


def _dtype_diagnostics(series: pd.Series, expectation: ColumnExpectation) -> list[str]:
    diagnostics: list[str] = []
    dtype = expectation.dtype
    if dtype == "integer":
        converted = pd.to_numeric(series, errors="coerce")
        fractional = (converted % 1).fillna(0)
        invalid_mask = series.notna() & (converted.isna() | ~np.isclose(fractional, 0))
    elif dtype == "float":
        converted = pd.to_numeric(series, errors="coerce")
        invalid_mask = series.notna() & converted.isna()
    elif dtype == "string":
        invalid_mask = series.notna() & ~series.map(lambda value: isinstance(value, str))
    elif dtype == "datetime":
        parsed = pd.to_datetime(series, format=expectation.fmt, errors="coerce")
        invalid_mask = series.notna() & parsed.isna()
    else:
        return diagnostics

    if invalid_mask.any():
        invalid = series[invalid_mask]
        details = f"expected {dtype}; rows {list(invalid.index)}; samples: {invalid.astype(str).head(5).tolist()}"
        if dtype == "datetime" and expectation.fmt:
            details += f"; format={expectation.fmt}"
        diagnostics.append(details)
    return diagnostics


def _validate_row_rule(df: pd.DataFrame, rule: RowRule) -> RowRuleResult:
    try:
        evaluated = df.eval(rule.expression)
    except Exception as exc:  # pragma: no cover - rare parse errors
        return RowRuleResult(
            description=rule.description,
            passed=False,
            failing_indices=list(range(len(df))),
            message=f"failed to evaluate expression: {exc}",
        )

    if isinstance(evaluated, pd.Series):
        mask = evaluated.astype(bool)
    else:
        mask = pd.Series(bool(evaluated), index=df.index)

    failing = list(df.index[~mask])
    passed = not failing
    message = None
    if failing:
        message = f"rows failing rule '{rule.expression}': {failing}"
    return RowRuleResult(description=rule.description, passed=passed, failing_indices=failing, message=message)


def _run_validator(
    df: pd.DataFrame, validator: RowRuleResult | tuple[str, Callable[[pd.DataFrame], object]] | Callable[[pd.DataFrame], object]
) -> RowRuleResult:
    if isinstance(validator, RowRuleResult):
        return validator

    if isinstance(validator, tuple):
        description, func = validator
    else:
        func = validator
        description = getattr(func, "__name__", "custom validator")

    outcome = func(df)

    if isinstance(outcome, RowRuleResult):
        return outcome

    message: str | None = None
    verdict = outcome
    if isinstance(outcome, tuple) and len(outcome) == 2:
        verdict, message = outcome

    if isinstance(verdict, pd.Series):
        mask = verdict.astype(bool)
        failing = list(mask.index[~mask])
        passed = not failing
        detail = message or (f"rows failing custom validator '{description}': {failing}" if failing else None)
        return RowRuleResult(description=description, passed=passed, failing_indices=failing, message=detail)

    if isinstance(verdict, (bool, np.bool_)):
        passed = bool(verdict)
        failing = [] if passed else list(range(len(df)))
        detail = message or (None if passed else f"validator '{description}' failed")
        return RowRuleResult(description=description, passed=passed, failing_indices=failing, message=detail)

    raise TypeError("custom validators must return a bool, pandas Series, or RowRuleResult")

