"""
BAARS-IV Self-Report: raw score -> percentile lookup (current symptoms).

Transcribed from the three age-band score sheets (18-39, 40-59, 60-89).

Each entry is (lowest_raw_score, highest_raw_score, percentile).
Percentiles are ints for exact rows, or the strings "1-50", "51-75", "99+"
for the banded rows at the bottom/top of each table.
"""

__all__ = [
    "baars_percentile", "baars_count_percentile",
    "NORMS", "COUNT_NORMS", "BAND_TO_INT",
]

NORMS = {
    (18, 39): {
        "inattention": [
            (9, 10, "1-50"), (11, 15, "51-75"), (16, 16, 80), (17, 17, 84),
            (18, 18, 89), (19, 19, 90), (20, 20, 92), (21, 21, 93),
            (22, 22, 95), (23, 23, 96), (24, 26, 97), (27, 28, 98),
            (29, 36, "99+"),
        ],
        "hyperactive": [
            (5, 5, "1-50"), (6, 8, "51-75"), (9, 9, 79), (10, 10, 86),
            (11, 11, 90), (12, 12, 93), (13, 13, 94), (14, 14, 96),
            (15, 16, 98), (17, 20, "99+"),
        ],
        "impulsive": [
            (4, 4, "1-50"), (5, 6, "51-75"), (7, 7, 81), (8, 8, 92),
            (9, 9, 94), (10, 10, 95), (11, 11, 96), (12, 13, 98),
            (14, 16, "99+"),
        ],
        "total": [
            (18, 22, "1-50"), (23, 29, "51-75"), (30, 30, 77), (31, 31, 79),
            (32, 32, 81), (33, 33, 82), (34, 34, 83), (35, 35, 85),
            (36, 36, 90), (37, 37, 91), (38, 38, 92), (39, 41, 93),
            (42, 42, 94), (43, 43, 95), (44, 45, 96), (46, 48, 97),
            (49, 53, 98), (54, 72, "99+"),
        ],
        "sct": [
            (9, 12, "1-50"), (13, 16, "51-75"), (17, 17, 77), (18, 18, 83),
            (19, 19, 85), (20, 20, 87), (21, 21, 90), (22, 22, 92),
            (23, 23, 93), (24, 24, 94), (25, 26, 96), (27, 28, 97),
            (29, 31, 98), (32, 36, "99+"),
        ],
    },
    (40, 59): {
        "inattention": [
            (9, 10, "1-50"), (11, 13, "51-75"), (14, 14, 78), (15, 15, 81),
            (16, 16, 84), (17, 17, 86), (18, 18, 91), (19, 19, 93),
            (20, 20, 94), (21, 21, 96), (22, 23, 97), (24, 26, 98),
            (27, 36, "99+"),
        ],
        "hyperactive": [
            (5, 5, "1-50"), (6, 7, "51-75"), (8, 8, 80), (9, 9, 86),
            (10, 10, 91), (11, 11, 94), (12, 12, 96), (13, 13, 97),
            (14, 14, 98), (15, 20, "99+"),
        ],
        "impulsive": [
            (4, 4, "1-50"), (5, 6, "51-75"), (7, 7, 84), (8, 8, 91),
            (9, 9, 95), (10, 10, 96), (11, 11, 97), (12, 12, 98),
            (13, 16, "99+"),
        ],
        "total": [
            (18, 21, "1-50"), (22, 28, "51-75"), (29, 29, 78), (30, 30, 80),
            (31, 31, 84), (32, 32, 86), (33, 33, 88), (34, 34, 89),
            (35, 35, 91), (36, 36, 93), (37, 37, 94), (38, 38, 95),
            (39, 41, 96), (42, 44, 97), (45, 51, 98), (52, 72, "99+"),
        ],
        "sct": [
            (9, 11, "1-50"), (12, 15, "51-75"), (16, 16, 76), (17, 17, 81),
            (18, 18, 84), (19, 19, 85), (20, 20, 88), (21, 21, 90),
            (22, 22, 92), (23, 23, 93), (24, 25, 94), (26, 26, 95),
            (27, 28, 96), (29, 29, 97), (30, 30, 98), (31, 36, "99+"),
        ],
    },
    (60, 89): {
        "inattention": [
            (9, 10, "1-50"), (11, 13, "51-75"), (14, 14, 77), (15, 15, 84),
            (16, 16, 88), (17, 17, 92), (18, 18, 96), (19, 19, 97),
            (20, 36, "99+"),
        ],
        "hyperactive": [
            (5, 5, "1-50"), (6, 6, "51-75"), (7, 7, 85), (8, 8, 92),
            (9, 9, 95), (10, 11, 97), (12, 12, 98), (13, 20, "99+"),
        ],
        "impulsive": [
            (4, 4, "1-50"), (5, 5, "51-75"), (6, 6, 83), (7, 7, 90),
            (8, 8, 96), (9, 9, 97), (10, 10, 98), (11, 16, "99+"),
        ],
        "total": [
            (18, 21, "1-50"), (22, 26, "51-75"), (27, 27, 79), (28, 28, 83),
            (29, 29, 87), (30, 30, 89), (31, 31, 91), (32, 32, 93),
            (33, 33, 95), (34, 34, 96), (35, 35, 97), (36, 38, 98),
            (39, 72, "99+"),
        ],
        "sct": [
            (9, 12, "1-50"), (13, 15, "51-75"), (16, 16, 78), (17, 17, 84),
            (18, 18, 89), (19, 19, 91), (20, 20, 94), (21, 21, 96),
            (22, 22, 97), (23, 23, 98), (24, 36, "99+"),
        ],
    },
}

