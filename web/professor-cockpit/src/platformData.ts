import type {
  AuditEvent,
  ConsentRecord,
  EfvpRecord,
  FnpQnnInteractionSignal,
  InterventionPlan,
  RouteManifest,
  StudentLearningSummary,
  StudentTransparencyView
} from './types';

export const routeManifest: RouteManifest = {
  classLearningMap: '/classes/:id/learning-map',
  studentSynthesis: '/students/:id/synthesis',
  studentEvidence: '/students/:id/evidence',
  interventions: '/interventions',
  teacherNotes: '/teacher-notes',
  privacyConsents: '/privacy/consents',
  efvpStatus: '/privacy/efvp-status',
  auditEvents: '/audit-events',
  studentExport: '/exports/student/:id'
};

export const students: StudentLearningSummary[] = [
  {
    studentId: 'stu-alex',
    classId: 'sci10-a',
    displayName: 'Alex M.',
    initials: 'AM',
    gradeLevel: 'Grade 10',
    homeroom: 'Sec. 2',
    supportPriority: 'needs_support',
    concepts: [
      { concept: 'Energy Transformations', mastery: 0.48, effort: 0.83, confusion: 0.62, confidence: 0.74 },
      { concept: 'Data Literacy', mastery: 0.58, effort: 0.77, confusion: 0.45, confidence: 0.68 }
    ],
    evidenceIds: ['ev-alex-energy-summary', 'ev-alex-exit-ticket', 'ev-alex-lab-report'],
    recommendation: 'Review energy efficiency with annotated real-world examples before the next lab.',
    confidence: 0.73,
    humanReviewRequired: true,
    aiLimitations: 'Based on minimized FNP-QNN summaries. Professor review is required before action.',
    createsGradeOrSanction: false
  },
  {
    studentId: 'stu-sara',
    classId: 'sci10-a',
    displayName: 'Sara N.',
    initials: 'SN',
    gradeLevel: 'Grade 10',
    homeroom: 'Sec. 2',
    supportPriority: 'approaching',
    concepts: [
      { concept: 'Chemical Reactions', mastery: 0.64, effort: 0.71, confusion: 0.38, confidence: 0.7 },
      { concept: 'Cell Structure and Function', mastery: 0.72, effort: 0.68, confusion: 0.31, confidence: 0.76 }
    ],
    evidenceIds: ['ev-sara-reactions', 'ev-sara-model'],
    recommendation: 'Use visual reaction evidence before symbolic notation.',
    confidence: 0.7,
    humanReviewRequired: true,
    aiLimitations: 'Synthia cannot infer motivation or ability from a single trace.',
    createsGradeOrSanction: false
  },
  {
    studentId: 'stu-jason',
    classId: 'sci10-a',
    displayName: 'Jason L.',
    initials: 'JL',
    gradeLevel: 'Grade 10',
    homeroom: 'Sec. 2',
    supportPriority: 'approaching',
    concepts: [
      { concept: 'Forces and Motion', mastery: 0.61, effort: 0.69, confusion: 0.44, confidence: 0.66 },
      { concept: 'Data Literacy', mastery: 0.55, effort: 0.64, confusion: 0.49, confidence: 0.62 }
    ],
    evidenceIds: ['ev-jason-motion', 'ev-jason-data'],
    recommendation: 'Check unit interpretation in multi-step force problems.',
    confidence: 0.66,
    humanReviewRequired: true,
    aiLimitations: 'Signal is a support priority, not a disciplinary or grading action.',
    createsGradeOrSanction: false
  },
  {
    studentId: 'stu-maya',
    classId: 'sci10-a',
    displayName: 'Maya P.',
    initials: 'MP',
    gradeLevel: 'Grade 10',
    homeroom: 'Sec. 4',
    supportPriority: 'on_track',
    concepts: [
      { concept: 'Cell Structure and Function', mastery: 0.82, effort: 0.74, confusion: 0.18, confidence: 0.79 },
      { concept: 'Data Literacy', mastery: 0.78, effort: 0.7, confusion: 0.2, confidence: 0.81 }
    ],
    evidenceIds: ['ev-maya-cell'],
    recommendation: 'Continue current practice and offer extension examples.',
    confidence: 0.79,
    humanReviewRequired: true,
    aiLimitations: 'Progress support only; professor remains the authority.',
    createsGradeOrSanction: false
  }
];

export const evidenceSignals: FnpQnnInteractionSignal[] = [
  {
    signalId: 'sig-001',
    studentId: 'stu-alex',
    classId: 'sci10-a',
    concept: 'Energy Transformations',
    summary: 'FNP-QNN summary shows correct vocabulary but unstable transfer to real-world efficiency examples.',
    evidenceId: 'ev-alex-energy-summary',
    mastery: 0.48,
    effort: 0.83,
    confusion: 0.62,
    confidence: 0.74,
    observedAt: '2026-07-05T14:20:00Z',
    purpose: 'learning_support'
  },
  {
    signalId: 'sig-002',
    studentId: 'stu-alex',
    classId: 'sci10-a',
    concept: 'Data Literacy',
    summary: 'Exit ticket indicates graph interpretation improves when examples are annotated.',
    evidenceId: 'ev-alex-exit-ticket',
    mastery: 0.58,
    effort: 0.77,
    confusion: 0.45,
    confidence: 0.68,
    observedAt: '2026-07-05T15:05:00Z',
    purpose: 'evidence_review'
  },
  {
    signalId: 'sig-003',
    studentId: 'stu-alex',
    classId: 'sci10-a',
    concept: 'Energy Transformations',
    summary: 'Lab report includes a good observation, but the conclusion skips the efficiency step.',
    evidenceId: 'ev-alex-lab-report',
    mastery: 0.52,
    effort: 0.8,
    confusion: 0.51,
    confidence: 0.71,
    observedAt: '2026-07-04T11:10:00Z',
    purpose: 'evidence_review'
  },
  {
    signalId: 'sig-004',
    studentId: 'stu-sara',
    classId: 'sci10-a',
    concept: 'Chemical Reactions',
    summary: 'Partial understanding of reaction evidence; asks for visual checks before symbolic notation.',
    evidenceId: 'ev-sara-reactions',
    mastery: 0.64,
    effort: 0.71,
    confusion: 0.38,
    confidence: 0.7,
    observedAt: '2026-07-05T13:40:00Z',
    purpose: 'learning_support'
  },
  {
    signalId: 'sig-005',
    studentId: 'stu-jason',
    classId: 'sci10-a',
    concept: 'Forces and Motion',
    summary: 'Consistent calculation path, but inconsistent interpretation of units in multi-step problems.',
    evidenceId: 'ev-jason-motion',
    mastery: 0.61,
    effort: 0.69,
    confusion: 0.44,
    confidence: 0.66,
    observedAt: '2026-07-05T12:55:00Z',
    purpose: 'learning_support'
  }
];

