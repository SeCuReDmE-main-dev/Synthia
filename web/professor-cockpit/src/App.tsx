import {
  BookOpen,
  Boxes,
  CalendarCheck,
  Check,
  ClipboardCheck,
  Download,
  Eye,
  FileCheck2,
  GraduationCap,
  Grid2X2,
  History,
  Info,
  LifeBuoy,
  LockKeyhole,
  Menu,
  MessageSquareText,
  Search,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  UserRound,
  UsersRound,
  X
} from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';
import type { CSSProperties, KeyboardEvent as ReactKeyboardEvent, ReactNode, RefObject } from 'react';
import {
  audit,
  createInitialState,
  exportStudentData,
  getClassLearningMap,
  getStudentEvidence,
  getStudentTransparency,
  makeDraftForStudent,
  professorContext,
  validateAndSaveIntervention
} from './mockApi';
import { routeManifest } from './platformData';
import type { AppState, UserContext } from './mockApi';
import type { FnpQnnInteractionSignal, InterventionPlan, StudentLearningSummary, UserRole } from './types';

const roleOptions: { role: UserRole; icon: typeof UserRound }[] = [
  { role: 'Professor', icon: UserRound },
  { role: 'Student', icon: GraduationCap },
  { role: 'Privacy Admin', icon: ShieldCheck },
  { role: 'School Admin', icon: Boxes }
];

const teachingLinks = [
  ['Dashboard', Grid2X2],
  ['Students', UsersRound],
  ['Classes', BookOpen],
  ['Concepts', Sparkles],
  ['Interventions', LifeBuoy],
  ['Reports', ClipboardCheck]
] as const;

const governanceLinks = [
  ['Privacy Centre', LockKeyhole],
  ['EFVP Ready', FileCheck2],
  ['Audit Timeline', History],
  ['Settings', SlidersHorizontal]
] as const;

const compactNavigationQuery = '(max-width: 1080px)';

