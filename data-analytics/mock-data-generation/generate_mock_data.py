"""
Mock data generator for the Virginia analytics tables — Issue #301.

Generates one CSV per table for local development, API testing, dashboard
testing and demonstrations. All values are synthetic; no real or sensitive
information is used.

Schema source:
    https://github.com/saayam-for-all/database/wiki/
    *-Changes-to-the-Database,-Waiting-for-Microservice

Generation order follows the foreign-key dependency graph so that every
child row can only reference a parent that has already been created:

    countries
      └── states
            ├── cities
            ├── organizations
            └── users ──┬── user_locations
                        ├── user_skills ── help_categories
                        └── volunteer_details ── volunteer_locations

Usage:
    python generate_mock_data.py                  # 400 rows (default)
    python generate_mock_data.py --rows 100
    python generate_mock_data.py --rows 5000
    python generate_mock_data.py --outdir ./out --seed 7

Row counts:
    --rows sets the size of the users table. The other tables scale from it:
    lookup tables (countries, states, cities, help_categories) are fixed by
    the real reference data; volunteer_details/locations/skills are derived
    from the generated users.
"""

import argparse
import json
import random
from pathlib import Path

import reference_data as ref
import utils


# ─────────────────────────────────────────────────────────
# Column order — mirrors the DDL exactly for each table
# ─────────────────────────────────────────────────────────

COLUMNS = {
    "countries": [
        "country_id", "country_name", "phone_code", "country_code",
        "last_updated_at", "is_eu_member",
    ],
    "states": [
        "state_id", "country_id", "state_name", "state_code", "last_updated_at",
    ],
    "cities": [
        # NOTE: "lattitude" is spelled with two t's in the DDL. Preserved
        # verbatim so the CSV header matches the real column name.
        "city_id", "state_id", "city_name", "lattitude", "longitude",
        "last_updated_at",
    ],
    "help_categories": [
        "cat_id", "cat_name", "cat_desc", "last_updated_at",
    ],
    "users": [
        "user_id", "state_id", "country_id", "user_status_id", "full_name",
        "first_name", "middle_name", "last_name", "primary_email_address",
        "primary_phone_number", "addr_ln1", "addr_ln2", "addr_ln3",
        "city_name", "zip_code", "last_location", "last_updated_at",
        "time_zone", "profile_picture_path", "gender", "language_1",
        "language_2", "language_3", "promotion_wizard_stage",
        "promotion_wizard_last_updated_at", "external_auth_provider",
        "dob", "is_eu",
    ],
    "volunteer_details": [
        "user_id", "terms_and_conditions", "terms_accepted_at",
        "govt_id_path1", "govt_id_path2", "path1_updated_at",
        "path2_updated_at", "availability_days", "availability_times",
        "created_at", "last_updated_at",
    ],
    "user_skills": [
        "user_id", "cat_id", "skill_level", "created_at", "last_updated_at",
    ],
    "organizations": [
        "org_id", "org_name", "street", "city_name", "state_id", "zip_code",
        "mission", "web_url", "phone", "email", "org_type", "org_size",
        "org_rating", "is_collaborator", "is_contributor", "created_at",
        "last_updated_at",
    ],
    "user_locations": [
        "user_id", "prev_loc", "curr_loc", "last_updated_at",
    ],
    "volunteer_locations": [
        "user_id", "prev_loc", "curr_loc", "last_updated_at",
    ],
}


# ─────────────────────────────────────────────────────────
# Lookup tables
# ─────────────────────────────────────────────────────────

def generate_countries():
    """countries — the root of the geographic hierarchy."""
    rows = []
    code_to_id = {}
    for idx, (name, phone_code, code, is_eu) in enumerate(ref.COUNTRIES, start=1):
        code_to_id[code] = idx
        rows.append({
            "country_id": idx,
            "country_name": name,
            "phone_code": phone_code,
            "country_code": code,
            "last_updated_at": utils.random_timestamp(),
            "is_eu_member": "true" if is_eu else "false",
        })
    return rows, code_to_id


def generate_states(code_to_id):
    """states — every row references a real country (country_id is NOT NULL)."""
    rows = []
    for country_code, states in ref.STATES.items():
        country_id = code_to_id[country_code]
        for state_id, state_name, state_code in states:
            rows.append({
                "state_id": state_id,
                "country_id": country_id,
                "state_name": state_name,
                "state_code": state_code,
                "last_updated_at": utils.random_timestamp(),
            })
    return rows


