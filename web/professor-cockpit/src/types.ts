export type UserRole = 'Professor' | 'Student' | 'Privacy Admin' | 'School Admin';

export type SupportPriority = 'on_track' | 'approaching' | 'needs_support';

export interface FnpQnnInteractionSignal {
  signalId: string;
  studentId: string;
  classId: string;
  concept: string;
  summary: string;
  evidenceId: string;
  mastery: number;
  effort: number;
  confusion: number;
  confidence: number;
  observedAt: string;
  purpose: 'learning_support' | 'evidence_review';
}

export interface ConceptUnderstanding {
  concept: string;
  mastery: number;
  effort: number;
  confusion: number;
  confidence: number;
}

export interface StudentLearningSummary {
  studentId: string;
  classId: string;
  displayName: string;
  initials: string;
  gradeLevel: string;
  homeroom: string;
  supportPriority: SupportPriority;
  concepts: ConceptUnderstanding[];
  evidenceIds: string[];
  recommendation: string;
  confidence: number;
  humanReviewRequired: boolean;
  aiLimitations: string;
  createsGradeOrSanction: false;
}

export interface TeacherObservation {
  observationId: string;
  studentId: string;
  professorId: string;
  note: string;
  purpose: string;
  sensitivity: 'moderate' | 'sensitive';
  createdAt: string;
}

export interface InterventionPlan {
  interventionId: string;
  studentId: string;
  classId: string;
  professorId: string;
  focusArea: string;
  goal: string;
  actions: string[];
  successIndicators: string[];
  followUpAt: string;
  humanValidated: boolean;
  status: 'draft' | 'validated';
}

export interface ConsentRecord {
  studentId: string;
  status: 'active' | 'withdrawn';
  allowedPurposes: string[];
  withdrawnPurposes: string[];
  paths: {
    access: string;
    rectification: string;
    export: string;
    complaint: string;
    withdraw: string;
  };
}

export interface EfvpRecord {
  efvpId: string;
  status: 'ready' | 'draft' | 'blocked';
  privacyResponsibleRole: string;
  cloudEnabled: boolean;
  crossBorderTransferAllowed: boolean;
  highestPrivacyByDefault: boolean;
  dataCategories: DataCategoryPolicy[];
  reviewedAt: string;
  legalReviewRequired: boolean;
}

export interface DataCategoryPolicy {
  category: string;
  purpose: string;
  sensitivity: 'low' | 'moderate' | 'sensitive';
  retention: string;
  leavesQuebec: boolean;
  writtenAgreementRequired: boolean;
}

export interface AuditEvent {
  eventId: string;
  actorId: string;
  actorRole: UserRole;
  action: string;
  route: string;
  subjectId: string;
  purpose: string;
  timestamp: string;
  detail: string;
}

export interface StudentTransparencyView {
  studentId: string;
  sharedFields: string[];
  purposes: string[];
  evidenceCount: number;
  latestSummary: string;
  correctionPath: string;
  exportPath: string;
  interventionSummaries: string[];
}

export interface HumanReviewDecision {
  decisionId: string;
  interventionId: string;
  reviewerId: string;
  approved: boolean;
  rationale: string;
  automatedOnly: false;
}

export interface RouteManifest {
  classLearningMap: '/classes/:id/learning-map';
  studentSynthesis: '/students/:id/synthesis';
  studentEvidence: '/students/:id/evidence';
  interventions: '/interventions';
  teacherNotes: '/teacher-notes';
  privacyConsents: '/privacy/consents';
  efvpStatus: '/privacy/efvp-status';
  auditEvents: '/audit-events';
  studentExport: '/exports/student/:id';
}
