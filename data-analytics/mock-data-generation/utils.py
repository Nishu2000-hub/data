"""
Shared helpers for Saayam mock data generation (Issue #301).

Kept dependency-free on purpose: only the Python standard library is used,
so the generator runs anywhere without a pip install step.
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


# ─────────────────────────────────────────────────────────
# Time helpers
# ─────────────────────────────────────────────────────────

START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2026, 8, 31)

TS_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"


def random_timestamp(start=None, end=None):
    """Return a PostgreSQL-compatible timestamp string between start and end."""
    start = start or START_DATE
    end = end or END_DATE
    if start >= end:
        return start.strftime(TS_FORMAT)
    span = int((end - start).total_seconds())
    return (start + timedelta(seconds=random.randint(0, span))).strftime(TS_FORMAT)


def timestamp_pair(start=None, end=None, max_gap_days=180):
    """
    Return (created_at, last_updated_at) where last_updated_at >= created_at.

    Used wherever the schema has both columns, to satisfy the issue's
    "created_at <= last_updated_at" consistency requirement.
    """
    created_str = random_timestamp(start, end)
    created = datetime.strptime(created_str, TS_FORMAT)
    ceiling = min(created + timedelta(days=max_gap_days), END_DATE)
    updated_str = random_timestamp(created, ceiling)
    return created_str, updated_str


def random_date(min_year=1950, max_year=2006):
    """Return a DATE string — used for users.dob."""
    year = random.randint(min_year, max_year)
    month = random.randint(1, 12)
    day = random.randint(1, 28)  # 28 keeps every month valid
    return datetime(year, month, day).strftime(DATE_FORMAT)


# ─────────────────────────────────────────────────────────
# ID generators — formats mirror the DB sequence triggers
# ─────────────────────────────────────────────────────────

def make_user_id(seq):
    """
    Mirror virginia_dev_saayam_rdbms.generate_sid().
    Sequence is left-padded to 15 digits and split into five groups of three:
        SID-00-000-000-000-000-001
    """
    padded = str(seq).zfill(15)
    groups = [padded[i:i + 3] for i in range(0, 15, 3)]
    return "SID-00-" + "-".join(groups)


def make_org_id(seq):
    """
    Mirror virginia_dev_saayam_rdbms.generate_org_id().
    Sequence is left-padded to 13 digits, split 3-3-3-4:
        ORG-000-000-000-0001
    """
    padded = str(seq).zfill(13)
    return f"ORG-{padded[0:3]}-{padded[3:6]}-{padded[6:9]}-{padded[9:13]}"


# ─────────────────────────────────────────────────────────
# Geography helpers
# ─────────────────────────────────────────────────────────

def jitter_point(lat, lon, max_km=25.0):
    """
    Offset a coordinate by a small random amount so generated points sit
    plausibly *near* a city centroid rather than exactly on it.

    ~111 km per degree of latitude; longitude is not corrected for latitude
    because the offsets are small enough that the difference is immaterial
    for mock data.
    """
    deg = max_km / 111.0
    return (
        round(lat + random.uniform(-deg, deg), 6),
        round(lon + random.uniform(-deg, deg), 6),
    )


def to_ewkt(lat, lon):
    """
    Format a point for a geography(Point, 4326) column.

    EWKT with an explicit SRID loads cleanly via \\copy into PostGIS
    geography columns. Note the axis order: POINT(longitude latitude).
    """
    return f"SRID=4326;POINT({lon} {lat})"


def to_pg_point(lat, lon):
    """Format for the native PostgreSQL `point` type (users.last_location)."""
    return f"({lat},{lon})"


# ─────────────────────────────────────────────────────────
# Output
# ─────────────────────────────────────────────────────────

def write_csv(rows, filename, outdir, columns):
    """
    Write rows to CSV with an explicit column order.

    Column order is passed in rather than inferred from the dicts so the
    header always matches the DDL order for that table.
    """
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / filename
    with open(path, "w", newline="", encoding="utf-8") as fh:
        # lineterminator="\n" keeps the files LF-only. The csv module
        # defaults to CRLF, which shows up as noise in git diffs on Linux
        # and macOS checkouts.
        writer = csv.DictWriter(fh, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return path


def pct(n, weights):
    """Pick one of `n` options using `weights` — thin wrapper for readability."""
    return random.choices(n, weights=weights, k=1)[0]