# Accepted spellings for each subscale.
_ALIASES = {
    "inattention": "inattention", "inattentive": "inattention", "ia": "inattention",
    "hyperactive": "hyperactive", "hyperactivity": "hyperactive", "hi": "hyperactive",
    "impulsive": "impulsive", "impulsivity": "impulsive", "im": "impulsive",
    "total": "total", "total adhd": "total", "adhd": "total", "total_adhd": "total",
    "sct": "sct", "sluggish cognitive tempo": "sct",
}


def _normalize_subscale(name):
    key = name.strip().lower().replace("-", " ")
    if key not in _ALIASES:
        raise ValueError(
            f"Unknown subscale {name!r}. Use one of: inattention, hyperactive, "
            f"impulsive, total, sct."
        )
    return _ALIASES[key]


def _age_band(age):
    for (lo, hi), table in NORMS.items():
        if lo <= age <= hi:
            return table
    raise ValueError(f"Age {age} is outside the normed range (18-89).")


# Integer stand-ins for the banded rows, used when as_int=True.
# "1-50" and "51-75" use the midpoint (rounded down); "99+" has no upper
# bound in the tables, so it maps to 99.
BAND_TO_INT = {"1-50": 25, "51-75": 63, "99+": 99}


def baars_percentile(age, raw_score, subscale, as_int=False):
    """
    Return the BAARS-IV self-report percentile for a raw score.

    age        : int, 18-89
    raw_score  : int, the subscale raw score
    subscale   : "inattention", "hyperactive", "impulsive", "total", or "sct"
    as_int     : if True, always return an int, replacing the banded rows
                 with BAND_TO_INT ("1-50" -> 25, "51-75" -> 63, "99+" -> 99)

    Returns an int (e.g. 93) or, when as_int is False, possibly one of the
    strings "1-50", "51-75", "99+".
    Raises ValueError for an out-of-range age, score, or unknown subscale.
    """
    table = _age_band(age)[_normalize_subscale(subscale)]
    for lo, hi, pct in table:
        if lo <= raw_score <= hi:
            if as_int and isinstance(pct, str):
                return BAND_TO_INT[pct]
            return pct
    raise ValueError(
        f"Raw score {raw_score} is outside the valid range "
        f"({table[0][0]}-{table[-1][1]}) for this subscale."
    )


# ---------------------------------------------------------------------------
# Symptom counts (number of items answered 3 or 4)
# ---------------------------------------------------------------------------
# Each entry is (lowest_count, highest_count, percentile).
# Note: in the 60-89 table, a count of 0 is printed in both the 76th row and
# the 1-75 row for Current Inattention and Current Hyperactive-Impulsive, so
# 0 maps to "1-76" for those two subscales.

