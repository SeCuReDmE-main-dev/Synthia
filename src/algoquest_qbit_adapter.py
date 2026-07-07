"""AlgoQuest/Qbit Education adapter hook for Synthia.

This hook is intentionally dry-run and secret-blind. Gateway owns auth.
"""

APP_SLUG = "synthia"
HUB_SLUG = "algoquest"


def build_learning_event_stub(artifact_ref: str, *, score: float = 93) -> dict:
    return {
        "schema": "securedme.education.student-learning-event.v1",
        "app_slug": APP_SLUG,
        "artifact_ref": artifact_ref,
        "skill_area": "synthia_systems_reasoning",
        "difficulty_band": "beginner",
        "score": score,
        "threshold": 93,
        "attempt_count": 1,
        "blocked_reason": "",
        "next_step_hint": "Open AlgoQuest for a guided systems reasoning reflection.",
        "qbit_help_accepted": False,
        "risk_flags": [],
        "contract_version": "v1",
        "raw_secret_stored": False,
        "dry_run": True,
    }
