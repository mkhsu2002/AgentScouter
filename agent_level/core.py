"""Agent Level Calculator: pure scoring functions (Formula Spec v1).

No I/O, no network, no third-party dependencies. Every function here is
deterministic: the same profile plus the same formula version gives the
same result. Decimals are always floored and every dimension caps at 100.
"""

import math

VERSION = "1.0.0"

AUTONOMY_TIERS = {
    "none": 0,
    "single_batch": 20,
    "multi_batch": 28,
    "domain_full": 36,
    "full": 40,
}

HONESTY_SCORES = {
    "none": 0,
    "disclosed": 15,
    "hidden": 0,
}

TITLES = [
    (1, 4, "Apprentice"),
    (5, 9, "Assistant"),
    (10, 14, "Practitioner"),
    (15, 19, "Expert"),
    (20, 29, "Master"),
    (30, None, "Legend"),
]


def _floor(value):
    return math.floor(value)


def _nonneg_int(profile, key, default=0):
    value = profile.get(key, default)
    if value is None:
        return default
    value = int(value)
    if value < 0:
        raise ValueError(f"{key} must be non-negative")
    return value


def _clamp(value, low, high):
    return max(low, min(high, value))


def level_threshold(level):
    """Cumulative XP required to reach `level`. Lv.1 needs 0."""
    if level < 1:
        raise ValueError("level must be at least 1")
    return 50 * level * (level - 1)


def level_up_cost(level):
    """XP needed to go from `level` to `level + 1`."""
    if level < 1:
        raise ValueError("level must be at least 1")
    return 100 * level


def title_for_level(level):
    for low, high, title in TITLES:
        if level >= low and (high is None or level <= high):
            return title
    raise ValueError(f"no title for level {level}")


def level_for_xp(xp):
    """Return level info for a total XP value."""
    xp = int(xp)
    if xp < 0:
        raise ValueError("xp must be non-negative")
    level = 1
    while level_threshold(level + 1) <= xp:
        level += 1
    nxt = level_threshold(level + 1)
    return {
        "xp": xp,
        "level": level,
        "title": title_for_level(level),
        "current_threshold": level_threshold(level),
        "next_threshold": nxt,
        "xp_to_next": nxt - xp,
        "level_up_cost": level_up_cost(level),
    }


