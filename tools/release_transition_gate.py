#!/usr/bin/env python3
from __future__ import annotations

from datetime import date
from typing import Any


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def transition_state(transition: dict[str, Any], as_of: date) -> dict[str, Any]:
    pending = transition.get("upcoming_state")
    gate = transition.get("ingestion_gate", {})
    authorized = gate.get("candidate_authorization") is True
    scheduled = parse_date(transition.get("scheduled_release_date"))

    if not pending:
        state = "CURRENT_STABLE_NO_PENDING_TRANSITION"
    elif authorized:
        state = "CANDIDATE_AUTHORIZED_BY_OFFICIAL_RECHECK"
    elif scheduled and as_of < scheduled:
        state = "HOLD_CURRENT_PRE_RELEASE"
    elif scheduled and as_of >= scheduled:
        state = "OFFICIAL_RECHECK_REQUIRED"
    else:
        state = "HOLD_CURRENT_RELEASE_DATE_UNKNOWN"

    return {
        "transition_id": transition.get("id"),
        "factions": list(transition.get("factions", [])),
        "current_legal_state": transition.get("current_legal_state"),
        "upcoming_state": pending,
        "scheduled_release_date": transition.get("scheduled_release_date"),
        "candidate_authorization": authorized,
        "state": state,
        "auto_promote": False,
        "rule": "A date can trigger an official recheck but cannot itself authorize promotion.",
    }


def evaluate_release_state(release_state: dict[str, Any], as_of: date) -> dict[str, Any]:
    rows = [transition_state(x, as_of) for x in release_state.get("transitions", [])]
    blocked = sorted({
        faction
        for row in rows
        if row["upcoming_state"] and not row["candidate_authorization"]
        for faction in row["factions"]
    })
    due = [x for x in rows if x["state"] == "OFFICIAL_RECHECK_REQUIRED"]
    authorized = [x for x in rows if x["state"] == "CANDIDATE_AUTHORIZED_BY_OFFICIAL_RECHECK"]
    return {
        "as_of": as_of.isoformat(),
        "transitions": rows,
        "blocked_factions": blocked,
        "official_rechecks_due": len(due),
        "authorized_pending_transitions": len(authorized),
        "auto_promote": False,
    }


def promotion_blockers(
    release_state: dict[str, Any],
    affected_factions: list[str] | set[str],
    as_of: date,
) -> list[dict[str, Any]]:
    affected = set(affected_factions)
    blockers = []
    for transition in release_state.get("transitions", []):
        row = transition_state(transition, as_of)
        overlap = sorted(affected & set(row["factions"]))
        if not overlap or not row["upcoming_state"] or row["candidate_authorization"]:
            continue
        blockers.append({
            "transition_id": row["transition_id"],
            "affected_factions": overlap,
            "state": row["state"],
            "scheduled_release_date": row["scheduled_release_date"],
            "reason": (
                "Affected roster identities are inside an active release transition. "
                "Official release/currentness evidence must explicitly authorize candidate promotion."
            ),
        })
    return blockers