export function App() {
  const [state, setState] = useState<AppState>(() => createInitialState());
  const [activeRole, setActiveRole] = useState<UserRole>('Professor');
  const [selectedStudentId, setSelectedStudentId] = useState('stu-alex');
  const [query, setQuery] = useState('');
  const [evidenceOpen, setEvidenceOpen] = useState(false);
  const [isCompactNavigation, setIsCompactNavigation] = useState(() => window.matchMedia(compactNavigationQuery).matches);
  const [navigationOpen, setNavigationOpen] = useState(false);
  const navigationToggleRef = useRef<HTMLButtonElement>(null);
  const navigationRef = useRef<HTMLElement>(null);
  const selectedStudent = state.students.find((student) => student.studentId === selectedStudentId) ?? state.students[0];
  const [draft, setDraft] = useState<InterventionPlan>(() => makeDraftForStudent(selectedStudent));
  const currentUser = useMemo<UserContext>(() => {
    if (activeRole === 'Student') {
      return { userId: `user-${selectedStudentId}`, role: 'Student', assignedClassIds: [], studentId: selectedStudentId };
    }
    if (activeRole === 'Privacy Admin') {
      return { userId: 'privacy-lead', role: activeRole, assignedClassIds: [] };
    }
    if (activeRole === 'School Admin') {
      return { userId: 'school-admin', role: activeRole, assignedClassIds: [] };
    }
    return professorContext;
  }, [activeRole, selectedStudentId]);

  useEffect(() => {
    setDraft(makeDraftForStudent(selectedStudent));
  }, [selectedStudent.studentId]);

  useEffect(() => {
    const mediaQuery = window.matchMedia(compactNavigationQuery);
    const updateNavigationMode = () => {
      setIsCompactNavigation(mediaQuery.matches);
      if (!mediaQuery.matches) {
        setNavigationOpen(false);
      }
    };

    updateNavigationMode();
    mediaQuery.addEventListener('change', updateNavigationMode);
    return () => mediaQuery.removeEventListener('change', updateNavigationMode);
  }, []);

  useEffect(() => {
    if (!isCompactNavigation || !navigationOpen) {
      return;
    }

    navigationRef.current?.querySelector<HTMLButtonElement>('[data-cockpit-nav-close]')?.focus();
  }, [isCompactNavigation, navigationOpen]);

  const classMap = getClassLearningMap(state, 'sci10-a', professorContext);
  const classRoster = state.students.filter((student) => student.classId === 'sci10-a');
  const healthCounts = {
    onTrack: classRoster.filter((student) => student.supportPriority === 'on_track').length,
    approaching: classRoster.filter((student) => student.supportPriority === 'approaching').length,
    needsSupport: classRoster.filter((student) => student.supportPriority === 'needs_support').length,
    total: classRoster.length
  };
  const filteredStudents = state.students.filter((student) =>
    `${student.displayName} ${student.concepts.map((concept) => concept.concept).join(' ')}`
      .toLowerCase()
      .includes(query.toLowerCase())
  );
  const evidence = getStudentEvidence(state, selectedStudent.studentId, professorContext);
  const transparency = getStudentTransparency(state, selectedStudent.studentId, currentUser);
  const classHealth = Math.round((healthCounts.onTrack / Math.max(1, healthCounts.total)) * 100);

  const saveIntervention = () => {
    try {
      const nextState = validateAndSaveIntervention(state, draft, professorContext);
      setState(nextState);
      setDraft({ ...draft, status: 'validated' });
    } catch (error) {
      window.alert(error instanceof Error ? error.message : 'Unable to save intervention');
    }
  };

  const exportSelectedStudent = () => {
    const exported = exportStudentData(state, selectedStudent.studentId, currentUser);
    const next = audit(
      state,
      currentUser,
      'student_export.created',
      routeManifest.studentExport,
      selectedStudent.studentId,
      'student_access_export',
      `${selectedStudent.displayName} structured export prepared.`
    );
    setState(next);
    window.alert(`Structured export ready for ${exported.summary.displayName}. Raw FNP-QNN messages included: no.`);
  };

  const closeNavigation = (returnFocus = false) => {
    setNavigationOpen(false);
    if (returnFocus) {
      window.requestAnimationFrame(() => navigationToggleRef.current?.focus());
    }
  };

  const selectRole = (role: UserRole) => {
    setActiveRole(role);
    if (isCompactNavigation) {
      closeNavigation(true);
    }
  };

  return (
    <div className="app-shell">
      {!isCompactNavigation && <CockpitNavigation activeRole={activeRole} selectRole={selectRole} />}

      {isCompactNavigation && navigationOpen && (
        <div
          className="navigation-backdrop"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) {
              closeNavigation(true);
            }
          }}
        >
          <CockpitNavigation
            activeRole={activeRole}
            selectRole={selectRole}
            onNavigate={() => closeNavigation(true)}
            drawer
            navigationRef={navigationRef}
            closeNavigation={() => closeNavigation(true)}
          />
        </div>
      )}

      <main id="cockpit-workspace" className="workspace">
        <header className="topbar">
          <div className="workspace-heading">
            <button
              ref={navigationToggleRef}
              type="button"
              className="navigation-toggle"
              aria-controls="cockpit-navigation"
              aria-expanded={isCompactNavigation && navigationOpen}
              data-cockpit-nav-toggle
              onClick={() => (navigationOpen ? closeNavigation(true) : setNavigationOpen(true))}
            >
              {navigationOpen ? <X size={18} aria-hidden="true" /> : <Menu size={18} aria-hidden="true" />}
              <span>{navigationOpen ? 'Close navigation' : 'Navigation'}</span>
            </button>
            <h1>Synthia Professor Cockpit</h1>
            <p>Grade 10 Science / Sec. 2 / Term 2</p>
          </div>
          <label className="search-box">
            <Search size={18} />
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search students, concepts, evidence..."
            />
          </label>
          <button type="button" className="ghost-button" onClick={exportSelectedStudent}>
            <Download size={16} />
            Export Student
          </button>
        </header>

        {activeRole === 'Student' ? (
          <StudentOnlyView student={selectedStudent} transparency={transparency} evidence={evidence} />
        ) : activeRole === 'Privacy Admin' || activeRole === 'School Admin' ? (
          <GovernanceView state={state} />
        ) : (
          <ProfessorView
            classHealth={classHealth}
            healthCounts={healthCounts}
            classMap={classMap}
            students={filteredStudents}
            selectedStudent={selectedStudent}
            evidence={evidence}
            evidenceOpen={evidenceOpen}
            setEvidenceOpen={setEvidenceOpen}
            setSelectedStudentId={setSelectedStudentId}
            draft={draft}
            setDraft={setDraft}
            saveIntervention={saveIntervention}
            transparency={transparency}
            state={state}
          />
        )}
      </main>
    </div>
  );
}

