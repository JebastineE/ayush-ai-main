"use client";

import { useState, useCallback } from "react";
import {
  WizardState,
  WizardResponse,
  WizardStepDefinition,
  ComplianceResponse,
} from "@/types";
import {
  CheckCircle,
  ChevronRight,
  ChevronLeft,
  Info,
  FileText,
  Shield,
  AlertCircle,
  Sparkles,
  BookOpen,
  Scale,
  Leaf,
  FlaskConical,
  Utensils,
  Droplets,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { API_BASE_URL } from "@/lib/config";

const API_BASE = API_BASE_URL;

// ── Category Icon Map ─────────────────────────────────────────────────────
const CATEGORY_ICONS: Record<string, React.ReactNode> = {
  "Classical Ayurvedic Medicine": <BookOpen className="w-6 h-6" />,
  "Proprietary Ayurvedic Medicine": <Scale className="w-6 h-6" />,
  "New / Non-Classical Ayurvedic Drug": <Sparkles className="w-6 h-6" />,
  "Phytopharmaceutical Drug": <FlaskConical className="w-6 h-6" />,
  "Ayurveda-Aahar / Nutraceutical": <Utensils className="w-6 h-6" />,
  Cosmetic: <Droplets className="w-6 h-6" />,
};

const CATEGORY_COLORS: Record<string, string> = {
  "Classical Ayurvedic Medicine":
    "from-amber-500/20 to-orange-500/10 border-amber-500/30 text-amber-700",
  "Proprietary Ayurvedic Medicine":
    "from-blue-500/20 to-indigo-500/10 border-blue-500/30 text-blue-700",
  "New / Non-Classical Ayurvedic Drug":
    "from-purple-500/20 to-violet-500/10 border-purple-500/30 text-purple-700",
  "Phytopharmaceutical Drug":
    "from-green-500/20 to-emerald-500/10 border-green-500/30 text-green-700",
  "Ayurveda-Aahar / Nutraceutical":
    "from-teal-500/20 to-cyan-500/10 border-teal-500/30 text-teal-700",
  Cosmetic: "from-pink-500/20 to-rose-500/10 border-pink-500/30 text-pink-700",
};

// ── Step Progress Bar ─────────────────────────────────────────────────────
function ProgressBar({
  current,
  total,
}: {
  current: number;
  total: number;
}) {
  const pct = Math.min(((current - 1) / total) * 100, 100);
  return (
    <div className="w-full mb-6">
      <div className="flex justify-between items-center mb-2">
        <span className="text-xs font-semibold text-secondary uppercase tracking-wider">
          Step {current} of {total}
        </span>
        <span className="text-xs text-secondary">{Math.round(pct)}% complete</span>
      </div>
      <div className="h-1.5 bg-surface-container-low rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-primary-container to-primary transition-all duration-500 ease-out rounded-full"
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className="flex justify-between mt-2">
        {Array.from({ length: total }).map((_, i) => (
          <div
            key={i}
            className={cn(
              "w-2 h-2 rounded-full transition-all duration-300",
              i + 1 < current
                ? "bg-primary-container scale-100"
                : i + 1 === current
                ? "bg-primary-container scale-125 ring-2 ring-primary-container/30"
                : "bg-outline-variant/40 scale-75"
            )}
          />
        ))}
      </div>
    </div>
  );
}

// ── Option Card ───────────────────────────────────────────────────────────
function OptionCard({
  option,
  selected,
  onSelect,
}: {
  option: { value: string; label: string };
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      onClick={onSelect}
      className={cn(
        "w-full text-left px-4 py-3.5 rounded-xl border-2 transition-all duration-200",
        "hover:border-primary-container/60 hover:bg-primary-container/5",
        "flex items-center gap-3 group",
        selected
          ? "border-primary-container bg-primary-container/10 shadow-sm"
          : "border-outline-variant/30 bg-surface/50"
      )}
    >
      <div
        className={cn(
          "w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-all",
          selected
            ? "border-primary-container bg-primary-container"
            : "border-outline-variant group-hover:border-primary-container/60"
        )}
      >
        {selected && <div className="w-2 h-2 rounded-full bg-white" />}
      </div>
      <span
        className={cn(
          "font-body-md text-sm transition-colors",
          selected ? "text-primary-container font-semibold" : "text-on-surface"
        )}
      >
        {option.label}
      </span>
    </button>
  );
}

// ── Result Card ───────────────────────────────────────────────────────────
function ResultCard({ result }: { result: ComplianceResponse }) {
  const colorClass =
    CATEGORY_COLORS[result.classification] ||
    "from-primary-container/20 to-primary/10 border-primary-container/30 text-primary-container";
  const icon =
    CATEGORY_ICONS[result.classification] || <Shield className="w-6 h-6" />;

  return (
    <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Classification Badge */}
      <div
        className={cn(
          "bg-gradient-to-br rounded-2xl border p-5",
          colorClass
        )}
      >
        <div className="flex items-center gap-3 mb-1">
          {icon}
          <h3 className="text-lg font-bold">{result.classification}</h3>
        </div>
        <p className="text-xs mt-1 opacity-80 font-mono">{result.statutory_provision}</p>
      </div>

      {/* IP Posture */}
      {result.ip_posture && (
        <div className="bg-surface/80 rounded-xl border border-outline-variant/30 p-4 space-y-1.5">
          <div className="flex items-center gap-2 text-primary-container mb-2">
            <Scale className="w-4 h-4" />
            <span className="font-semibold text-sm">IP Posture</span>
          </div>
          <p className="text-sm text-on-surface/90 leading-relaxed">{result.ip_posture}</p>
        </div>
      )}

      {/* ABS Duties */}
      {result.abs_duties && (
        <div className="bg-surface/80 rounded-xl border border-outline-variant/30 p-4 space-y-1.5">
          <div className="flex items-center gap-2 text-amber-600 mb-2">
            <Leaf className="w-4 h-4" />
            <span className="font-semibold text-sm">ABS Obligations</span>
          </div>
          <p className="text-sm text-on-surface/90 leading-relaxed">{result.abs_duties}</p>
        </div>
      )}

      {/* Required Forms */}
      {result.required_forms && result.required_forms.length > 0 && (
        <div className="bg-surface/80 rounded-xl border border-outline-variant/30 p-4">
          <div className="flex items-center gap-2 text-secondary mb-3">
            <FileText className="w-4 h-4" />
            <span className="font-semibold text-sm">Required Forms & Licences</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {result.required_forms.map((f, i) => (
              <span
                key={i}
                className="px-2.5 py-1 rounded-md bg-surface-container border border-outline-variant/40 text-xs font-mono text-secondary"
              >
                {f}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Timeline */}
      <div className="bg-surface/80 rounded-xl border border-outline-variant/30 p-4">
        <div className="flex items-center gap-2 text-secondary mb-1">
          <Info className="w-4 h-4" />
          <span className="font-semibold text-sm">Approval Timeline</span>
        </div>
        <p className="text-sm text-on-surface font-medium">{result.approval_timeline}</p>
      </div>

      {/* Recommended Next Steps */}
      {result.recommended_next_steps && result.recommended_next_steps.length > 0 && (
        <div className="bg-surface/80 rounded-xl border border-outline-variant/30 p-4">
          <div className="flex items-center gap-2 text-green-600 mb-3">
            <CheckCircle className="w-4 h-4" />
            <span className="font-semibold text-sm">Recommended Next Steps</span>
          </div>
          <ol className="space-y-2">
            {result.recommended_next_steps.map((step, i) => (
              <li key={i} className="flex items-start gap-3 text-sm">
                <span className="flex-shrink-0 w-5 h-5 rounded-full bg-primary-container/10 text-primary-container text-xs flex items-center justify-center font-bold mt-0.5">
                  {i + 1}
                </span>
                <span className="text-on-surface/90 leading-relaxed">{step}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* Disclaimer */}
      <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 flex items-start gap-2">
        <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
        <p className="text-xs text-amber-700 leading-relaxed">
          This classification is for informational purposes only and does not constitute legal advice.
          Consult a qualified IP attorney or the relevant statutory authority before taking action.
        </p>
      </div>
    </div>
  );
}

// ── Main Wizard Component ─────────────────────────────────────────────────
export function FormulationClassifier() {
  const [wizardState, setWizardState] = useState<WizardState>({
    current_step: 1,
    answers: {},
  });
  const [currentStepDef, setCurrentStepDef] = useState<WizardStepDefinition | null>(null);
  const [selectedOption, setSelectedOption] = useState<string>("");
  const [result, setResult] = useState<ComplianceResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalSteps, setTotalSteps] = useState(5);
  const [started, setStarted] = useState(false);
  const [history, setHistory] = useState<WizardStepDefinition[]>([]);

  const callWizard = useCallback(async (state: WizardState) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/classify/wizard`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(state),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: WizardResponse = await res.json();

      setTotalSteps(data.total_steps);

      if (data.is_complete && data.result) {
        setResult(data.result);
        setCurrentStepDef(null);
      } else if (data.next_step) {
        setCurrentStepDef(data.next_step);
        setSelectedOption("");
      }
    } catch (e) {
      setError("Could not reach the backend. Is it running on port 8000?");
    } finally {
      setLoading(false);
    }
  }, []);

  const handleStart = () => {
    setStarted(true);
    setResult(null);
    setHistory([]);
    const initialState: WizardState = { current_step: 1, answers: {} };
    setWizardState(initialState);
    callWizard(initialState);
  };

  const handleNext = () => {
    if (!selectedOption || !currentStepDef) return;

    const newAnswers = { ...wizardState.answers, [currentStepDef.field]: selectedOption };
    const newStep = wizardState.current_step + 1;
    const newState: WizardState = { current_step: newStep, answers: newAnswers };

    if (currentStepDef) setHistory((h) => [...h, currentStepDef]);
    setWizardState(newState);
    callWizard(newState);
  };

  const handleBack = () => {
    if (history.length === 0) return;

    const prevStep = history[history.length - 1];
    const newHistory = history.slice(0, -1);
    const newStep = wizardState.current_step - 1;
    const newAnswers = { ...wizardState.answers };
    delete newAnswers[prevStep.field];

    const newState: WizardState = { current_step: newStep, answers: newAnswers };

    setHistory(newHistory);
    setWizardState(newState);
    setCurrentStepDef(prevStep);
    setSelectedOption(wizardState.answers[prevStep.field] || "");
    setResult(null);
  };

  const handleReset = () => {
    setStarted(false);
    setResult(null);
    setCurrentStepDef(null);
    setWizardState({ current_step: 1, answers: {} });
    setHistory([]);
    setSelectedOption("");
    setError(null);
  };

  // ── Welcome Screen ─────────────────────────────────────────────────────
  if (!started) {
    return (
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        <div>
          <h2 className="font-headline-sm text-headline-sm text-on-surface">
            Formulation Classifier
          </h2>
          <p className="text-secondary text-sm mt-1">
            5-step diagnostic triage — determine your product&apos;s regulatory category
            and IP/ABS posture.
          </p>
        </div>

        <div className="bg-surface/80 rounded-2xl border border-outline-variant/30 p-6 space-y-5">
          <div className="grid grid-cols-2 gap-3">
            {[
              { icon: <BookOpen className="w-5 h-5" />, label: "Classical", color: "text-amber-600" },
              { icon: <Scale className="w-5 h-5" />, label: "Proprietary", color: "text-blue-600" },
              { icon: <Sparkles className="w-5 h-5" />, label: "New Drug", color: "text-purple-600" },
              { icon: <FlaskConical className="w-5 h-5" />, label: "Phytopharmaceutical", color: "text-green-600" },
              { icon: <Utensils className="w-5 h-5" />, label: "Ayurveda-Aahar", color: "text-teal-600" },
              { icon: <Droplets className="w-5 h-5" />, label: "Cosmetic", color: "text-pink-600" },
            ].map((c) => (
              <div
                key={c.label}
                className="flex items-center gap-2 px-3 py-2 rounded-lg bg-surface-container/50 border border-outline-variant/20"
              >
                <span className={c.color}>{c.icon}</span>
                <span className="text-xs font-medium text-on-surface">{c.label}</span>
              </div>
            ))}
          </div>

          <p className="text-xs text-secondary leading-relaxed">
            Answer 5 short questions to determine whether your Ayurvedic product is a Classical
            Medicine, Proprietary Medicine, New Drug, Phytopharmaceutical, Ayurveda-Aahar, or
            Cosmetic — and see the exact IP protection strategies and ABS obligations for each
            category.
          </p>

          <button
            onClick={handleStart}
            className="w-full flex items-center justify-center gap-2 bg-primary-container text-white rounded-xl py-3 font-semibold hover:bg-primary transition-all duration-200 shadow-md hover:shadow-lg hover:-translate-y-0.5"
          >
            <ChevronRight className="w-5 h-5" />
            Begin Diagnostic Triage
          </button>
        </div>
      </div>
    );
  }

  // ── Result Screen ──────────────────────────────────────────────────────
  if (result) {
    return (
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-headline-sm text-headline-sm text-on-surface">
              Classification Result
            </h2>
            <p className="text-secondary text-sm mt-0.5">Completed in {totalSteps} steps</p>
          </div>
          <button
            onClick={handleReset}
            className="text-xs px-3 py-1.5 rounded-lg border border-outline-variant/50 text-secondary hover:text-primary-container hover:border-primary-container/40 transition-all"
          >
            Restart
          </button>
        </div>
        <ResultCard result={result} />
      </div>
    );
  }

  // ── Question Screen ────────────────────────────────────────────────────
  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-4">
      <div>
        <h2 className="font-headline-sm text-headline-sm text-on-surface">
          Formulation Classifier
        </h2>
        <p className="text-secondary text-sm mt-1">
          Multi-step diagnostic triage
        </p>
      </div>

      {loading && (
        <div className="bg-surface/80 rounded-2xl border border-outline-variant/30 p-8 flex flex-col items-center justify-center gap-3">
          <div className="w-8 h-8 rounded-full border-2 border-primary-container border-t-transparent animate-spin" />
          <p className="text-secondary text-sm">Analysing your inputs...</p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {!loading && currentStepDef && (
        <div className="bg-surface/80 rounded-2xl border border-outline-variant/30 p-5 space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
          <ProgressBar current={wizardState.current_step} total={totalSteps} />

          <div>
            <p className="font-semibold text-on-surface leading-snug text-sm">
              {currentStepDef.question}
            </p>
            {currentStepDef.hint && (
              <div className="mt-2 flex items-start gap-2">
                <Info className="w-3.5 h-3.5 text-primary-container flex-shrink-0 mt-0.5" />
                <p className="text-xs text-secondary leading-relaxed">{currentStepDef.hint}</p>
              </div>
            )}
          </div>

          <div className="space-y-2.5">
            {currentStepDef.options.map((opt) => (
              <OptionCard
                key={opt.value}
                option={opt}
                selected={selectedOption === opt.value}
                onSelect={() => setSelectedOption(opt.value)}
              />
            ))}
          </div>

          <div className="flex gap-3 pt-1">
            {history.length > 0 && (
              <button
                onClick={handleBack}
                className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl border border-outline-variant/50 text-secondary hover:text-on-surface hover:border-outline-variant transition-all text-sm font-medium"
              >
                <ChevronLeft className="w-4 h-4" />
                Back
              </button>
            )}
            <button
              onClick={handleNext}
              disabled={!selectedOption}
              className={cn(
                "flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl font-semibold text-sm transition-all duration-200",
                selectedOption
                  ? "bg-primary-container text-white hover:bg-primary shadow-md hover:shadow-lg hover:-translate-y-0.5"
                  : "bg-surface-container-low text-outline cursor-not-allowed"
              )}
            >
              {wizardState.current_step === totalSteps ? (
                <>
                  <CheckCircle className="w-4 h-4" />
                  Get Classification
                </>
              ) : (
                <>
                  Next
                  <ChevronRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