COUNT_NORMS = {
    (18, 39): {
        "current_inattention": [
            (0, 0, "1-75"), (1, 1, 86), (2, 2, 89), (3, 3, 92), (4, 4, 95),
            (5, 5, 96), (6, 6, 97), (7, 8, 98), (9, 9, "99+"),
        ],
        "current_hi": [
            (0, 0, "1-75"), (1, 1, 80), (2, 2, 88), (3, 3, 93), (4, 4, 95),
            (5, 5, 97), (6, 7, 98), (8, 9, "99+"),
        ],
        "current_total": [
            (0, 1, "1-75"), (2, 2, 80), (3, 3, 85), (4, 4, 88), (5, 5, 91),
            (6, 6, 92), (7, 7, 94), (8, 8, 95), (9, 11, 97), (12, 13, 98),
            (14, 18, "99+"),
        ],
        "current_sct": [
            (0, 0, "1-75"), (1, 1, 78), (2, 2, 85), (3, 3, 88), (4, 4, 93),
            (5, 5, 94), (6, 6, 96), (7, 7, 97), (8, 8, 98), (9, 9, "99+"),
        ],
        "child_inattention": [
            (0, 0, "1-75"), (1, 1, 79), (2, 2, 83), (3, 3, 85), (4, 4, 89),
            (5, 5, 92), (6, 6, 93), (7, 7, 96), (8, 8, 98), (9, 9, "99+"),
        ],
        "child_hi": [
            (0, 0, "1-75"), (1, 1, 78), (2, 2, 83), (3, 3, 87), (4, 4, 89),
            (5, 5, 93), (6, 6, 95), (7, 7, 97), (8, 8, 98), (9, 9, "99+"),
        ],
        "child_total": [
            (0, 2, "1-75"), (3, 3, 78), (4, 4, 81), (5, 5, 84), (6, 6, 86),
            (7, 7, 87), (8, 8, 89), (9, 9, 92), (10, 10, 93), (11, 12, 95),
            (13, 13, 96), (14, 14, 97), (15, 16, 98), (17, 18, "99+"),
        ],
    },
    (40, 59): {
        "current_inattention": [
            (0, 0, "1-75"), (1, 1, 90), (2, 2, 92), (3, 3, 95), (4, 5, 97),
            (6, 7, 98), (8, 9, "99+"),
        ],
        "current_hi": [
            (0, 0, "1-75"), (1, 1, 86), (2, 2, 91), (3, 3, 95), (4, 4, 97),
            (5, 5, 98), (6, 9, "99+"),
        ],
        "current_total": [
            (0, 0, "1-75"), (1, 1, 82), (2, 2, 86), (3, 3, 89), (4, 4, 91),
            (5, 5, 94), (6, 7, 96), (8, 8, 97), (9, 13, 98), (14, 18, "99+"),
        ],
        "current_sct": [
            (0, 0, "1-75"), (1, 1, 80), (2, 2, 86), (3, 3, 90), (4, 4, 92),
            (5, 5, 94), (6, 6, 95), (7, 7, 97), (8, 8, 98), (9, 9, "99+"),
        ],
        "child_inattention": [
            (0, 0, "1-75"), (1, 1, 84), (2, 2, 88), (3, 3, 91), (4, 4, 93),
            (5, 5, 94), (6, 6, 96), (7, 7, 97), (8, 8, 98), (9, 9, "99+"),
        ],
        "child_hi": [
            (0, 0, "1-75"), (1, 1, 84), (2, 2, 88), (3, 3, 90), (4, 4, 94),
            (5, 5, 96), (6, 6, 97), (7, 8, 98), (9, 9, "99+"),
        ],
        "child_total": [
            (0, 1, "1-75"), (2, 2, 81), (3, 3, 83), (4, 4, 86), (5, 5, 88),
            (6, 6, 90), (7, 7, 93), (8, 8, 94), (9, 9, 95), (10, 10, 97),
            (11, 13, 98), (14, 18, "99+"),
        ],
    },
    (60, 89): {
        "current_inattention": [
            (0, 0, "1-76"), (1, 1, 94), (2, 2, 97), (3, 9, "99+"),
        ],
        "current_hi": [
            (0, 0, "1-76"), (1, 1, 94), (2, 2, 96), (3, 3, 98), (4, 9, "99+"),
        ],
        "current_total": [
            (0, 0, "1-75"), (1, 1, 89), (2, 2, 92), (3, 3, 95), (4, 4, 97),
            (5, 5, 98), (6, 18, "99+"),
        ],
        "current_sct": [
            (0, 0, "1-75"), (1, 1, 84), (2, 2, 88), (3, 3, 93), (4, 4, 97),
            (5, 9, "99+"),
        ],
        "child_inattention": [
            (0, 0, "1-75"), (1, 1, 90), (2, 2, 92), (3, 3, 93), (4, 4, 95),
            (5, 5, 97), (6, 9, "99+"),
        ],
        "child_hi": [
            (0, 0, "1-75"), (1, 1, 92), (2, 2, 95), (3, 4, 97), (5, 6, 98),
            (7, 9, "99+"),
        ],
        "child_total": [
            (0, 0, "1-75"), (1, 1, 85), (2, 2, 89), (3, 3, 92), (4, 4, 93),
            (5, 6, 95), (7, 7, 96), (8, 8, 97), (9, 9, 98), (10, 18, "99+"),
        ],
    },
}