interface CockpitNavigationProps {
  activeRole: UserRole;
  selectRole: (role: UserRole) => void;
  onNavigate?: () => void;
  drawer?: boolean;
  navigationRef?: RefObject<HTMLElement>;
  closeNavigation?: () => void;
}

function CockpitNavigation({
  activeRole,
  selectRole,
  onNavigate,
  drawer = false,
  navigationRef,
  closeNavigation
}: CockpitNavigationProps) {
  const handleKeyDown = (event: ReactKeyboardEvent<HTMLElement>) => {
    if (event.key === 'Escape' && closeNavigation) {
      event.preventDefault();
      closeNavigation();
      return;
    }

    if (event.key !== 'Tab' || !drawer) {
      return;
    }

    const focusableItems = Array.from(
      event.currentTarget.querySelectorAll<HTMLElement>(
        'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
      )
    );
    const firstItem = focusableItems[0];
    const lastItem = focusableItems[focusableItems.length - 1];

    if (!firstItem || !lastItem) {
      return;
    }

    if (event.shiftKey && document.activeElement === firstItem) {
      event.preventDefault();
      lastItem.focus();
    } else if (!event.shiftKey && document.activeElement === lastItem) {
      event.preventDefault();
      firstItem.focus();
    }
  };

  return (
    <aside
      ref={navigationRef}
      id={drawer ? 'cockpit-navigation' : undefined}
      className={`sidebar ${drawer ? 'sidebar--drawer' : ''}`}
      aria-label="Synthia professor navigation"
      aria-modal={drawer || undefined}
      role={drawer ? 'dialog' : undefined}
      data-cockpit-nav={drawer ? '' : undefined}
      onKeyDown={handleKeyDown}
    >
      <div className="brand">
        <div className="brand-mark" aria-hidden="true">
          <Sparkles size={24} />
        </div>
        <div>
          <strong>SYNTHIA</strong>
          <span>Learning. Human. Together.</span>
        </div>
        {drawer && (
          <button type="button" className="navigation-close" data-cockpit-nav-close onClick={closeNavigation}>
            <X size={18} aria-hidden="true" />
            <span>Close navigation</span>
          </button>
        )}
      </div>

      <nav aria-label="Cockpit sections">
        <section aria-labelledby="roles-title">
          <h2 id="roles-title" className="rail-title">
            Role Switcher
          </h2>
          <div className="role-stack">
            {roleOptions.map(({ role, icon: Icon }) => (
              <button
                key={role}
                type="button"
                className={`rail-button ${activeRole === role ? 'selected' : ''}`}
                aria-pressed={activeRole === role}
                onClick={() => selectRole(role)}
              >
                <Icon size={18} aria-hidden="true" />
                <span>{role}</span>
              </button>
            ))}
          </div>
        </section>

        <section aria-labelledby="teaching-title">
          <h2 id="teaching-title" className="rail-title">
            Teaching
          </h2>
          <div className="role-stack">
            {teachingLinks.map(([label, Icon], index) => (
              <button
                key={label}
                type="button"
                className={`rail-button ${index === 0 ? 'selected' : ''}`}
                aria-current={index === 0 ? 'page' : undefined}
                onClick={onNavigate}
              >
                <Icon size={18} aria-hidden="true" />
                <span>{label}</span>
              </button>
            ))}
          </div>
        </section>

        <section aria-labelledby="governance-title">
          <h2 id="governance-title" className="rail-title">
            Privacy &amp; Governance
          </h2>
          <div className="role-stack">
            {governanceLinks.map(([label, Icon]) => (
              <button key={label} type="button" className="rail-button" onClick={onNavigate}>
                <Icon size={18} aria-hidden="true" />
                <span>{label}</span>
              </button>
            ))}
          </div>
        </section>
      </nav>

      <div className="rail-footer">
        <strong>FNP-QNN summaries minimized</strong>
      </div>
    </aside>
  );
}

