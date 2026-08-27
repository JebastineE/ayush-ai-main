"use client";

import { X, CheckSquare, AlertTriangle } from "lucide-react";
import { useState } from "react";

interface PatentChecklistProps {
  onClose: () => void;
  citations?: any[];
}

const CHECKLIST_ITEMS = [
  {
    category: "Invention Details",
    items: [
      "Clearly identify the invention and its technical features",
      "Document the problem being solved",
      "Describe the technical solution provided",
      "Identify key innovative aspects",
    ],
  },
  {
    category: "Applicant Information",
    items: [
      "Identify applicant(s) - individual or entity",
      "Identify inventor(s)",
      "Verify address and contact details",
      "Confirm right to file (if applicant ≠ inventor)",
    ],
  },
  {
    category: "Prior Art & Novelty",
    items: [
      "Conduct thorough prior art search",
      "Review existing patents in relevant IPC classes",
      "Check TKDL database for traditional knowledge",
      "Document novelty over prior art",
      "Assess inventive step / non-obviousness",
    ],
  },
  {
    category: "Legal Requirements",
    items: [
      "Review relevant patent exclusions (Section 3, Patents Act 1970)",
      "Check for traditional knowledge issues (Section 3(p))",
      "Assess biological resource requirements if applicable",
      "Verify industrial applicability",
    ],
  },
  {
    category: "Documentation",
    items: [
      "Prepare detailed specification",
      "Draft clear and comprehensive claims",
      "Prepare drawings/diagrams if applicable",
      "Compile supporting technical data",
    ],
  },
  {
    category: "Professional Review",
    items: [
      "Obtain professional IP attorney review",
      "Consider provisional vs. complete application strategy",
      "Plan international filing strategy if needed",
      "Review estimated costs and timeline",
    ],
  },
];

export function PatentChecklist({ onClose, citations }: PatentChecklistProps) {
  const [checkedItems, setCheckedItems] = useState<Set<string>>(new Set());

  const toggleItem = (item: string) => {
    const newChecked = new Set(checkedItems);
    if (newChecked.has(item)) {
      newChecked.delete(item);
    } else {
      newChecked.add(item);
    }
    setCheckedItems(newChecked);
  };

  const totalItems = CHECKLIST_ITEMS.reduce((sum, cat) => sum + cat.items.length, 0);
  const completedItems = checkedItems.size;
  const progress = totalItems > 0 ? (completedItems / totalItems) * 100 : 0;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <CheckSquare className="w-6 h-6 text-white" />
            <h2 className="text-xl font-bold text-white">Patent Preparation Checklist</h2>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="px-6 py-3 border-b border-gray-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-semibold text-gray-700">
              Progress: {completedItems} / {totalItems}
            </span>
            <span className="text-sm font-semibold text-blue-600">{progress.toFixed(0)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Disclaimer */}
        <div className="px-6 py-3 bg-amber-50 border-b border-amber-200 flex items-start gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
          <p className="text-xs text-amber-800 leading-relaxed">
            <strong>Disclaimer:</strong> This checklist is for informational purposes only. Completing
            these items does <strong>not guarantee</strong> patentability. Always consult a qualified
            patent attorney or IP professional before filing.
          </p>
        </div>

        {/* Checklist Content */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          <div className="space-y-6">
            {CHECKLIST_ITEMS.map((category, catIdx) => (
              <div key={catIdx}>
                <h3 className="text-sm font-bold text-gray-800 mb-3 flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-blue-100 text-blue-600 text-xs flex items-center justify-center font-bold">
                    {catIdx + 1}
                  </span>
                  {category.category}
                </h3>
                <div className="space-y-2 ml-8">
                  {category.items.map((item, itemIdx) => {
                    const itemKey = `${catIdx}-${itemIdx}`;
                    const isChecked = checkedItems.has(itemKey);
                    return (
                      <label
                        key={itemIdx}
                        className="flex items-start gap-3 cursor-pointer group"
                      >
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => toggleItem(itemKey)}
                          className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-2 focus:ring-blue-500 flex-shrink-0 mt-0.5"
                        />
                        <span
                          className={`text-sm leading-relaxed transition-all ${
                            isChecked
                              ? "text-gray-400 line-through"
                              : "text-gray-700 group-hover:text-blue-600"
                          }`}
                        >
                          {item}
                        </span>
                      </label>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          {/* Supporting Citations */}
          {citations && citations.length > 0 && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <h3 className="text-sm font-bold text-gray-800 mb-3">
                Supporting Statutory References
              </h3>
              <div className="space-y-2">
                {citations.slice(0, 3).map((cit: any, idx: number) => (
                  <div
                    key={idx}
                    className="text-xs p-3 bg-gray-50 rounded-lg border border-gray-200"
                  >
                    <div className="font-semibold text-gray-700 mb-1">
                      📄 {cit.source} (Page {cit.page})
                    </div>
                    <div className="text-gray-600 line-clamp-2">{cit.snippet}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <button
            onClick={onClose}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
          >
            Close Checklist
          </button>
        </div>
      </div>
    </div>
  );
}