def generate_cities(state_rows):
    """cities — every row references a state that exists in states.csv."""
    valid_state_ids = {r["state_id"] for r in state_rows}
    rows = []
    city_id = 1
    for state_id, cities in ref.CITIES.items():
        if state_id not in valid_state_ids:
            continue
        for city_name, lat, lon, _zip_prefix in cities:
            rows.append({
                "city_id": city_id,
                "state_id": state_id,
                "city_name": city_name,
                "lattitude": f"{lat:.6f}",
                "longitude": f"{lon:.6f}",
                "last_updated_at": utils.random_timestamp(),
            })
            city_id += 1
    return rows


def generate_help_categories():
    """help_categories — official materialized-path cat_ids."""
    return [
        {
            "cat_id": cat_id,
            "cat_name": cat_name,
            "cat_desc": cat_desc,
            "last_updated_at": utils.random_timestamp(),
        }
        for cat_id, cat_name, cat_desc in ref.HELP_CATEGORIES
    ]


# ─────────────────────────────────────────────────────────
# users
# ─────────────────────────────────────────────────────────

def _build_location_index(state_rows, city_rows):
    """
    Build a lookup of (state_id -> country_id) and (state_id -> [cities]),
    so a user's country, state, city, ZIP and coordinates all agree.
    """
    state_to_country = {r["state_id"]: r["country_id"] for r in state_rows}
    state_to_cities = {}
    for r in city_rows:
        state_to_cities.setdefault(r["state_id"], []).append(r)
    # Attach ZIP prefixes from the reference data
    zip_lookup = {}
    for state_id, cities in ref.CITIES.items():
        for city_name, _lat, _lon, zip_prefix in cities:
            zip_lookup[(state_id, city_name)] = zip_prefix
    return state_to_country, state_to_cities, zip_lookup


def _make_zip(state_id, city_name, zip_lookup):
    """Generate a plausible postal code consistent with the city."""
    prefix = zip_lookup.get((state_id, city_name), "000")
    if prefix and prefix[0].isalpha():
        # UK/Canada style — prefix plus a short alphanumeric suffix
        return f"{prefix} {random.randint(1, 9)}{random.choice('ABDEFGHJLNPQRSTUWXYZ')}{random.choice('ABDEFGHJLNPQRSTUWXYZ')}"
    return f"{prefix}{random.randint(0, 99):02d}"


def generate_users(n_rows, state_rows, city_rows, country_rows):
    """
    users — the central table. Each user gets a consistent
    country -> state -> city -> ZIP -> coordinate chain.
    """
    state_to_country, state_to_cities, zip_lookup = _build_location_index(
        state_rows, city_rows
    )
    eu_country_ids = {
        r["country_id"] for r in country_rows if r["is_eu_member"] == "true"
    }
    # Only states that actually have cities are eligible, so every user
    # can be given a city consistent with their state.
    eligible_states = [s for s in state_to_cities if s in state_to_country]

    rows = []
    for seq in range(1, n_rows + 1):
        state_id = random.choice(eligible_states)
        country_id = state_to_country[state_id]
        city = random.choice(state_to_cities[state_id])
        city_name = city["city_name"]
        lat, lon = utils.jitter_point(
            float(city["lattitude"]), float(city["longitude"])
        )

        first = random.choice(ref.FIRST_NAMES)
        last = random.choice(ref.LAST_NAMES)
        has_middle = random.random() < 0.35
        middle = random.choice(ref.FIRST_NAMES) if has_middle else ""
        full_name = " ".join(p for p in (first, middle, last) if p)

        # Synthetic contact details. example.com/.org/.net are reserved by
        # RFC 2606 for documentation, so these can never reach a real inbox.
        email = f"{first.lower()}.{last.lower()}{seq}@{random.choice(ref.EMAIL_DOMAINS)}"
        country_code = next(
            c["phone_code"] for c in country_rows if c["country_id"] == country_id
        )
        phone = f"{country_code}-555-{random.randint(1000, 9999)}"

        addr1 = f"{random.randint(1, 9999)} {random.choice(ref.STREET_NAMES)} {random.choice(ref.STREET_TYPES)}"
        addr2 = f"Apt {random.randint(1, 450)}" if random.random() < 0.3 else ""
        addr3 = ""

        created, updated = utils.timestamp_pair()
        promo_stage = random.choice([None, 1, 2, 3, 4, 5])

        # Pick 1-3 distinct language ids; unused slots stay NULL.
        langs = random.sample(ref.LANGUAGE_IDS, k=random.randint(1, 3))
        langs += [""] * (3 - len(langs))

        rows.append({
            "user_id": utils.make_user_id(seq),
            "state_id": state_id,
            "country_id": country_id,
            "user_status_id": random.choices([1, 2, 3], weights=[0.8, 0.15, 0.05])[0],
            "full_name": full_name,
            "first_name": first,
            "middle_name": middle,
            "last_name": last,
            "primary_email_address": email,
            "primary_phone_number": phone,
            "addr_ln1": addr1,
            "addr_ln2": addr2,
            "addr_ln3": addr3,
            "city_name": city_name,
            "zip_code": _make_zip(state_id, city_name, zip_lookup),
            "last_location": utils.to_pg_point(lat, lon),
            "last_updated_at": updated,
            "time_zone": random.choice(ref.TIME_ZONES),
            "profile_picture_path": (
                f"s3://saayam-mock-profiles/{utils.make_user_id(seq)}.jpg"
                if random.random() < 0.45 else ""
            ),
            "gender": random.choice(ref.GENDERS),
            "language_1": langs[0],
            "language_2": langs[1],
            "language_3": langs[2],
            "promotion_wizard_stage": promo_stage if promo_stage is not None else "",
            "promotion_wizard_last_updated_at": updated,
            "external_auth_provider": random.choice(ref.EXTERNAL_AUTH_PROVIDERS) or "",
            "dob": utils.random_date(),
            "is_eu": "true" if country_id in eu_country_ids else "false",
            # Carried for downstream generators, stripped before writing.
            "_created_at": created,
            "_lat": lat,
            "_lon": lon,
        })
    return rows