interface ProfessorViewProps {
  classHealth: number;
  healthCounts: { onTrack: number; approaching: number; needsSupport: number; total: number };
  classMap: ReturnType<typeof getClassLearningMap>;
  students: StudentLearningSummary[];
  selectedStudent: StudentLearningSummary;
  evidence: FnpQnnInteractionSignal[];
  evidenceOpen: boolean;
  setEvidenceOpen: (value: boolean) => void;
  setSelectedStudentId: (studentId: string) => void;
  draft: InterventionPlan;
  setDraft: (draft: InterventionPlan) => void;
  saveIntervention: () => void;
  transparency: ReturnType<typeof getStudentTransparency>;
  state: AppState;
}

function ProfessorView(props: ProfessorViewProps) {
  return (
    <>
      <section className="dashboard-grid top-grid">
        <Panel title="Class Health" icon={Info}>
          <div className="health-layout">
            <div className="gauge" style={{ '--score': `${props.classHealth}%` } as CSSProperties}>
              <strong>{props.classHealth}%</strong>
              <span>On Track</span>
            </div>
            <div className="legend-list">
              <Legend color="green" label="On Track" value={formatCount(props.healthCounts.onTrack, props.healthCounts.total)} />
              <Legend color="amber" label="Approaching" value={formatCount(props.healthCounts.approaching, props.healthCounts.total)} />
              <Legend color="rose" label="Needs Support" value={formatCount(props.healthCounts.needsSupport, props.healthCounts.total)} />
              <div className="trend">
                <span>Trend (2 weeks)</span>
                <strong>+6%</strong>
              </div>
            </div>
          </div>
        </Panel>

        <Panel title="Support Priorities" icon={LifeBuoy}>
          <div className="priority-list">
            {props.students
              .filter((student) => student.supportPriority !== 'on_track')
              .map((student) => (
                <button
                  type="button"
                  key={student.studentId}
                  className="priority-row"
                  onClick={() => props.setSelectedStudentId(student.studentId)}
                >
                  <Avatar initials={student.initials} priority={student.supportPriority} />
                  <span>{student.displayName}</span>
                  <PriorityBadge priority={student.supportPriority} />
                  <small>{student.recommendation}</small>
                </button>
              ))}
          </div>
        </Panel>

        <Panel title="Concept Mastery" icon={Grid2X2}>
          <div className="heatmap" role="table" aria-label="Whole-class concept mastery">
            <div className="heat-label"></div>
            {props.classMap.conceptMastery.map((concept) => (
              <div className="heat-label" key={concept.concept}>
                {concept.concept}
              </div>
            ))}
            {['Mastered', 'Proficient', 'Developing', 'Emerging'].map((level, rowIndex) => (
              <RowCells key={level} label={level} concepts={props.classMap.conceptMastery} rowIndex={rowIndex} />
            ))}
          </div>
        </Panel>
      </section>

      <section className="dashboard-grid detail-grid">
        <StudentPanel student={props.selectedStudent} setSelectedStudentId={props.setSelectedStudentId} students={props.students} />
        <EvidencePanel evidence={props.evidence} openDrawer={() => props.setEvidenceOpen(true)} />
        <InterventionComposer draft={props.draft} setDraft={props.setDraft} saveIntervention={props.saveIntervention} />
        <div className="stacked-panels">
          <StudentTransparencyPanel transparency={props.transparency} student={props.selectedStudent} />
          <PrivacyPanel state={props.state} />
        </div>
      </section>

      <AuditTimeline events={props.state.auditEvents} />

      {props.evidenceOpen && (
        <EvidenceDrawer evidence={props.evidence} closeDrawer={() => props.setEvidenceOpen(false)} student={props.selectedStudent} />
      )}
    </>
  );
}