BAND_TO_INT.update({"1-75": 38, "1-76": 38})

_COUNT_ALIASES = {}
for _prefix in ("current", "child"):
    for _names, _canon in (
        (("inattention", "inattentive", "ia"), "inattention"),
        (("hi", "hyperactive impulsive", "hyperactive_impulsive",
          "hyperactivity impulsivity"), "hi"),
        (("total", "total adhd", "total_adhd", "adhd"), "total"),
        (("sct", "sluggish cognitive tempo"), "sct"),
    ):
        if _prefix == "child" and _canon == "sct":
            continue  # there is no childhood SCT column
        for _n in _names:
            for _sep in (" ", "_"):
                _COUNT_ALIASES[f"{_prefix}{_sep}{_n}"] = f"{_prefix}_{_canon}"


def _normalize_count_subscale(name):
    key = name.strip().lower().replace("-", " ")
    if key not in _COUNT_ALIASES:
        raise ValueError(
            f"Unknown symptom-count subscale {name!r}. Use one of: "
            + ", ".join(sorted(COUNT_NORMS[(18, 39)]))
        )
    return _COUNT_ALIASES[key]


def baars_count_percentile(age, count, subscale, as_int=False):
    """
    Return the BAARS-IV self-report percentile for a symptom count
    (the number of items in a subscale answered 3 or 4).

    age       : int, 18-89
    count     : int, number of items rated 3 or 4
    subscale  : one of "current_inattention", "current_hi", "current_total",
                "current_sct", "child_inattention", "child_hi", "child_total"
                (spaces or "-" also work, e.g. "Child Hyperactive-Impulsive")
    as_int    : if True, always return an int, replacing banded rows with
                BAND_TO_INT ("1-75" -> 38, "99+" -> 99, etc.)

    Returns an int or, when as_int is False, possibly a string band.
    Raises ValueError for an out-of-range age, count, or unknown subscale.
    """
    for (lo, hi), table in COUNT_NORMS.items():
        if lo <= age <= hi:
            break
    else:
        raise ValueError(f"Age {age} is outside the normed range (18-89).")
    rows = table[_normalize_count_subscale(subscale)]
    for lo, hi, pct in rows:
        if lo <= count <= hi:
            if as_int and isinstance(pct, str):
                return BAND_TO_INT[pct]
            return pct
    raise ValueError(
        f"Count {count} is outside the valid range "
        f"({rows[0][0]}-{rows[-1][1]}) for this subscale."
    )


if __name__ == "__main__":
    print(baars_percentile(25, 21, "inattention"))   # 93
    print(baars_percentile(45, 38, "total"))         # 95
    print(baars_percentile(70, 7, "impulsive"))      # 90
    print(baars_percentile(30, 12, "sct"))           # 1-50
    print(baars_percentile(30, 12, "sct", as_int=True))   # 25
    print(baars_percentile(30, 14, "sct", as_int=True))   # 63
    print(baars_percentile(30, 35, "sct", as_int=True))   # 99
    print(baars_count_percentile(25, 3, "current_inattention"))        # 92
    print(baars_count_percentile(45, 7, "child total"))                # 93
    print(baars_count_percentile(65, 0, "Current Hyperactive-Impulsive"))  # 1-76
    print(baars_count_percentile(65, 0, "current_hi", as_int=True))    # 38