# ─────────────────────────────────────────────────────────
# volunteer_details and dependent tables
# ─────────────────────────────────────────────────────────

def generate_volunteer_details(user_rows, volunteer_ratio=0.45):
    """
    volunteer_details — a subset of users who became volunteers.

    Returns rows plus the list of user dicts that were selected, so
    volunteer_locations can reference exactly this set.
    """
    selected = random.sample(
        user_rows, k=max(1, int(len(user_rows) * volunteer_ratio))
    )
    rows = []
    for u in selected:
        created, updated = utils.timestamp_pair()
        accepted = random.random() < 0.9
        has_second_id = random.random() < 0.4
        rows.append({
            "user_id": u["user_id"],
            "terms_and_conditions": "true" if accepted else "false",
            "terms_accepted_at": created if accepted else "",
            "govt_id_path1": f"s3://saayam-mock-ids/{u['user_id']}-1.pdf",
            "govt_id_path2": (
                f"s3://saayam-mock-ids/{u['user_id']}-2.pdf" if has_second_id else ""
            ),
            "path1_updated_at": created,
            "path2_updated_at": updated if has_second_id else "",
            # JSONB columns — compact JSON so \copy loads them directly.
            "availability_days": json.dumps(
                sorted(random.sample(ref.AVAILABILITY_DAYS,
                                     k=random.randint(1, 5)))
            ),
            "availability_times": json.dumps(
                sorted(random.sample(ref.AVAILABILITY_TIMES,
                                     k=random.randint(1, 3)))
            ),
            "created_at": created,
            "last_updated_at": updated,
        })
    return rows, selected


def generate_user_skills(user_rows, category_rows, avg_skills=2.5):
    """
    user_skills — composite PK (user_id, cat_id), so each pair appears once.

    Only leaf-ish categories are used as skills; the top-level parent ids
    ("1", "2", ...) are skipped because a skill is expected to be specific.
    """
    leaf_cats = [
        c["cat_id"] for c in category_rows
        if "." in c["cat_id"] and c["cat_id"] != "0.0.0.0.0"
    ]
    rows = []
    for u in user_rows:
        k = max(1, int(random.gauss(avg_skills, 1.2)))
        k = min(k, 6, len(leaf_cats))
        for cat_id in random.sample(leaf_cats, k=k):
            created, updated = utils.timestamp_pair()
            rows.append({
                "user_id": u["user_id"],
                "cat_id": cat_id,
                "skill_level": random.choices(
                    ref.SKILL_LEVELS, weights=[0.35, 0.35, 0.22, 0.08]
                )[0],
                "created_at": created,
                "last_updated_at": updated,
            })
    return rows


