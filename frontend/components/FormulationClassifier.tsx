"use client";

import { useState } from "react";
import {
  FlaskConical,
  Plus,
  Trash2,
  Loader2,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  ExternalLink,
  ArrowRight,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { API_BASE_URL } from "@/lib/config";
import type {
  ClassifyFormulationRequest,
  ClassifyFormulationResponse,
  IngredientInput,
} from "@/types";

interface FormulationClassifierProps {
  onCitationClick: (url: string, page: number) => void;
  onNavigateTab: (tab: string) => void;
}

const METHODS = [
  "Churna",
  "Vati",
  "Kashaya",
  "Asava-Arishta",
  "Ghrita",
  "Taila",
  "Bhasma",
  "Other",
];

const ROUTES = [
  { value: "oral", label: "Oral / Therapeutic" },
  { value: "topical", label: "Topical" },
  { value: "cosmetic", label: "Cosmetic" },
  { value: "nutritional", label: "Nutritional" },
];

const DEMO_EXAMPLES = [
  {
    label: "Ashwagandha Churna",
    data: {
      formulation_name: "Ashwagandha Churna",
      ingredients: [
        { name: "Ashwagandha", part: "Root", proportion: "" },
        { name: "Honey", part: "", proportion: "" },
        { name: "Ghee", part: "", proportion: "" },
      ],
      method: "Churna",
      claimed_indication: "General debility, strength promotion, rejuvenation",
      route: "oral",
    },
  },
  {
    label: "Triphala Vati",
    data: {
      formulation_name: "Triphala Vati",
      ingredients: [
        { name: "Haritaki", part: "Fruit", proportion: "1 part" },
        { name: "Bibhitaki", part: "Fruit", proportion: "1 part" },
        { name: "Amalaki", part: "Fruit", proportion: "1 part" },
      ],
      method: "Vati",
      claimed_indication: "Digestive disorders, constipation, eye health",
      route: "oral",
    },
  },
];

export function FormulationClassifier({
  onCitationClick,
  onNavigateTab,
}: FormulationClassifierProps) {
  const [formulationName, setFormulationName] = useState("");
  const [ingredients, setIngredients] = useState<IngredientInput[]>([
    { name: "", part: "", proportion: "" },
  ]);
  const [method, setMethod] = useState("");
  const [route, setRoute] = useState("oral");
  const [indication, setIndication] = useState("");
  const [claimType, setClaimType] = useState("Formulation");
  const [citedSource, setCitedSource] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<ClassifyFormulationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const addIngredient = () => {
    setIngredients([...ingredients, { name: "", part: "", proportion: "" }]);
  };

  const removeIngredient = (index: number) => {
    if (ingredients.length <= 1) return;
    setIngredients(ingredients.filter((_, i) => i !== index));
  };

  const updateIngredient = (
    index: number,
    field: keyof IngredientInput,
    value: string
  ) => {
    const updated = [...ingredients];
    updated[index] = { ...updated[index], [field]: value };
    setIngredients(updated);
  };

  const loadDemo = (demo: (typeof DEMO_EXAMPLES)[0]) => {
    setFormulationName(demo.data.formulation_name || "");
    setIngredients(demo.data.ingredients);
    setMethod(demo.data.method || "");
    setIndication(demo.data.claimed_indication || "");
    setRoute(demo.data.route || "oral");
    setResult(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    const validIngredients = ingredients.filter((i) => i.name.trim());
    if (!validIngredients.length || !indication.trim()) return;

    setIsAnalyzing(true);
    setError(null);
    setResult(null);

    const body: ClassifyFormulationRequest = {
      formulation_name: formulationName || undefined,
      ingredients: validIngredients,
      method: method || undefined,
      claimed_indication: indication,
      cited_source_text: citedSource || undefined,
      route,
      claim_type: claimType,
    };

    try {
      const res = await fetch(
        `${API_BASE_URL}/api/v1/classify-formulation`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        }
      );
      if (!res.ok) throw new Error(`Server returned ${res.status}`);
      const data: ClassifyFormulationResponse = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      setError(
        "Classification failed. Ensure the backend is running and formulation collections are indexed."
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getCategoryBadge = (category: string) => {
    switch (category) {
      case "classical_generic":
        return {
          bg: "bg-blue-50 border-blue-200 text-blue-800",
          icon: <CheckCircle2 className="w-4 h-4" />,
          label: "Classical / Generic",
        };
      case "possible_classical_match":
        return {
          bg: "bg-amber-50 border-amber-200 text-amber-800",
          icon: <AlertTriangle className="w-4 h-4" />,
          label: "Possible Classical Match (Inconclusive)",
        };
      case "insufficient_data":
        return {
          bg: "bg-gray-100 border-gray-300 text-gray-700",
          icon: <AlertTriangle className="w-4 h-4" />,
          label: "Insufficient / Unrecognized Formulation Data",
        };
      default:
        return {
          bg: "bg-gray-50 border-gray-200 text-gray-700",
          icon: <HelpCircle className="w-4 h-4" />,
          label: "No Classical Match Found",
        };
    }
  };

  return (
    <div className="flex-1 overflow-y-auto bg-surface flex flex-col relative h-full">
      <div className="p-6 max-w-5xl mx-auto w-full flex-1">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="inline-flex items-center justify-center p-3 bg-primary-container/10 rounded-2xl mb-4">
            <FlaskConical className="w-8 h-8 text-primary-container" />
          </div>
          <h1 className="text-3xl font-display-md text-on-surface mb-3">
            Formulation Classifier
          </h1>
          <p className="text-secondary max-w-2xl mx-auto text-sm leading-relaxed">
            Classify Ayurvedic formulations against the Ayurvedic Pharmacopoeia
            of India and TKDL records. Determines if a formulation matches known
            classical texts or requires further regulatory assessment.
          </p>
        </div>

        {/* Demo Examples */}
        <div className="flex items-center gap-2 mb-6 justify-center">
          <span className="text-xs text-secondary font-medium">Try:</span>
          {DEMO_EXAMPLES.map((demo) => (
            <button
              key={demo.label}
              onClick={() => loadDemo(demo)}
              className="px-3 py-1.5 text-xs rounded-full border border-outline-variant/40 bg-surface-container-lowest hover:border-primary-container/40 hover:bg-primary-container/5 text-secondary hover:text-primary-container transition-all font-ui-label-bold"
            >
              {demo.label}
            </button>
          ))}
        </div>

        {/* Form */}
        <div className="bg-surface-container-lowest rounded-2xl border border-outline-variant/40 p-6 shadow-sm mb-6">
          {/* Formulation Name */}
          <div className="mb-5">
            <label className="block text-sm font-ui-label-bold text-on-surface mb-1.5">
              Formulation Name{" "}
              <span className="text-secondary font-normal">(optional)</span>
            </label>
            <input
              type="text"
              value={formulationName}
              onChange={(e) => setFormulationName(e.target.value)}
              placeholder="e.g. Ashwagandha Churna"
              className="w-full bg-surface border border-outline-variant/40 rounded-lg py-2.5 px-3 text-on-surface text-sm focus:ring-2 focus:ring-primary-container/20 focus:border-primary-container transition-all"
            />
          </div>

          {/* Ingredients */}
          <div className="mb-5">
            <label className="block text-sm font-ui-label-bold text-on-surface mb-1.5">
              Ingredients
            </label>
            <div className="space-y-2">
              {ingredients.map((ing, idx) => (
                <div key={idx} className="flex gap-2 items-center">
                  <input
                    type="text"
                    value={ing.name}
                    onChange={(e) =>
                      updateIngredient(idx, "name", e.target.value)
                    }
                    placeholder="Ingredient name"
                    className="flex-1 bg-surface border border-outline-variant/40 rounded-lg py-2 px-3 text-sm text-on-surface focus:ring-2 focus:ring-primary-container/20 focus:border-primary-container transition-all"
                  />
                  <input
                    type="text"
                    value={ing.part || ""}
                    onChange={(e) =>
                      updateIngredient(idx, "part", e.target.value)
                    }
                    placeholder="Part used"
                    className="w-28 bg-surface border border-outline-variant/40 rounded-lg py-2 px-3 text-sm text-on-surface focus:ring-2 focus:ring-primary-container/20 focus:border-primary-container transition-all"
                  />
                  <input
                    type="text"
                    value={ing.proportion || ""}
                    onChange={(e) =>
                      updateIngredient(idx, "proportion", e.target.value)
                    }
                    placeholder="Proportion"
                    className="w-28 bg-surface border border-outline-variant/40 rounded-lg py-2 px-3 text-sm text-on-surface focus:ring-2 focus:ring-primary-container/20 focus:border-primary-container transition-all"
                  />
                  <button
                    onClick={() => removeIngredient(idx)}
                    disabled={ingredients.length <= 1}
                    className="p-2 text-secondary hover:text-red-600 disabled:opacity-30 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
            <button
              onClick={addIngredient}
              className="mt-2 flex items-center gap-1.5 text-xs text-primary-container hover:text-primary font-ui-label-bold transition-colors"
            >
              <Plus className="w-3.5 h-3.5" /> Add Ingredient
            </button>
          </div>

          {/* Method + Route row */}
          <div className="grid grid-cols-2 gap-4 mb-5">
            <div>
              <label className="block text-sm font-ui-label-bold text-on-surface mb-1.5">
                Preparation Method
              </label>
              <select
                value={method}
                onChange={(e) => setMethod(e.target.value)}
                className="w-full bg-surface border border-outline-variant/40 rounded-lg py-2.5 px-3 text-sm text-on-surface focus:ring-2 focus:ring-primary-container/20 focus:border-primary-container transition-all"
              >
                <option value="">Select method...</option>
                {METHODS.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-ui-label-bold text-on-surface mb-1.5">
                Route / Claim Type
              </label>
              <select
                value={route}
                onChange={(e) => setRoute(e.target.value)}
                className="w-full bg-surface border border-outline-variant/40 rounded-lg py-2.5 px-3 text-sm text-on-surface focus:ring-2 focus:ring-primary-container/20 focus:border-primary-container transition-all"
              >
                {ROUTES.map((r) => (
                  <option key={r.value} value={r.value}>
                    {r.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* What are you trying to protect? */}
          <div className="mb-5">
            <label className="block text-sm font-ui-label-bold text-on-surface mb-1.5">
              What are you trying to protect?
            </label>
            <select
              value={claimType}
              onChange={(e) => setClaimType(e.target.value)}
              className="w-full bg-surface border border-outline-variant/40 rounded-lg py-2.5 px-3 text-sm text-on-surface focus:ring-2 focus:ring-primary-container/20 focus:border-primary-container transition-all"
            >
              <option value="Plant / biological material">Plant / biological material</option>
              <option value="Plant part">Plant part</option>
              <option value="Extract">Extract</option>
              <option value="Isolated compound / constituent">Isolated compound / constituent</option>
              <option value="Composition">Composition</option>
              <option value="Formulation">Formulation</option>
              <option value="Preparation / extraction process">Preparation / extraction process</option>
              <option value="Method / use">Method / use</option>
              <option value="Other">Other</option>
            </select>
          </div>

          {/* Indication */}
          <div className="mb-5">
            <label className="block text-sm font-ui-label-bold text-on-surface mb-1.5">
              Claimed Indication / Use
            </label>
            <textarea
              value={indication}
              onChange={(e) => setIndication(e.target.value)}
              placeholder="e.g. General debility, strength promotion, rejuvenation"
              rows={2}
              className="w-full bg-surface border border-outline-variant/40 rounded-lg py-2.5 px-3 text-sm text-on-surface focus:ring-2 focus:ring-primary-container/20 focus:border-primary-container transition-all resize-none"
            />
          </div>

          {/* Cited Source (optional) */}
          <div className="mb-6">
            <label className="block text-sm font-ui-label-bold text-on-surface mb-1.5">
              Cited Source Text{" "}
              <span className="text-secondary font-normal">(optional)</span>
            </label>
            <input
              type="text"
              value={citedSource}
              onChange={(e) => setCitedSource(e.target.value)}
              placeholder="e.g. Charaka Samhita, Chikitsa Sthana 1/3"
              className="w-full bg-surface border border-outline-variant/40 rounded-lg py-2.5 px-3 text-sm text-on-surface focus:ring-2 focus:ring-primary-container/20 focus:border-primary-container transition-all"
            />
          </div>

          {/* Analyze Button */}
          <button
            onClick={handleAnalyze}
            disabled={
              isAnalyzing ||
              !indication.trim() ||
              !ingredients.some((i) => i.name.trim())
            }
            className="w-full bg-primary-container text-white py-3 rounded-xl font-ui-label-bold text-sm hover:bg-primary transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" /> Analyzing...
              </>
            ) : (
              <>
                <FlaskConical className="w-4 h-4" /> Analyze Formulation
              </>
            )}
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm mb-6 text-center">
            {error}
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 space-y-4">
            {/* Category Badge */}
            {(() => {
              const badge = getCategoryBadge(result.category);
              return (
                <div
                  className={cn(
                    "flex items-center gap-3 p-4 rounded-xl border",
                    badge.bg
                  )}
                >
                  {badge.icon}
                  <div>
                    <span className="font-ui-label-bold text-sm">
                      {badge.label}
                    </span>
                    <span className="ml-3 text-xs opacity-70">
                      Confidence: {result.confidence}
                    </span>
                  </div>
                </div>
              );
            })()}

            {/* Matched Source */}
            {result.matched_classical_source && (
              <div className="bg-surface-container-lowest rounded-xl border border-outline-variant/40 p-4">
                <h3 className="text-sm font-ui-label-bold text-on-surface mb-2">
                  Classification Evidence
                </h3>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-on-surface font-medium">
                      {result.matched_classical_source.formula_name}
                    </p>
                    <p className="text-xs text-secondary mt-0.5">
                      Ayurvedic Pharmacopoeia Vol.{" "}
                      {result.matched_classical_source.volume}, Page{" "}
                      {result.matched_classical_source.page} — Similarity:{" "}
                      {(result.matched_classical_source.similarity * 100).toFixed(
                        1
                      )}
                      %
                    </p>
                  </div>
                  <button
                    onClick={() =>
                      onCitationClick(
                        `/docs/${result.matched_classical_source!.source}`,
                        result.matched_classical_source!.page
                      )
                    }
                    className="text-xs text-primary-container hover:text-primary flex items-center gap-1 transition-colors"
                  >
                    <ExternalLink className="w-3.5 h-3.5" /> View Source
                  </button>
                </div>
              </div>
            )}

            {/* TKDL Match */}
            {result.matched_tkdl_record && (
              <div className="bg-surface-container-lowest rounded-xl border border-outline-variant/40 p-4">
                <h3 className="text-sm font-ui-label-bold text-on-surface mb-2">
                  TKDL Evidence
                </h3>
                <p className="text-sm text-on-surface">
                  {result.matched_tkdl_record.formulation_name}
                </p>
                <p className="text-xs text-secondary mt-1">
                  IPC: {result.matched_tkdl_record.ipc_code} | TKRC:{" "}
                  {result.matched_tkdl_record.tkrc_code} | Similarity:{" "}
                  {(result.matched_tkdl_record.similarity * 100).toFixed(1)}%
                </p>
              </div>
            )}

            {/* Ingredient Match Table */}
            {result.ingredient_matches.length > 0 && (
              <div className="bg-surface-container-lowest rounded-xl border border-outline-variant/40 p-4">
                <h3 className="text-sm font-ui-label-bold text-on-surface mb-3">
                  Ingredient Evidence
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="border-b border-outline-variant/30">
                        <th className="text-left py-2 px-2 text-secondary font-medium">
                          Input
                        </th>
                        <th className="text-left py-2 px-2 text-secondary font-medium">
                          Canonical Name
                        </th>
                        <th className="text-left py-2 px-2 text-secondary font-medium">
                          Matched
                        </th>
                        <th className="text-left py-2 px-2 text-secondary font-medium">
                          Confidence
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.ingredient_matches.map((ing, i) => (
                        <tr
                          key={i}
                          className="border-b border-outline-variant/20 last:border-0"
                        >
                          <td className="py-2 px-2 text-on-surface">
                            {ing.input}
                          </td>
                          <td className="py-2 px-2 text-on-surface">
                            {ing.canonical_name}
                          </td>
                          <td className="py-2 px-2">
                            {ing.matched ? (
                              <span className="text-green-700 font-medium">
                                Yes
                              </span>
                            ) : (
                              <span className="text-amber-600 font-medium">
                                No
                              </span>
                            )}
                          </td>
                          <td className="py-2 px-2 text-secondary">
                            {ing.matched && ing.confidence ? `${ing.confidence}%` : "N/A"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {result.unmatched_ingredients.length > 0 && (
                  <p className="mt-2 text-xs text-amber-700 bg-amber-50 px-3 py-1.5 rounded-md">
                    Unmatched: {result.unmatched_ingredients.join(", ")}
                  </p>
                )}
              </div>
            )}

            {/* Explanation */}
            <div className="bg-surface-container-lowest rounded-xl border border-outline-variant/40 p-4">
              <h3 className="text-sm font-ui-label-bold text-on-surface mb-2">
                IP Posture & Regulatory Guidance
              </h3>
              <p className="text-sm text-on-surface/80 leading-relaxed whitespace-pre-line">
                {result.ip_posture_explanation}
              </p>
            </div>

            {/* Traditional Uses (Source-backed) */}
            {result.traditional_uses && (
              <div className="bg-surface-container-lowest rounded-xl border border-outline-variant/40 p-4">
                <h3 className="text-sm font-ui-label-bold text-on-surface mb-2">
                  Traditional Uses / Associated Conditions
                </h3>
                <p className="text-sm text-on-surface/80 leading-relaxed whitespace-pre-line">
                  {result.traditional_uses}
                </p>
              </div>
            )}


            {/* Regulatory Citations */}
            {result.regulatory_citations.length > 0 && (() => {
              const pdfCitations = result.regulatory_citations.filter(
                (c) => c.source.toLowerCase().endsWith(".pdf")
              );
              if (pdfCitations.length === 0) return null;
              return (
              <div className="bg-surface-container-lowest rounded-xl border border-outline-variant/40 p-4">
                <h3 className="text-sm font-ui-label-bold text-on-surface mb-2">
                  General Regulatory Guidance
                </h3>
                <div className="space-y-2">
                  {pdfCitations.map((cit, i) => (
                    <button
                      key={i}
                      onClick={() =>
                        onCitationClick(`${API_BASE_URL}/api/v1/document/${encodeURIComponent(cit.source)}`, cit.page ?? 0)
                      }
                      className="w-full text-left p-2.5 rounded-lg bg-surface-container-low/50 hover:bg-primary-container/5 border border-outline-variant/20 hover:border-primary-container/30 transition-all"
                    >
                      <span className="text-xs font-medium text-primary-container">
                        {cit.source}, p.{cit.page}
                      </span>
                      <p className="text-xs text-secondary mt-0.5 line-clamp-2">
                        {cit.snippet}
                      </p>
                    </button>
                  ))}
                </div>
              </div>
              );
            })()}

            {/* Cross-Tab Actions */}
            {result.suggested_actions.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {result.suggested_actions.map((action, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      const tabMap: Record<string, string> = {
                        "/biopiracy-scanner": "biopiracy",
                        "/legal-assistant": "chat",
                      };
                      const tab = tabMap[action.route] || "chat";
                      onNavigateTab(tab);
                    }}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg border border-outline-variant/40 bg-surface-container-lowest hover:border-primary-container/40 hover:bg-primary-container/5 text-sm text-secondary hover:text-primary-container transition-all"
                  >
                    <ArrowRight className="w-3.5 h-3.5" />
                    {action.label}
                  </button>
                ))}
              </div>
            )}

            {/* Disclaimer */}
            <p className="text-xs text-secondary/70 text-center italic pt-2">
              {result.disclaimer}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
