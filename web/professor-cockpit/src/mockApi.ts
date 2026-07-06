import {
  buildTransparencyView,
  consentRecords,
  defaultIntervention,
  efvpRecord,
  evidenceSignals,
  initialAuditEvents,
  routeManifest,
  students
} from './platformData';
import type {
  AuditEvent,
  ConsentRecord,
  EfvpRecord,
  FnpQnnInteractionSignal,
  InterventionPlan,
  StudentLearningSummary,
  StudentTransparencyView,
  UserRole
} from './types';

export interface AppState {
  students: StudentLearningSummary[];
  evidenceSignals: FnpQnnInteractionSignal[];
  interventions: InterventionPlan[];
  consents: ConsentRecord[];
  efvp: EfvpRecord;
  auditEvents: AuditEvent[];
}

export interface UserContext {
  userId: string;
  role: UserRole;
  assignedClassIds: string[];
  studentId?: string;
}

export const professorContext: UserContext = {
  userId: 'prof-marie',
  role: 'Professor',
  assignedClassIds: ['sci10-a']
};

export const createInitialState = (): AppState => ({
  students,
  evidenceSignals,
  interventions: [],
  consents: consentRecords,
  efvp: efvpRecord,
  auditEvents: initialAuditEvents
});

export const audit = (
  state: AppState,
  user: UserContext,
  action: string,
  route: string,
  subjectId: string,
  purpose: string,
  detail: string
): AppState => ({
  ...state,
  auditEvents: [
    {
      eventId: `audit-${String(state.auditEvents.length + 1).padStart(4, '0')}`,
      actorId: user.userId,
      actorRole: user.role,
      action,
      route,
      subjectId,
      purpose,
      timestamp: new Date().toISOString(),
      detail
    },
    ...state.auditEvents
  ]
});

export const getClassLearningMap = (state: AppState, classId: string, user: UserContext) => {
  assertClassAccess(classId, user);
  const roster = state.students.filter((student) => student.classId === classId);
  const conceptNames = Array.from(new Set(roster.flatMap((student) => student.concepts.map((concept) => concept.concept))));
  const conceptMastery = conceptNames.map((concept) => {
    const matching = roster.flatMap((student) => student.concepts.filter((item) => item.concept === concept));
    const average = matching.reduce((sum, item) => sum + item.mastery, 0) / Math.max(1, matching.length);
    return { concept, mastery: average };
  });

  return {
    classId,
    studentCount: roster.length,
    supportPriorities: roster.filter((student) => student.supportPriority !== 'on_track'),
    conceptMastery,
    fnpQnnBoundary: 'FNP-QNN summaries minimized'
  };
};

export const getStudentSynthesis = (
  state: AppState,
  studentId: string,
  user: UserContext
): StudentLearningSummary => {
  const student = state.students.find((item) => item.studentId === studentId);
  if (!student) throw new Error(`Unknown student ${studentId}`);
  assertStudentAccess(student, user);
  return student;
};

export const getStudentEvidence = (
  state: AppState,
  studentId: string,
  user: UserContext
): FnpQnnInteractionSignal[] => {
  const student = getStudentSynthesis(state, studentId, user);
  return state.evidenceSignals.filter((signal) => student.evidenceIds.includes(signal.evidenceId));
};

export const validateAndSaveIntervention = (
  state: AppState,
  draft: InterventionPlan,
  user: UserContext
): AppState => {
  const student = getStudentSynthesis(state, draft.studentId, user);
  assertConsent(state, draft.studentId, 'intervention_support');
  if (!draft.humanValidated) {
    throw new Error('Human review is required before Synthia can save an intervention.');
  }
  if (containsGradeOrSanction([...draft.actions, draft.goal])) {
    throw new Error('Synthia cannot create grades, sanctions, discipline, or automated-only decisions.');
  }
  const saved: InterventionPlan = {
    ...draft,
    classId: student.classId,
    professorId: user.userId,
    status: 'validated'
  };
  const withIntervention = { ...state, interventions: [saved, ...state.interventions] };
  return audit(
    withIntervention,
    user,
    'intervention.validated',
    routeManifest.interventions,
    draft.studentId,
    'intervention_support',
    `${student.displayName} intervention validated by professor.`
  );
};

export const getStudentTransparency = (
  state: AppState,
  studentId: string,
  user: UserContext
): StudentTransparencyView => {
  const student = getStudentSynthesis(state, studentId, user);
  return buildTransparencyView(student, state.interventions);
};

export const exportStudentData = (state: AppState, studentId: string, user: UserContext) => {
  const student = getStudentSynthesis(state, studentId, user);
  const consent = state.consents.find((item) => item.studentId === studentId);
  return {
    studentId,
    summary: student,
    consent,
    transparency: getStudentTransparency(state, studentId, user),
    rawFnpQnnMessagesIncluded: false
  };
};

export const makeDraftForStudent = defaultIntervention;

function assertClassAccess(classId: string, user: UserContext) {
  if (user.role === 'Privacy Admin' || user.role === 'School Admin') return;
  if (user.role === 'Professor' && user.assignedClassIds.includes(classId)) return;
  throw new Error(`${user.role} is not authorized for class ${classId}`);
}

function assertStudentAccess(student: StudentLearningSummary, user: UserContext) {
  if (user.role === 'Student' && user.studentId !== student.studentId) {
    throw new Error('Students can only view their own transparency page.');
  }
  if (user.role !== 'Student') assertClassAccess(student.classId, user);
}

function assertConsent(state: AppState, studentId: string, purpose: string) {
  const consent = state.consents.find((item) => item.studentId === studentId);
  if (!consent || !consent.allowedPurposes.includes(purpose) || consent.withdrawnPurposes.includes(purpose)) {
    throw new Error(`${purpose} is not currently allowed for ${studentId}.`);
  }
}

function containsGradeOrSanction(actions: string[]) {
  const disallowed = ['grade', 'sanction', 'discipline', 'suspend', 'punish', 'fail the student'];
  return actions.some((action) => disallowed.some((token) => action.toLowerCase().includes(token)));
}