export const efvpRecord: EfvpRecord = {
  efvpId: 'efvp-synthia-professor-cockpit-001',
  status: 'ready',
  privacyResponsibleRole: 'School privacy officer',
  cloudEnabled: true,
  crossBorderTransferAllowed: false,
  highestPrivacyByDefault: true,
  reviewedAt: '2026-07-05',
  legalReviewRequired: true,
  dataCategories: [
    {
      category: 'learning_traces',
      purpose: 'learning_support',
      sensitivity: 'moderate',
      retention: 'school-year plus review window',
      leavesQuebec: false,
      writtenAgreementRequired: true
    },
    {
      category: 'messages',
      purpose: 'intervention_support',
      sensitivity: 'sensitive',
      retention: 'school-year plus review window',
      leavesQuebec: false,
      writtenAgreementRequired: true
    },
    {
      category: 'grades',
      purpose: 'display-only context',
      sensitivity: 'sensitive',
      retention: 'source system retention',
      leavesQuebec: false,
      writtenAgreementRequired: true
    },
    {
      category: 'teacher_notes',
      purpose: 'professional_observation',
      sensitivity: 'sensitive',
      retention: 'school policy retention',
      leavesQuebec: false,
      writtenAgreementRequired: true
    },
    {
      category: 'ai_summaries',
      purpose: 'learning_support',
      sensitivity: 'moderate',
      retention: 'refresh when source evidence changes',
      leavesQuebec: false,
      writtenAgreementRequired: true
    }
  ]
};

export const consentRecords: ConsentRecord[] = students.map((student) => ({
  studentId: student.studentId,
  status: 'active',
  allowedPurposes: ['learning_support', 'evidence_review', 'intervention_support', 'student_transparency', 'student_access_export'],
  withdrawnPurposes: [],
  paths: {
    access: '/privacy/access-request',
    rectification: '/privacy/rectification',
    export: `/exports/student/${student.studentId}`,
    complaint: '/privacy/complaint',
    withdraw: '/privacy/withdraw-consent'
  }
}));

export const initialAuditEvents: AuditEvent[] = [
  {
    eventId: 'audit-0001',
    actorId: 'prof-marie',
    actorRole: 'Professor',
    action: 'student_synthesis.read',
    route: routeManifest.studentSynthesis,
    subjectId: 'stu-alex',
    purpose: 'learning_support',
    timestamp: '2026-07-05T10:42:00Z',
    detail: 'Alex M. synthesis opened for human review.'
  },
  {
    eventId: 'audit-0002',
    actorId: 'prof-marie',
    actorRole: 'Professor',
    action: 'student_evidence.read',
    route: routeManifest.studentEvidence,
    subjectId: 'stu-alex',
    purpose: 'evidence_review',
    timestamp: '2026-07-05T10:45:00Z',
    detail: 'Evidence drawer opened.'
  },
  {
    eventId: 'audit-0003',
    actorId: 'privacy-lead',
    actorRole: 'Privacy Admin',
    action: 'efvp_status.read',
    route: routeManifest.efvpStatus,
    subjectId: efvpRecord.efvpId,
    purpose: 'privacy_governance',
    timestamp: '2026-07-05T11:08:00Z',
    detail: 'EFVP status reviewed before cloud activation.'
  }
];

export const defaultIntervention = (student: StudentLearningSummary): InterventionPlan => ({
  interventionId: `int-${student.studentId}-${Date.now()}`,
  studentId: student.studentId,
  classId: student.classId,
  professorId: 'prof-marie',
  focusArea: student.concepts[0]?.concept ?? 'Concept review',
  goal: student.recommendation,
  actions: ['Mini-lesson with annotated examples', 'Guided practice with professor check-in', 'Small group problem-solving'],
  successIndicators: ['Student can explain the concept using examples', 'Student can solve a multi-step practice item'],
  followUpAt: '2026-07-12',
  humanValidated: false,
  status: 'draft'
});

export const buildTransparencyView = (
  student: StudentLearningSummary,
  interventions: InterventionPlan[]
): StudentTransparencyView => ({
  studentId: student.studentId,
  sharedFields: ['concept_progress', 'support_priority', 'evidence_count', 'teacher_validated_interventions'],
  purposes: ['learning_support', 'intervention_support', 'student_transparency'],
  evidenceCount: student.evidenceIds.length,
  latestSummary: student.recommendation,
  correctionPath: '/privacy/rectification',
  exportPath: `/exports/student/${student.studentId}`,
  interventionSummaries: interventions
    .filter((item) => item.studentId === student.studentId && item.status === 'validated')
    .map((item) => `${item.focusArea}: ${item.goal}`)
});