function Panel({ title, icon: Icon, children }: { title: string; icon: typeof Info; children: ReactNode }) {
  return (
    <section className="panel" aria-labelledby={`${title.replace(/\s+/g, '-').toLowerCase()}-title`}>
      <div className="panel-title">
        <h2 id={`${title.replace(/\s+/g, '-').toLowerCase()}-title`}>{title}</h2>
        <Icon size={16} />
      </div>
      {children}
    </section>
  );
}

function Legend({ color, label, value }: { color: string; label: string; value: string }) {
  return (
    <div className="legend-item">
      <span className={`dot ${color}`} />
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function formatCount(count: number, total: number) {
  return `${count} (${Math.round((count / Math.max(1, total)) * 100)}%)`;
}

function RowCells({
  label,
  concepts,
  rowIndex
}: {
  label: string;
  concepts: { concept: string; mastery: number }[];
  rowIndex: number;
}) {
  return (
    <>
      <div className="heat-row-label">{label}</div>
      {concepts.map((concept) => {
        const base = Math.max(0, Math.min(100, Math.round(concept.mastery * 100) - rowIndex * 12));
        return (
          <div
            key={`${label}-${concept.concept}`}
            className={`heat-cell ${base > 70 ? 'strong' : base > 52 ? 'medium' : base > 35 ? 'low' : 'quiet'}`}
          >
            {base}
          </div>
        );
      })}
    </>
  );
}

function StudentPanel({
  student,
  students,
  setSelectedStudentId
}: {
  student: StudentLearningSummary;
  students: StudentLearningSummary[];
  setSelectedStudentId: (studentId: string) => void;
}) {
  return (
    <Panel title="Selected Student" icon={UserRound}>
      <div className="student-head">
        <Avatar initials={student.initials} priority={student.supportPriority} large />
        <div>
          <h3>{student.displayName}</h3>
          <p>{student.gradeLevel}</p>
          <p>Homeroom: {student.homeroom}</p>
        </div>
      </div>
      <div className="student-list">
        {students.map((item) => (
          <button
            type="button"
            key={item.studentId}
            className={item.studentId === student.studentId ? 'selected' : ''}
            onClick={() => setSelectedStudentId(item.studentId)}
          >
            <span>{item.displayName}</span>
            <PriorityBadge priority={item.supportPriority} />
          </button>
        ))}
      </div>
      <div className="why-box">
        <strong>Why am I seeing this?</strong>
        <p>{student.recommendation}</p>
        <small>{student.aiLimitations}</small>
      </div>
    </Panel>
  );
}

function EvidencePanel({ evidence, openDrawer }: { evidence: FnpQnnInteractionSignal[]; openDrawer: () => void }) {
  return (
    <Panel title="Evidence" icon={FileCheck2}>
      <div className="evidence-list">
        {evidence.map((item) => (
          <article key={item.evidenceId} className="evidence-row">
            <div className="evidence-icon">
              <FileCheck2 size={18} />
            </div>
            <div>
              <strong>{item.concept}</strong>
              <p>{item.summary}</p>
              <small>
                Confidence {Math.round(item.confidence * 100)}% / {new Date(item.observedAt).toLocaleDateString()}
              </small>
            </div>
          </article>
        ))}
      </div>
      <button type="button" className="link-button" onClick={openDrawer}>
        View all evidence <Eye size={15} />
      </button>
    </Panel>
  );
}

function InterventionComposer({
  draft,
  setDraft,
  saveIntervention
}: {
  draft: InterventionPlan;
  setDraft: (draft: InterventionPlan) => void;
  saveIntervention: () => void;
}) {
  const toggleAction = (action: string) => {
    const exists = draft.actions.includes(action);
    setDraft({
      ...draft,
      actions: exists ? draft.actions.filter((item) => item !== action) : [...draft.actions, action]
    });
  };

  return (
    <Panel title="Intervention Draft" icon={MessageSquareText}>
      <div className="form-grid">
        <label>
          Focus Area
          <input value={draft.focusArea} onChange={(event) => setDraft({ ...draft, focusArea: event.target.value })} />
        </label>
        <label>
          Goal
          <textarea value={draft.goal} onChange={(event) => setDraft({ ...draft, goal: event.target.value })} />
        </label>
        <fieldset>
          <legend>Planned Actions</legend>
          {['Mini-lesson with annotated examples', 'Guided practice with professor check-in', 'Small group problem-solving', 'Student self-reflection prompt'].map(
            (action) => (
              <label key={action} className="check-row">
                <input type="checkbox" checked={draft.actions.includes(action)} onChange={() => toggleAction(action)} />
                <span>{action}</span>
              </label>
            )
          )}
        </fieldset>
        <label>
          Success Indicators
          <textarea
            value={draft.successIndicators.join('\n')}
            onChange={(event) => setDraft({ ...draft, successIndicators: event.target.value.split('\n').filter(Boolean) })}
          />
        </label>
        <label className="check-row human-review">
          <input
            type="checkbox"
            checked={draft.humanValidated}
            onChange={(event) => setDraft({ ...draft, humanValidated: event.target.checked })}
          />
          <span>Human Review Required</span>
        </label>
      </div>
      <div className="form-actions">
        <button type="button" className="ghost-button">
          Save draft
        </button>
        <button type="button" className="primary-button" disabled={!draft.humanValidated} onClick={saveIntervention}>
          <Check size={16} />
          Save Intervention
        </button>
      </div>
    </Panel>
  );
}

function StudentTransparencyPanel({
  transparency,
  student
}: {
  transparency: ReturnType<typeof getStudentTransparency>;
  student: StudentLearningSummary;
}) {
  return (
    <Panel title="Student Transparency" icon={Eye}>
      <div className="student-preview">
        <Avatar initials={student.initials} priority={student.supportPriority} />
        <div>
          <strong>Your Learning Overview</strong>
          <span>Private to you</span>
        </div>
      </div>
      <div className="transparency-row">
        <span>My Progress</span>
        <strong>{student.supportPriority === 'needs_support' ? 'Support planned' : 'On Track'}</strong>
      </div>
      <div className="transparency-row">
        <span>Recent Evidence</span>
        <strong>{transparency.evidenceCount} linked items</strong>
      </div>
      <div className="transparency-row">
        <span>Next Steps</span>
        <strong>{student.recommendation}</strong>
      </div>
      {transparency.interventionSummaries.length > 0 && (
        <div className="notice success">
          <Check size={16} />
          Teacher-validated support is visible to the student.
        </div>
      )}
    </Panel>
  );
}

function PrivacyPanel({ state }: { state: AppState }) {
  return (
    <Panel title="Privacy Centre" icon={LockKeyhole}>
      <div className="privacy-strip">
        <span className="status-chip good">EFVP Ready</span>
        <span className="status-chip warn">Human Review Required</span>
      </div>
      <div className="privacy-facts">
        <span>Responsible role</span>
        <strong>{state.efvp.privacyResponsibleRole}</strong>
        <span>Cloud mode</span>
        <strong>{state.efvp.cloudEnabled ? 'Allowed after EFVP' : 'Blocked'}</strong>
        <span>Leaves Quebec</span>
        <strong>{state.efvp.crossBorderTransferAllowed ? 'Requires agreement' : 'No by default'}</strong>
      </div>
    </Panel>
  );
}

function AuditTimeline({ events }: { events: AppState['auditEvents'] }) {
  return (
    <section className="panel timeline-panel" aria-labelledby="audit-title">
      <div className="panel-title">
        <h2 id="audit-title">Audit Event Timeline</h2>
        <History size={16} />
      </div>
      <div className="timeline">
        {events.slice(0, 5).map((event) => (
          <article key={event.eventId}>
            <div className="timeline-icon">
              <History size={18} />
            </div>
            <div>
              <strong>{event.action}</strong>
              <p>{event.detail}</p>
              <small>{new Date(event.timestamp).toLocaleString()}</small>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function EvidenceDrawer({
  evidence,
  closeDrawer,
  student
}: {
  evidence: FnpQnnInteractionSignal[];
  closeDrawer: () => void;
  student: StudentLearningSummary;
}) {
  return (
    <div className="drawer-backdrop" role="presentation" onMouseDown={closeDrawer}>
      <aside className="drawer" aria-label="Evidence drawer" onMouseDown={(event) => event.stopPropagation()}>
        <div className="drawer-head">
          <div>
            <h2>Evidence for {student.displayName}</h2>
            <p>Minimized FNP-QNN summaries with source IDs, not raw messages.</p>
          </div>
          <button type="button" className="ghost-button" onClick={closeDrawer}>
            Close
          </button>
        </div>
        {evidence.map((item) => (
          <article key={item.evidenceId} className="drawer-evidence">
            <strong>{item.concept}</strong>
            <p>{item.summary}</p>
            <div className="metric-row">
              <span>Mastery {Math.round(item.mastery * 100)}%</span>
              <span>Effort {Math.round(item.effort * 100)}%</span>
              <span>Confusion {Math.round(item.confusion * 100)}%</span>
              <span>Confidence {Math.round(item.confidence * 100)}%</span>
            </div>
            <small>{item.evidenceId}</small>
          </article>
        ))}
      </aside>
    </div>
  );
}

function StudentOnlyView({
  student,
  transparency,
  evidence
}: {
  student: StudentLearningSummary;
  transparency: ReturnType<typeof getStudentTransparency>;
  evidence: FnpQnnInteractionSignal[];
}) {
  return (
    <section className="student-mode">
      <Panel title="Student Transparency" icon={Eye}>
        <div className="student-head">
          <Avatar initials={student.initials} priority={student.supportPriority} large />
          <div>
            <h3>{student.displayName}</h3>
            <p>This is what Synthia can share with your professor.</p>
          </div>
        </div>
        <div className="privacy-facts">
          <span>Shared fields</span>
          <strong>{transparency.sharedFields.join(', ')}</strong>
          <span>Purposes</span>
          <strong>{transparency.purposes.join(', ')}</strong>
          <span>Correction path</span>
          <strong>{transparency.correctionPath}</strong>
        </div>
      </Panel>
      <EvidencePanel evidence={evidence} openDrawer={() => undefined} />
    </section>
  );
}

function GovernanceView({ state }: { state: AppState }) {
  return (
    <section className="governance-grid">
      <PrivacyPanel state={state} />
      <Panel title="Data Flow Register" icon={ShieldCheck}>
        <div className="data-table">
          {state.efvp.dataCategories.map((item) => (
            <article key={item.category}>
              <strong>{item.category}</strong>
              <span>{item.purpose}</span>
              <span>{item.sensitivity}</span>
              <span>{item.retention}</span>
              <span>{item.leavesQuebec ? 'Transfer requires agreement' : 'Quebec by default'}</span>
            </article>
          ))}
        </div>
      </Panel>
      <Panel title="Consent Records" icon={LockKeyhole}>
        <div className="data-table">
          {state.consents.map((item) => (
            <article key={item.studentId}>
              <strong>{item.studentId}</strong>
              <span>{item.status}</span>
              <span>{item.allowedPurposes.length} allowed purposes</span>
              <span>{item.paths.export}</span>
            </article>
          ))}
        </div>
      </Panel>
      <AuditTimeline events={state.auditEvents} />
    </section>
  );
}

function Avatar({ initials, priority, large = false }: { initials: string; priority: string; large?: boolean }) {
  return <span className={`avatar ${priority} ${large ? 'large' : ''}`}>{initials}</span>;
}

function PriorityBadge({ priority }: { priority: string }) {
  const label = priority === 'needs_support' ? 'High' : priority === 'approaching' ? 'Medium' : 'On Track';
  return <span className={`priority-badge ${priority}`}>{label}</span>;
}