def _generate_location_rows(source_rows):
    """
    Shared builder for user_locations and volunteer_locations.

    Both tables store geography(Point, 4326) rather than city/state ids,
    so coordinates are jittered around the row's own city to keep them
    plausibly inside the right region. prev_loc is a second, nearby point
    (the schema's trigger shifts curr_loc into prev_loc on update).
    """
    rows = []
    for u in source_rows:
        curr_lat, curr_lon = u["_lat"], u["_lon"]
        has_prev = random.random() < 0.7
        if has_prev:
            prev_lat, prev_lon = utils.jitter_point(curr_lat, curr_lon, max_km=12.0)
            prev = utils.to_ewkt(prev_lat, prev_lon)
        else:
            prev = ""
        rows.append({
            "user_id": u["user_id"],
            "prev_loc": prev,
            "curr_loc": utils.to_ewkt(curr_lat, curr_lon),
            "last_updated_at": utils.random_timestamp(),
        })
    return rows


def generate_user_locations(user_rows, coverage=0.7):
    """user_locations — references users.user_id directly."""
    subset = random.sample(user_rows, k=max(1, int(len(user_rows) * coverage)))
    return _generate_location_rows(subset)


def generate_volunteer_locations(volunteer_users, coverage=0.8):
    """
    volunteer_locations — references volunteer_details.user_id, NOT users
    directly, so the input must be the users who have a volunteer_details row.
    """
    subset = random.sample(
        volunteer_users, k=max(1, int(len(volunteer_users) * coverage))
    )
    return _generate_location_rows(subset)


# ─────────────────────────────────────────────────────────
# organizations
# ─────────────────────────────────────────────────────────

def generate_organizations(n_rows, state_rows, city_rows, country_rows):
    """organizations — state_id is the FK; states.state_id is the referenced PK."""
    state_to_cities = {}
    for r in city_rows:
        state_to_cities.setdefault(r["state_id"], []).append(r)
    state_to_country, _, zip_lookup = _build_location_index(state_rows, city_rows)
    # Dial code per country, so an organisation's phone number agrees with
    # the country its state belongs to.
    country_dial = {r["country_id"]: r["phone_code"] for r in country_rows}
    eligible_states = list(state_to_cities.keys())

    rows = []
    used_names = set()
    for seq in range(1, n_rows + 1):
        state_id = random.choice(eligible_states)
        city = random.choice(state_to_cities[state_id])
        city_name = city["city_name"]

        # Keep org names distinct; org_name is not UNIQUE in the schema but
        # duplicate names make dashboards confusing to read.
        for _ in range(50):
            name = (
                f"{random.choice(ref.ORG_PREFIXES)}"
                f"{random.choice(ref.ORG_MIDDLES)} "
                f"{random.choice(ref.ORG_SUFFIXES)}"
            )
            if name not in used_names:
                break
        used_names.add(name)

        slug = name.lower().replace(" ", "")
        created, updated = utils.timestamp_pair()

        # org_rating is CHECK (1..5); NULL models an unrated organisation,
        # which the Organization Performance dashboard needs to handle.
        rated = random.random() < 0.8

        rows.append({
            "org_id": utils.make_org_id(seq),
            "org_name": name[:125],
            "street": f"{random.randint(1, 9999)} {random.choice(ref.STREET_NAMES)} {random.choice(ref.STREET_TYPES)}",
            "city_name": city_name,
            "state_id": state_id,
            "zip_code": _make_zip(state_id, city_name, zip_lookup)[:10],
            "mission": (
                f"{random.choice(ref.ORG_MISSION_OPENERS)} "
                f"{random.choice(ref.ORG_MISSION_SUBJECTS)} "
                f"{random.choice(ref.ORG_MISSION_CLOSERS)}"
            ),
            # CHECK constraint requires web_url LIKE 'http%'
            "web_url": f"https://{slug}.example.org",
            "phone": f"{country_dial[state_to_country[state_id]]}-555-{random.randint(1000, 9999)}",
            # CHECK constraint requires email LIKE '%@%'
            "email": f"contact@{slug}.example.org",
            "org_type": random.choices(
                ["non_profit", "for_profit"], weights=[0.72, 0.28]
            )[0],
            "org_size": random.choices(
                ["small", "medium", "large"], weights=[0.5, 0.35, 0.15]
            )[0],
            "org_rating": random.choices(
                [1, 2, 3, 4, 5], weights=[0.04, 0.08, 0.18, 0.38, 0.32]
            )[0] if rated else "",
            "is_collaborator": "true" if random.random() < 0.35 else "false",
            "is_contributor": "true" if random.random() < 0.55 else "false",
            "created_at": created,
            "last_updated_at": updated,
        })
    return rows


