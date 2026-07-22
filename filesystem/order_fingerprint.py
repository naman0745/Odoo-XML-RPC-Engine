"""
order_fingerprint.py
--------------------
Generates a deterministic, content-based fingerprint for a parsed
Purchase Order.

The fingerprint is computed from normalized business data returned by
``ExcelProcessor.get_mapped_rows()``.  It is intentionally blind to:
  - Excel formatting and metadata
  - Workbook filename
  - Row order within the file
  - Explicitly excluded fields (price, UOM)

Any business field added to the parser's column mapping will
automatically participate in the fingerprint — no logic change needed —
unless it appears in ``FINGERPRINT_EXCLUDED_FIELDS``.

Usage
-----
    from filesystem.order_fingerprint import generate_fingerprint

    rows        = processor.get_mapped_rows()
    fingerprint = generate_fingerprint(rows)       # 64-char hex string
"""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Current algorithm version.  Increment this whenever the normalization
# logic changes so that stale manifest entries can be identified.
FINGERPRINT_VERSION: int = 1

# Internal field names that are NEVER included in the fingerprint.
# All other fields returned by the parser participate automatically.
FINGERPRINT_EXCLUDED_FIELDS: frozenset[str] = frozenset(
    {
        # Business exclusions (by spec)
        "price_unit",
        "uom",
        # Internal bookkeeping keys injected by ExcelProcessor
        "_row",
    }
)

# The field whose value becomes the PO-level header key (used to
# extract the vendor name for canonical string construction).
_VENDOR_FIELD = "vendor"

# Fields that are line-specific identifiers (used for sort key).
_LINE_SORT_FIELDS = ("x_vendor_code", "attribute_value_ids")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_fingerprint(rows: list[dict]) -> str:
    """
    Generate a deterministic SHA-256 fingerprint from normalized PO data.

    Parameters
    ----------
    rows : list[dict]
        Mapped rows as returned by ``ExcelProcessor.get_mapped_rows()``.
        Must contain at least one row.

    Returns
    -------
    str
        64-character lowercase hex digest.

    Raises
    ------
    ValueError
        If ``rows`` is empty.
    """
    if not rows:
        raise ValueError("Cannot generate fingerprint: rows list is empty.")

    canonical = _build_canonical_string(rows)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _build_canonical_string(rows: list[dict]) -> str:
    """
    Assemble the deterministic string that is fed into SHA-256.

    Structure::

        header:<field>=<value>|<field>=<value>|...
        lines:[{"field":"value",...},{"field":"value",...},...]

    Header fields are taken from the first row (PO-level data shared
    across all rows).  Line fields use every non-excluded, non-header
    field from each row, sorted for determinism.
    """
    # 1. Collect all business field keys present anywhere across all rows,
    #    excluding known non-business / excluded keys.
    all_keys: set[str] = set()
    for row in rows:
        all_keys.update(row.keys())
    all_keys -= FINGERPRINT_EXCLUDED_FIELDS

    # 2. Separate header (PO-level) keys from line-item keys.
    #    Currently "vendor" is the only true header field; any future
    #    header-level fields added to the mapping (e.g. "ship_via",
    #    "payment_terms") must also be present in every row and will be
    #    automatically included here.
    header_keys = sorted(k for k in all_keys if _is_header_field(k))
    line_keys   = sorted(k for k in all_keys if not _is_header_field(k))

    # 3. Build header segment from the first row.
    first_row = rows[0]
    header_parts = []
    for key in header_keys:
        value = _normalize(key, first_row.get(key))
        if value:          # ignore empty / None header fields
            header_parts.append(f"{key}={value}")
    header_segment = "|".join(header_parts)

    # 4. Build per-line segment, excluding header fields.
    normalized_lines: list[dict] = []
    for row in rows:
        line: dict[str, str] = {}
        for key in line_keys:
            value = _normalize(key, row.get(key))
            if value:      # ignore empty / None line fields
                line[key] = value
        if line:           # skip completely empty lines
            normalized_lines.append(line)

    # 5. Sort lines for row-order independence.
    normalized_lines.sort(key=_sort_key)

    lines_segment = json.dumps(normalized_lines, separators=(",", ":"), sort_keys=True)

    return f"header:{header_segment}|lines:{lines_segment}"


def _is_header_field(key: str) -> bool:
    """
    Return True for PO-level (header) fields — those shared by every row.

    Currently only ``vendor`` qualifies.  Future header fields should be
    added to this predicate or to a dedicated constant.
    """
    _HEADER_FIELDS: frozenset[str] = frozenset(
        {
            "vendor",
            # Future additions: "ship_via", "payment_terms", "country",
            # "sample_date", "ex_date"
        }
    )
    return key in _HEADER_FIELDS


def _normalize(field: str, value: object) -> str:
    """
    Normalize a single field value to a canonical string.

    Rules
    -----
    - ``None`` or blank → ``""`` (excluded by callers)
    - Dates (``date`` / ``datetime`` / ISO strings) → ``"YYYY-MM-DD"``
    - Quantities / numerics → ``str(float(value))``  (``"10"`` == ``"10.0"`` ❌ → ``"10.0"`` ✅)
    - Text → stripped and lowercased
    """
    if value is None:
        return ""

    # -- Date normalization ------------------------------------------------
    if isinstance(value, (date, datetime)):
        return value.strftime("%Y-%m-%d")

    str_value = str(value).strip()

    if not str_value:
        return ""

    # Try to parse date strings
    if _is_date_field(field):
        parsed = _try_parse_date(str_value)
        if parsed:
            return parsed

    # -- Numeric normalization --------------------------------------------
    if _is_numeric_field(field):
        try:
            return str(float(str_value))
        except (ValueError, TypeError):
            pass

    # -- Default: strip + lowercase ---------------------------------------
    return str_value.strip().lower()


def _is_date_field(field: str) -> bool:
    _DATE_FIELDS: frozenset[str] = frozenset({"date_planned"})
    return field in _DATE_FIELDS


def _is_numeric_field(field: str) -> bool:
    _NUMERIC_FIELDS: frozenset[str] = frozenset({"product_qty"})
    return field in _NUMERIC_FIELDS


def _try_parse_date(value: str) -> str:
    """Attempt to parse common date formats; return ISO string or ''."""
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""


def _sort_key(line: dict) -> tuple[str, ...]:
    """Stable sort key for line items: (vendor_code, color, ...)."""
    return tuple(line.get(f, "") for f in _LINE_SORT_FIELDS)
