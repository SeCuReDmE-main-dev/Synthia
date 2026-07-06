"""Professor-facing Synthia platform contracts and guarded route handlers.

This module keeps the school-tool boundary explicit: Synthia supports teacher
judgment with minimized FNP-QNN summaries, evidence links, privacy controls,
and human-reviewed intervention workflows. It does not create grades,
sanctions, or automated-only educational decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Iterable


class Role(str, Enum):
    PROFESSOR = "professor"
    STUDENT = "student"
    PRIVACY_ADMIN = "privacy_admin"
    SCHOOL_ADMIN = "school_admin"


class ConsentStatus(str, Enum):
    ACTIVE = "active"
    WITHDRAWN = "withdrawn"


class EfvpStatus(str, Enum):
    READY = "ready"
    DRAFT = "draft"
    BLOCKED = "blocked"


class SupportPriority(str, Enum):
    ON_TRACK = "on_track"
    APPROACHING = "approaching"
    NEEDS_SUPPORT = "needs_support"


@dataclass(frozen=True)
class UserContext:
    user_id: str
    role: Role
    assigned_class_ids: tuple[str, ...] = ()
    student_id: str | None = None


@dataclass(frozen=True)
class FnpQnnInteractionSignal:
    signal_id: str
    student_id: str
    class_id: str
    concept: str
    summary: str
    evidence_id: str
    mastery: float
    effort: float
    confusion: float
    confidence: float
    observed_at: str
    purpose: str = "learning_support"


@dataclass(frozen=True)
class ConceptUnderstanding:
    concept: str
    mastery: float
    effort: float
    confusion: float
    confidence: float


@dataclass(frozen=True)
class StudentLearningSummary:
    student_id: str
    class_id: str
    display_name: str
    grade_level: str
    support_priority: SupportPriority
    concepts: tuple[ConceptUnderstanding, ...]
    evidence_ids: tuple[str, ...]
    recommendation: str
    confidence: float
    human_review_required: bool
    ai_limitations: str
    creates_grade_or_sanction: bool = False


@dataclass(frozen=True)
class TeacherObservation:
    observation_id: str
    student_id: str
    class_id: str
    professor_id: str
    note: str
    purpose: str
    sensitivity: str
    created_at: str


@dataclass(frozen=True)
class InterventionPlan:
    intervention_id: str
    student_id: str
    class_id: str
    professor_id: str
    focus_area: str
    goal: str
    actions: tuple[str, ...]
    success_indicators: tuple[str, ...]
    follow_up_at: str
    human_validated: bool
    status: str = "draft"
    created_at: str = ""


@dataclass(frozen=True)
class ConsentRecord:
    student_id: str
    status: ConsentStatus
    allowed_purposes: tuple[str, ...]
    withdrawn_purposes: tuple[str, ...] = ()
    access_path: str = "/privacy/access-request"
    rectification_path: str = "/privacy/rectification"
    export_path: str = "/privacy/export"
    complaint_path: str = "/privacy/complaint"
    withdrawal_path: str = "/privacy/withdraw-consent"


@dataclass(frozen=True)
class DataCategoryPolicy:
    category: str
    purpose: str
    sensitivity: str
    retention: str
    leaves_quebec: bool
    written_agreement_required: bool


@dataclass(frozen=True)
class EfvpRecord:
    efvp_id: str
    status: EfvpStatus
    privacy_responsible_role: str
    cloud_enabled: bool
    cross_border_transfer_allowed: bool
    highest_privacy_by_default: bool
    data_categories: tuple[DataCategoryPolicy, ...]
    reviewed_at: str
    legal_review_required: bool = True


@dataclass(frozen=True)
class AuditEvent:
    event_id: str
    actor_id: str
    actor_role: Role
    action: str
    route: str
    subject_id: str
    purpose: str
    timestamp: str
    detail: str


@dataclass(frozen=True)
class StudentTransparencyView:
    student_id: str
    shared_fields: tuple[str, ...]
    purposes: tuple[str, ...]
    evidence_count: int
    latest_summary: str
    correction_path: str
    export_path: str
    intervention_summaries: tuple[str, ...] = ()


@dataclass(frozen=True)
class HumanReviewDecision:
    decision_id: str
    intervention_id: str
    reviewer_id: str
    approved: bool
    rationale: str
    automated_only: bool = False


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _event_id(index: int) -> str:
    return f"audit-{index:04d}"


class ProfessorPlatformService:
    """In-memory professor platform route layer for UI and contract tests."""

    api_routes = {
        "class_learning_map": "/classes/:id/learning-map",
        "student_synthesis": "/students/:id/synthesis",
        "student_evidence": "/students/:id/evidence",
        "interventions": "/interventions",
        "teacher_notes": "/teacher-notes",
        "privacy_consents": "/privacy/consents",
        "efvp_status": "/privacy/efvp-status",
        "audit_events": "/audit-events",
        "student_export": "/exports/student/:id",
    }

    def __init__(self) -> None:
        self.class_ids = {"sci10-a", "sci10-b"}
        self.class_students = {
            "sci10-a": ("stu-alex", "stu-sara", "stu-jason"),
            "sci10-b": ("stu-maya",),
        }
        self.signals = _seed_signals()
        self.summaries = _seed_summaries()
        self.consents = _seed_consents()
        self.efvp = _seed_efvp()
        self.teacher_notes: list[TeacherObservation] = []
        self.interventions: list[InterventionPlan] = []
        self.audit_log: list[AuditEvent] = []

    def get_class_learning_map(self, class_id: str, user: UserContext) -> dict[str, object]:
        self._authorize_class(class_id, user, route=self.api_routes["class_learning_map"])
        students = self.class_students.get(class_id, ())
        summaries = [self.summaries[student_id] for student_id in students]
        concept_map: dict[str, dict[str, float]] = {}
        for summary in summaries:
            for concept in summary.concepts:
                bucket = concept_map.setdefault(
                    concept.concept,
                    {"mastery": 0.0, "effort": 0.0, "confusion": 0.0, "confidence": 0.0, "count": 0.0},
                )
                bucket["mastery"] += concept.mastery
                bucket["effort"] += concept.effort
                bucket["confusion"] += concept.confusion
                bucket["confidence"] += concept.confidence
                bucket["count"] += 1.0

        averaged = {
            concept: {
                key: round(value / values["count"], 3)
                for key, value in values.items()
                if key != "count"
            }
            for concept, values in concept_map.items()
        }
        priorities = [
            {
                "student_id": summary.student_id,
                "display_name": summary.display_name,
                "support_priority": summary.support_priority.value,
                "why": summary.recommendation,
                "human_review_required": summary.human_review_required,
            }
            for summary in summaries
            if summary.support_priority != SupportPriority.ON_TRACK
        ]
        self._audit(user, "class_learning_map.read", self.api_routes["class_learning_map"], class_id, "learning_support")
        return {
            "class_id": class_id,
            "student_count": len(students),
            "support_priorities": priorities,
            "concept_mastery": averaged,
            "fnp_qnn_boundary": "Synthia receives minimized FNP-QNN summaries unless explicit evidence review is needed.",
        }

    def get_student_synthesis(self, student_id: str, user: UserContext) -> StudentLearningSummary:
        summary = self._authorized_student_summary(student_id, user, self.api_routes["student_synthesis"])
        self._audit(user, "student_synthesis.read", self.api_routes["student_synthesis"], student_id, "learning_support")
        return summary

    def get_student_evidence(self, student_id: str, user: UserContext) -> tuple[FnpQnnInteractionSignal, ...]:
        summary = self._authorized_student_summary(student_id, user, self.api_routes["student_evidence"])
        evidence = tuple(signal for signal in self.signals if signal.evidence_id in summary.evidence_ids)
        self._audit(user, "student_evidence.read", self.api_routes["student_evidence"], student_id, "evidence_review")
        return evidence

    def create_intervention(self, plan: InterventionPlan, user: UserContext) -> InterventionPlan:
        self._authorize_class(plan.class_id, user, route=self.api_routes["interventions"])
        self._ensure_professor(user, self.api_routes["interventions"])
        self._ensure_consent(plan.student_id, "intervention_support")
        if not plan.human_validated:
            raise ValueError("interventions require human professor validation before saving")
        if _contains_disallowed_educational_decision(plan.actions) or _contains_disallowed_educational_decision((plan.goal,)):
            raise ValueError("Synthia cannot create grades, sanctions, or disciplinary decisions")
        saved = InterventionPlan(
            intervention_id=plan.intervention_id,
            student_id=plan.student_id,
            class_id=plan.class_id,
            professor_id=user.user_id,
            focus_area=plan.focus_area,
            goal=plan.goal,
            actions=plan.actions,
            success_indicators=plan.success_indicators,
            follow_up_at=plan.follow_up_at,
            human_validated=True,
            status="validated",
            created_at=plan.created_at or _now(),
        )
        self.interventions.append(saved)
        self._audit(user, "intervention.validated", self.api_routes["interventions"], plan.student_id, "intervention_support")
        return saved

    def create_teacher_note(
        self,
        student_id: str,
        class_id: str,
        note: str,
        purpose: str,
        user: UserContext,
        sensitivity: str = "moderate",
    ) -> TeacherObservation:
        self._authorize_class(class_id, user, route=self.api_routes["teacher_notes"])
        self._ensure_professor(user, self.api_routes["teacher_notes"])
        self._ensure_consent(student_id, purpose)
        observation = TeacherObservation(
            observation_id=f"obs-{len(self.teacher_notes) + 1:03d}",
            student_id=student_id,
            class_id=class_id,
            professor_id=user.user_id,
            note=note,
            purpose=purpose,
            sensitivity=sensitivity,
            created_at=_now(),
        )
        self.teacher_notes.append(observation)
        self._audit(user, "teacher_note.created", self.api_routes["teacher_notes"], student_id, purpose)
        return observation

    def list_consents(self, user: UserContext) -> tuple[ConsentRecord, ...]:
        if user.role not in {Role.PRIVACY_ADMIN, Role.SCHOOL_ADMIN, Role.PROFESSOR}:
            raise PermissionError("only staff can list consent records")
        self._audit(user, "privacy_consents.read", self.api_routes["privacy_consents"], "all", "privacy_governance")
        return tuple(self.consents.values())

    def get_efvp_status(self, user: UserContext) -> EfvpRecord:
        if user.role not in {Role.PRIVACY_ADMIN, Role.SCHOOL_ADMIN, Role.PROFESSOR}:
            raise PermissionError("only staff can read EFVP status")
        self._audit(user, "efvp_status.read", self.api_routes["efvp_status"], self.efvp.efvp_id, "privacy_governance")
        return self.efvp

    def list_audit_events(self, user: UserContext) -> tuple[AuditEvent, ...]:
        if user.role not in {Role.PRIVACY_ADMIN, Role.SCHOOL_ADMIN}:
            raise PermissionError("audit timeline is limited to privacy or school admins")
        self._audit(user, "audit_events.read", self.api_routes["audit_events"], "all", "privacy_governance")
        return tuple(self.audit_log)

    def get_student_transparency(self, student_id: str, user: UserContext) -> StudentTransparencyView:
        if user.role == Role.STUDENT and user.student_id != student_id:
            raise PermissionError("students can only view their own Synthia transparency page")
        if user.role != Role.STUDENT:
            self._authorized_student_summary(student_id, user, "/student-transparency")
        summary = self.summaries[student_id]
        interventions = tuple(
            f"{item.focus_area}: {item.goal}" for item in self.interventions if item.student_id == student_id
        )
        self._audit(user, "student_transparency.read", "/student-transparency", student_id, "student_transparency")
        return StudentTransparencyView(
            student_id=student_id,
            shared_fields=("concept_progress", "support_priority", "evidence_count", "teacher_validated_interventions"),
            purposes=("learning_support", "intervention_support", "student_transparency"),
            evidence_count=len(summary.evidence_ids),
            latest_summary=summary.recommendation,
            correction_path="/privacy/rectification",
            export_path=f"/exports/student/{student_id}",
            intervention_summaries=interventions,
        )

    def export_student_data(self, student_id: str, user: UserContext) -> dict[str, object]:
        if user.role == Role.STUDENT and user.student_id != student_id:
            raise PermissionError("students can only export their own data")
        if user.role != Role.STUDENT:
            self._authorized_student_summary(student_id, user, self.api_routes["student_export"])
        summary = self.summaries[student_id]
        consent = self.consents[student_id]
        transparency = self.get_student_transparency(student_id, user)
        self._audit(user, "student_export.created", self.api_routes["student_export"], student_id, "student_access_export")
        return {
            "student_id": student_id,
            "summary": {
                "display_name": summary.display_name,
                "grade_level": summary.grade_level,
                "support_priority": summary.support_priority.value,
                "concepts": [concept.__dict__ for concept in summary.concepts],
                "evidence_ids": list(summary.evidence_ids),
                "ai_limitations": summary.ai_limitations,
                "human_review_required": summary.human_review_required,
            },
            "consent": {
                "status": consent.status.value,
                "allowed_purposes": list(consent.allowed_purposes),
                "withdrawn_purposes": list(consent.withdrawn_purposes),
            },
            "transparency": transparency.__dict__,
            "raw_fnp_qnn_messages_included": False,
        }

    def withdraw_consent(self, student_id: str, purpose: str) -> ConsentRecord:
        current = self.consents[student_id]
        allowed = tuple(item for item in current.allowed_purposes if item != purpose)
        withdrawn = tuple(dict.fromkeys((*current.withdrawn_purposes, purpose)))
        updated = ConsentRecord(
            student_id=student_id,
            status=ConsentStatus.WITHDRAWN if not allowed else ConsentStatus.ACTIVE,
            allowed_purposes=allowed,
            withdrawn_purposes=withdrawn,
            access_path=current.access_path,
            rectification_path=current.rectification_path,
            export_path=current.export_path,
            complaint_path=current.complaint_path,
            withdrawal_path=current.withdrawal_path,
        )
        self.consents[student_id] = updated
        return updated

    def _authorized_student_summary(
        self,
        student_id: str,
        user: UserContext,
        route: str,
    ) -> StudentLearningSummary:
        summary = self.summaries[student_id]
        if user.role == Role.STUDENT:
            if user.student_id != student_id:
                raise PermissionError("students can only access their own Synthia view")
            return summary
        self._authorize_class(summary.class_id, user, route=route)
        return summary

    def _authorize_class(self, class_id: str, user: UserContext, route: str) -> None:
        if class_id not in self.class_ids:
            raise KeyError(f"unknown class: {class_id}")
        if user.role in {Role.PRIVACY_ADMIN, Role.SCHOOL_ADMIN}:
            return
        if user.role == Role.PROFESSOR and class_id in user.assigned_class_ids:
            return
        self._audit(user, "authorization.denied", route, class_id, "access_control")
        raise PermissionError(f"{user.role.value} is not authorized for class {class_id}")

    @staticmethod
    def _ensure_professor(user: UserContext, route: str) -> None:
        if user.role != Role.PROFESSOR:
            raise PermissionError(f"{route} requires a professor context")

    def _ensure_consent(self, student_id: str, purpose: str) -> None:
        consent = self.consents[student_id]
        if purpose not in consent.allowed_purposes or purpose in consent.withdrawn_purposes:
            raise PermissionError(f"purpose {purpose} is not currently allowed for {student_id}")

    def _audit(self, user: UserContext, action: str, route: str, subject_id: str, purpose: str, detail: str = "") -> None:
        self.audit_log.append(
            AuditEvent(
                event_id=_event_id(len(self.audit_log) + 1),
                actor_id=user.user_id,
                actor_role=user.role,
                action=action,
                route=route,
                subject_id=subject_id,
                purpose=purpose,
                timestamp=_now(),
                detail=detail or "Synthia professor platform guarded route",
            )
        )


def _contains_disallowed_educational_decision(actions: Iterable[str]) -> bool:
    disallowed = ("grade", "mark as failed", "fail the student", "sanction", "discipline", "suspend", "punish")
    return any(any(token in action.lower() for token in disallowed) for action in actions)


def _seed_signals() -> tuple[FnpQnnInteractionSignal, ...]:
    return (
        FnpQnnInteractionSignal(
            signal_id="sig-001",
            student_id="stu-alex",
            class_id="sci10-a",
            concept="Energy Transformations",
            summary="FNP-QNN summary shows correct vocabulary but unstable transfer to real-world efficiency examples.",
            evidence_id="ev-alex-energy-summary",
            mastery=0.48,
            effort=0.83,
            confusion=0.62,
            confidence=0.74,
            observed_at="2026-07-05T14:20:00Z",
        ),
        FnpQnnInteractionSignal(
            signal_id="sig-002",
            student_id="stu-alex",
            class_id="sci10-a",
            concept="Data Literacy",
            summary="Exit ticket indicates graph interpretation improves when examples are annotated.",
            evidence_id="ev-alex-exit-ticket",
            mastery=0.58,
            effort=0.77,
            confusion=0.45,
            confidence=0.68,
            observed_at="2026-07-05T15:05:00Z",
        ),
        FnpQnnInteractionSignal(
            signal_id="sig-003",
            student_id="stu-sara",
            class_id="sci10-a",
            concept="Chemical Reactions",
            summary="Partial understanding of reaction evidence; asks for visual checks before symbolic notation.",
            evidence_id="ev-sara-reactions",
            mastery=0.64,
            effort=0.71,
            confusion=0.38,
            confidence=0.7,
            observed_at="2026-07-05T13:40:00Z",
        ),
        FnpQnnInteractionSignal(
            signal_id="sig-004",
            student_id="stu-jason",
            class_id="sci10-a",
            concept="Forces and Motion",
            summary="Consistent calculation path, but inconsistent interpretation of units in multi-step problems.",
            evidence_id="ev-jason-motion",
            mastery=0.61,
            effort=0.69,
            confusion=0.44,
            confidence=0.66,
            observed_at="2026-07-05T12:55:00Z",
        ),
        FnpQnnInteractionSignal(
            signal_id="sig-005",
            student_id="stu-maya",
            class_id="sci10-b",
            concept="Cell Structure and Function",
            summary="Stable concept map and accurate use of function vocabulary.",
            evidence_id="ev-maya-cell",
            mastery=0.82,
            effort=0.74,
            confusion=0.18,
            confidence=0.79,
            observed_at="2026-07-05T12:05:00Z",
        ),
    )


def _seed_summaries() -> dict[str, StudentLearningSummary]:
    return {
        "stu-alex": StudentLearningSummary(
            student_id="stu-alex",
            class_id="sci10-a",
            display_name="Alex M.",
            grade_level="Grade 10",
            support_priority=SupportPriority.NEEDS_SUPPORT,
            concepts=(
                ConceptUnderstanding("Energy Transformations", 0.48, 0.83, 0.62, 0.74),
                ConceptUnderstanding("Data Literacy", 0.58, 0.77, 0.45, 0.68),
            ),
            evidence_ids=("ev-alex-energy-summary", "ev-alex-exit-ticket"),
            recommendation="Review energy efficiency with annotated examples before the next lab.",
            confidence=0.73,
            human_review_required=True,
            ai_limitations="Synthesis is based on minimized FNP-QNN summaries and must be checked by the professor.",
        ),
        "stu-sara": StudentLearningSummary(
            student_id="stu-sara",
            class_id="sci10-a",
            display_name="Sara N.",
            grade_level="Grade 10",
            support_priority=SupportPriority.APPROACHING,
            concepts=(ConceptUnderstanding("Chemical Reactions", 0.64, 0.71, 0.38, 0.7),),
            evidence_ids=("ev-sara-reactions",),
            recommendation="Use visual reaction evidence before symbolic notation.",
            confidence=0.7,
            human_review_required=True,
            ai_limitations="Synthia cannot infer motivation or ability from a single trace.",
        ),
        "stu-jason": StudentLearningSummary(
            student_id="stu-jason",
            class_id="sci10-a",
            display_name="Jason L.",
            grade_level="Grade 10",
            support_priority=SupportPriority.APPROACHING,
            concepts=(ConceptUnderstanding("Forces and Motion", 0.61, 0.69, 0.44, 0.66),),
            evidence_ids=("ev-jason-motion",),
            recommendation="Check unit interpretation in multi-step force problems.",
            confidence=0.66,
            human_review_required=True,
            ai_limitations="Signal is a support priority, not a disciplinary or grading action.",
        ),
        "stu-maya": StudentLearningSummary(
            student_id="stu-maya",
            class_id="sci10-b",
            display_name="Maya P.",
            grade_level="Grade 10",
            support_priority=SupportPriority.ON_TRACK,
            concepts=(ConceptUnderstanding("Cell Structure and Function", 0.82, 0.74, 0.18, 0.79),),
            evidence_ids=("ev-maya-cell",),
            recommendation="Continue current practice and offer extension examples.",
            confidence=0.79,
            human_review_required=True,
            ai_limitations="Progress support only; professor remains the authority.",
        ),
    }


def _seed_consents() -> dict[str, ConsentRecord]:
    purposes = ("learning_support", "evidence_review", "intervention_support", "student_transparency", "student_access_export")
    return {
        student_id: ConsentRecord(student_id=student_id, status=ConsentStatus.ACTIVE, allowed_purposes=purposes)
        for student_id in ("stu-alex", "stu-sara", "stu-jason", "stu-maya")
    }


def _seed_efvp() -> EfvpRecord:
    return EfvpRecord(
        efvp_id="efvp-synthia-professor-cockpit-001",
        status=EfvpStatus.READY,
        privacy_responsible_role="School privacy officer",
        cloud_enabled=True,
        cross_border_transfer_allowed=False,
        highest_privacy_by_default=True,
        reviewed_at="2026-07-05",
        data_categories=(
            DataCategoryPolicy("learning_traces", "learning_support", "moderate", "school-year plus review window", False, True),
            DataCategoryPolicy("messages", "intervention_support", "sensitive", "school-year plus review window", False, True),
            DataCategoryPolicy("grades", "display-only context", "sensitive", "source system retention", False, True),
            DataCategoryPolicy("teacher_notes", "professional_observation", "sensitive", "school policy retention", False, True),
            DataCategoryPolicy("ai_summaries", "learning_support", "moderate", "refresh when source evidence changes", False, True),
        ),
    )