# ─────────────────────────────────────────────────────────
# Validation
# ─────────────────────────────────────────────────────────

def validate(tables):
    """
    Run the data-quality checks listed in the issue.
    Returns (passed, failed) counts and prints a per-check report.
    """
    print("\nValidation")
    print("-" * 62)
    results = []

    def check(label, ok, detail=""):
        results.append(ok)
        status = "PASS" if ok else "FAIL"
        line = f"  [{status}] {label}"
        if detail:
            line += f" — {detail}"
        print(line)

    # Primary key uniqueness
    pk_map = {
        "countries": ["country_id"],
        "states": ["state_id"],
        "cities": ["city_id"],
        "help_categories": ["cat_id"],
        "users": ["user_id"],
        "volunteer_details": ["user_id"],
        "user_skills": ["user_id", "cat_id"],
        "organizations": ["org_id"],
        "user_locations": ["user_id"],
        "volunteer_locations": ["user_id"],
    }
    for table, pk_cols in pk_map.items():
        rows = tables[table]
        keys = [tuple(r[c] for c in pk_cols) for r in rows]
        dupes = len(keys) - len(set(keys))
        check(f"{table}: primary key unique", dupes == 0,
              f"{dupes} duplicates" if dupes else f"{len(keys)} rows")

    # Foreign key integrity
    country_ids = {r["country_id"] for r in tables["countries"]}
    state_ids = {r["state_id"] for r in tables["states"]}
    user_ids = {r["user_id"] for r in tables["users"]}
    vol_ids = {r["user_id"] for r in tables["volunteer_details"]}
    cat_ids = {r["cat_id"] for r in tables["help_categories"]}

    fk_checks = [
        ("states.country_id -> countries", tables["states"], "country_id", country_ids),
        ("cities.state_id -> states", tables["cities"], "state_id", state_ids),
        ("users.country_id -> countries", tables["users"], "country_id", country_ids),
        ("users.state_id -> states", tables["users"], "state_id", state_ids),
        ("volunteer_details.user_id -> users", tables["volunteer_details"], "user_id", user_ids),
        ("user_skills.user_id -> users", tables["user_skills"], "user_id", user_ids),
        ("user_skills.cat_id -> help_categories", tables["user_skills"], "cat_id", cat_ids),
        ("organizations.state_id -> states", tables["organizations"], "state_id", state_ids),
        ("user_locations.user_id -> users", tables["user_locations"], "user_id", user_ids),
        ("volunteer_locations.user_id -> volunteer_details",
         tables["volunteer_locations"], "user_id", vol_ids),
    ]
    for label, rows, col, valid in fk_checks:
        orphans = [r for r in rows if r[col] not in valid and r[col] != ""]
        check(f"{label}", not orphans,
              f"{len(orphans)} orphans" if orphans else f"{len(rows)} rows")

    # states.country_id is NOT NULL in the schema
    null_country = [r for r in tables["states"] if r["country_id"] in ("", None)]
    check("states.country_id NOT NULL", not null_country,
          f"{len(null_country)} nulls" if null_country else "")

    # Geographic consistency: every user's city belongs to their state
    state_city_pairs = {(r["state_id"], r["city_name"]) for r in tables["cities"]}
    bad_geo = [
        r for r in tables["users"]
        if (r["state_id"], r["city_name"]) not in state_city_pairs
    ]
    check("users: city belongs to its state", not bad_geo,
          f"{len(bad_geo)} mismatches" if bad_geo else "")

    bad_geo_org = [
        r for r in tables["organizations"]
        if (r["state_id"], r["city_name"]) not in state_city_pairs
    ]
    check("organizations: city belongs to its state", not bad_geo_org,
          f"{len(bad_geo_org)} mismatches" if bad_geo_org else "")

    # Phone dial code agrees with the row's country
    dial = {r["country_id"]: r["phone_code"] for r in tables["countries"]}
    bad_phone = [
        r for r in tables["users"]
        if not r["primary_phone_number"].startswith(dial[r["country_id"]] + "-")
    ]
    check("users: phone dial code matches country", not bad_phone,
          f"{len(bad_phone)} mismatches" if bad_phone else "")

    state_country = {r["state_id"]: r["country_id"] for r in tables["states"]}
    bad_org_phone = [
        r for r in tables["organizations"]
        if not r["phone"].startswith(dial[state_country[r["state_id"]]] + "-")
    ]
    check("organizations: phone dial code matches country", not bad_org_phone,
          f"{len(bad_org_phone)} mismatches" if bad_org_phone else "")

    # Timestamp ordering where both columns exist
    from datetime import datetime as _dt

    def _ts_ok(rows, a, b):
        bad = 0
        for r in rows:
            if r.get(a) and r.get(b):
                if _dt.strptime(r[a], utils.TS_FORMAT) > _dt.strptime(r[b], utils.TS_FORMAT):
                    bad += 1
        return bad

    for table in ("volunteer_details", "user_skills", "organizations"):
        bad = _ts_ok(tables[table], "created_at", "last_updated_at")
        check(f"{table}: created_at <= last_updated_at", bad == 0,
              f"{bad} inverted" if bad else "")

    # org_rating CHECK (1..5) — blank is allowed (unrated)
    bad_rating = [
        r for r in tables["organizations"]
        if r["org_rating"] != "" and not (1 <= int(r["org_rating"]) <= 5)
    ]
    check("organizations.org_rating within 1..5", not bad_rating,
          f"{len(bad_rating)} out of range" if bad_rating else "")

    # CHECK constraints on organizations
    bad_url = [r for r in tables["organizations"]
               if r["web_url"] and not r["web_url"].startswith("http")]
    check("organizations.web_url LIKE 'http%'", not bad_url)
    bad_email = [r for r in tables["organizations"]
                 if r["email"] and "@" not in r["email"]]
    check("organizations.email LIKE '%@%'", not bad_email)

    passed = sum(results)
    total = len(results)
    print("-" * 62)
    print(f"  {passed}/{total} checks passed")
    return passed, total


