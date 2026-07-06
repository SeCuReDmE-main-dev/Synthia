import pytest

from synthia_core.professor_platform import (
    InterventionPlan,
    ProfessorPlatformService,
    Role,
    UserContext,
)


def professor() -> UserContext:
    return UserContext(user_id="prof-marie", role=Role.PROFESSOR, assigned_class_ids=("sci10-a",))


def privacy_admin() -> UserContext:
    return UserContext(user_id="privacy-lead", role=Role.PRIVACY_ADMIN)


def student(student_id: str) -> UserContext:
    return UserContext(user_id=f"user-{student_id}", role=Role.STUDENT, student_id=student_id)


def valid_intervention(student_id: str = "stu-alex") -> InterventionPlan:
    return InterventionPlan(
        intervention_id="int-test-001",
        student_id=student_id,
        class_id="sci10-a",
        professor_id="prof-marie",
        focus_area="Energy Transformations",
        goal="Strengthen real-world examples before the next lab.",
        actions=("Mini-lesson with annotated examples", "Check-in after practice"),
        success_indicators=("Can explain efficiency using examples",),
        follow_up_at="2026-07-12",
        human_validated=True,
    )


def test_professor_cannot_access_unauthorized_classes():
    service = ProfessorPlatformService()

    with pytest.raises(PermissionError):
        service.get_class_learning_map("sci10-b", professor())


def test_student_sees_only_their_own_transparency_view():
    service = ProfessorPlatformService()

    own_view = service.get_student_transparency("stu-alex", student("stu-alex"))
    assert own_view.student_id == "stu-alex"

    with pytest.raises(PermissionError):
        service.get_student_transparency("stu-sara", student("stu-alex"))


def test_every_synthesis_links_to_evidence():
    service = ProfessorPlatformService()

    summary = service.get_student_synthesis("stu-alex", professor())
    evidence = service.get_student_evidence("stu-alex", professor())

    assert summary.evidence_ids
    assert {item.evidence_id for item in evidence} == set(summary.evidence_ids)
    assert summary.human_review_required is True
    assert summary.creates_grade_or_sanction is False


def test_interventions_require_human_validation():
    service = ProfessorPlatformService()
    draft = valid_intervention()
    unvalidated = InterventionPlan(
        intervention_id=draft.intervention_id,
        student_id=draft.student_id,
        class_id=draft.class_id,
        professor_id=draft.professor_id,
        focus_area=draft.focus_area,
        goal=draft.goal,
        actions=draft.actions,
        success_indicators=draft.success_indicators,
        follow_up_at=draft.follow_up_at,
        human_validated=False,
    )

    with pytest.raises(ValueError, match="human professor validation"):
        service.create_intervention(unvalidated, professor())


def test_ai_outputs_cannot_create_grades_or_sanctions():
    service = ProfessorPlatformService()
    plan = InterventionPlan(
        intervention_id="int-bad-001",
        student_id="stu-alex",
        class_id="sci10-a",
        professor_id="prof-marie",
        focus_area="Energy Transformations",
        goal="Assign a failing grade automatically.",
        actions=("Sanction the student for confusion",),
        success_indicators=("Grade changed",),
        follow_up_at="2026-07-12",
        human_validated=True,
    )

    with pytest.raises(ValueError, match="cannot create grades"):
        service.create_intervention(plan, professor())


def test_consent_withdrawal_and_purpose_limitation():
    service = ProfessorPlatformService()
    updated = service.withdraw_consent("stu-alex", "learning_support")

    assert "learning_support" not in updated.allowed_purposes
    assert "learning_support" in updated.withdrawn_purposes

    with pytest.raises(PermissionError, match="not currently allowed"):
        service.create_teacher_note(
            student_id="stu-alex",
            class_id="sci10-a",
            note="Needs another worked example.",
            purpose="learning_support",
            user=professor(),
        )


def test_exportable_structured_student_data_excludes_raw_fnp_qnn_messages():
    service = ProfessorPlatformService()

    exported = service.export_student_data("stu-alex", student("stu-alex"))

    assert exported["student_id"] == "stu-alex"
    assert exported["raw_fnp_qnn_messages_included"] is False
    assert exported["summary"]["evidence_ids"]
    assert exported["transparency"]["correction_path"] == "/privacy/rectification"


def test_audit_logs_sensitive_actions():
    service = ProfessorPlatformService()
    user = professor()

    service.get_class_learning_map("sci10-a", user)
    service.get_student_synthesis("stu-alex", user)
    service.get_student_evidence("stu-alex", user)
    service.create_intervention(valid_intervention(), user)

    events = service.list_audit_events(privacy_admin())
    actions = {event.action for event in events}

    assert "class_learning_map.read" in actions
    assert "student_synthesis.read" in actions
    assert "student_evidence.read" in actions
    assert "intervention.validated" in actions
    assert "audit_events.read" in actions


def test_ux_acceptance_support_signal_to_validated_intervention_to_student_view():
    service = ProfessorPlatformService()
    user = professor()

    class_map = service.get_class_learning_map("sci10-a", user)
    assert any(item["student_id"] == "stu-alex" for item in class_map["support_priorities"])

    summary = service.get_student_synthesis("stu-alex", user)
    evidence = service.get_student_evidence("stu-alex", user)
    saved = service.create_intervention(valid_intervention(), user)
    student_view = service.get_student_transparency("stu-alex", student("stu-alex"))

    assert summary.display_name == "Alex M."
    assert evidence
    assert saved.status == "validated"
    assert student_view.intervention_summaries
    assert "teacher_validated_interventions" in student_view.shared_fields