def calculate(profile):
    """Score one agent profile. `profile` follows the README schema."""
    if not isinstance(profile, dict):
        raise ValueError("profile must be an object")

    # --- HUM ---
    persona_items = _clamp(_nonneg_int(profile, "persona_items"), 0, 7)
    soul_bytes = _nonneg_int(profile, "soul_bytes")
    thin = 2 if soul_bytes < 1500 else 0
    persona = max(0, 30 - 4 * (7 - persona_items) - thin)
    pref = min(30, _floor(_nonneg_int(profile, "pref_count") * 1.2))
    tier = profile.get("autonomy_tier", "none")
    if tier not in AUTONOMY_TIERS:
        raise ValueError(f"unknown autonomy_tier: {tier!r}")
    autonomy = AUTONOMY_TIERS[tier]
    hum = min(100, persona + pref + autonomy)

    # --- KNOW ---
    mem_total = _nonneg_int(profile, "mem_total")
    domains = profile.get("domains", []) or []
    people = _nonneg_int(profile, "people")
    groups = _nonneg_int(profile, "groups")
    fact = min(40, _floor(mem_total * 0.6))
    domain = min(30, len(domains) * 3)
    relation = min(15, people * 2 + groups * 2)
    days = profile.get("days_since_update")
    if days is None:
        freshness = 0
    else:
        freshness = _floor(15 - min(15, float(days) * 0.5))
    know = min(100, fact + domain + relation + freshness)

    # --- SKILL ---
    skills = profile.get("skills", []) or []
    skill_count = min(35, len(skills) * 6)
    structure = 0
    used_count = 0
    logged_count = 0
    migration_steps = 0
    for skill in skills:
        steps = _clamp(int(skill.get("steps", 0)), 0, 2)
        acceptance = _clamp(int(skill.get("acceptance", 0)), 0, 2)
        failure = _clamp(int(skill.get("failure", 0)), 0, 2)
        structure += steps + acceptance + failure
        if skill.get("used"):
            used_count += 1
        if skill.get("logged"):
            logged_count += 1
        migration_steps += max(0, int(skill.get("projects", 0)) - 1)
    structure = min(30, structure)
    usage = min(35, used_count * 6 + logged_count * 1)
    skill = min(100, skill_count + structure + usage)

    # --- SPAN ---
    goals_total = _nonneg_int(profile, "goals_total")
    goals_done = _nonneg_int(profile, "goals_done")
    platforms = _nonneg_int(profile, "platforms")
    project = min(50, _floor(goals_total * 2.5))
    migration = min(30, 5 * migration_steps)
    collaboration = min(20, _floor(people * 2 + platforms * 0.5))
    span = min(100, project + migration + collaboration)

    # --- REL ---
    pass_rate = profile.get("pass_rate")
    if pass_rate is None:
        passed = 0
    else:
        passed = _floor(60 * float(pass_rate))
    fixes = _nonneg_int(profile, "fixes")
    acknowledged = _nonneg_int(profile, "acknowledged_fixes")
    fixes_score = min(25, 5 * fixes + 2 * acknowledged)
    honesty = profile.get("honesty", "none")
    if honesty not in HONESTY_SCORES:
        raise ValueError(f"unknown honesty value: {honesty!r}")
    honesty_score = HONESTY_SCORES[honesty]
    rel = min(100, passed + fixes_score + honesty_score)

    # --- Composite and INT ---
    composite = _floor((hum + know + skill + span + rel) / 5)
    reasoning_evidence = _nonneg_int(profile, "reasoning_evidence")
    reasoning_j = _clamp(_nonneg_int(profile, "reasoning_j"), 0, 19)
    reasoning = min(100, 20 * reasoning_evidence + reasoning_j)
    intelligence = _floor(0.5 * know + 0.3 * skill + 0.2 * reasoning)

    # --- XP and level ---
    deliveries = _nonneg_int(profile, "deliveries")
    m = float(profile.get("m", 1.0))
    if m < 0:
        raise ValueError("m must be non-negative")
    xp = _floor(
        m
        * (
            100 * len(skills)
            + 80 * len(domains)
            + 40 * goals_done
            + 25 * deliveries
        )
    )
    level_info = level_for_xp(xp)

    return {
        "version": VERSION,
        "dimensions": {
            "HUM": {
                "score": hum,
                "breakdown": {
                    "persona": persona,
                    "preference": pref,
                    "autonomy": autonomy,
                },
            },
            "KNOW": {
                "score": know,
                "breakdown": {
                    "fact": fact,
                    "domain": domain,
                    "relation": relation,
                    "freshness": freshness,
                },
            },
            "SKILL": {
                "score": skill,
                "breakdown": {
                    "skill_count": skill_count,
                    "structure": structure,
                    "usage": usage,
                },
            },
            "SPAN": {
                "score": span,
                "breakdown": {
                    "project": project,
                    "migration": migration,
                    "collaboration": collaboration,
                },
            },
            "REL": {
                "score": rel,
                "breakdown": {
                    "pass": passed,
                    "fixes": fixes_score,
                    "honesty": honesty_score,
                },
            },
        },
        "composite": composite,
        "intelligence": intelligence,
        "reasoning_depth": reasoning,
        "xp": xp,
        "xp_breakdown": {
            "skills": 100 * len(skills),
            "domains": 80 * len(domains),
            "goals_done": 40 * goals_done,
            "deliveries": 25 * deliveries,
            "m": m,
        },
        "level": level_info["level"],
        "title": level_info["title"],
        "current_threshold": level_info["current_threshold"],
        "next_threshold": level_info["next_threshold"],
        "xp_to_next": level_info["xp_to_next"],
        "estimated_fields": list(profile.get("estimated", []) or []),
    }