# ─────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generate mock CSV data for the Virginia analytics tables (Issue #301)"
    )
    parser.add_argument("--rows", type=int, default=400,
                        help="Number of users to generate; other tables scale from this (default: 400)")
    parser.add_argument("--orgs", type=int, default=None,
                        help="Number of organizations (default: same as --rows)")
    parser.add_argument("--outdir", type=str, default=".",
                        help="Output directory for the CSV files (default: current directory)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducible output (default: 42)")
    args = parser.parse_args()

    random.seed(args.seed)
    n_users = args.rows
    n_orgs = args.orgs if args.orgs is not None else args.rows
    outdir = Path(args.outdir)

    print(f"\nSaayam mock data generator — Issue #301")
    print(f"  users : {n_users:,}")
    print(f"  orgs  : {n_orgs:,}")
    print(f"  seed  : {args.seed}")
    print(f"  outdir: {outdir.resolve()}\n")

    # Generate in FK dependency order
    print("Generating...")
    countries, code_to_id = generate_countries()
    states = generate_states(code_to_id)
    cities = generate_cities(states)
    help_categories = generate_help_categories()
    users = generate_users(n_users, states, cities, countries)
    volunteer_details, volunteer_users = generate_volunteer_details(users)
    user_skills = generate_user_skills(users, help_categories)
    organizations = generate_organizations(n_orgs, states, cities, countries)
    user_locations = generate_user_locations(users)
    volunteer_locations = generate_volunteer_locations(volunteer_users)

    tables = {
        "countries": countries,
        "states": states,
        "cities": cities,
        "help_categories": help_categories,
        "users": users,
        "volunteer_details": volunteer_details,
        "user_skills": user_skills,
        "organizations": organizations,
        "user_locations": user_locations,
        "volunteer_locations": volunteer_locations,
    }

    passed, total = validate(tables)

    print("\nWriting CSV files")
    print("-" * 62)
    for table, rows in tables.items():
        cols = COLUMNS[table]
        # Strip internal helper keys (prefixed with _) before writing
        clean = [{k: r[k] for k in cols} for r in rows]
        path = utils.write_csv(clean, f"{table}.csv", outdir, cols)
        print(f"  {table + '.csv':<28} {len(clean):>7,} rows")

    print("-" * 62)
    total_rows = sum(len(r) for r in tables.values())
    print(f"  {'TOTAL':<28} {total_rows:>7,} rows across {len(tables)} files")

    if passed < total:
        print("\nSome validation checks failed — review before committing.")
        raise SystemExit(1)
    print("\nAll validation checks passed.\n")


if __name__ == "__main__":
    main()
