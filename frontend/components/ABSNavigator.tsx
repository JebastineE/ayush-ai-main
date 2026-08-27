"use client";

import { useState, useEffect, useRef } from "react";
import { ABSRequest, ComplianceResponse } from "@/types";
import { CheckCircle, Clock, FileText } from "lucide-react";
import { API_BASE_URL } from "@/lib/config";

interface ABSNavigatorProps {
  /** Demo auto-submit: entity type to pre-fill */
  demoEntityType?: "Indian" | "Foreign" | null;
  /** Demo auto-submit: resource source to pre-fill */
  demoResourceSource?: "Cultivated" | "Wild" | null;
}

export function ABSNavigator({ demoEntityType, demoResourceSource }: ABSNavigatorProps) {
  const [formData, setFormData] = useState<ABSRequest>({
    entity_type: "Indian",
    resource_source: "Cultivated"
  });
  const [result, setResult] = useState<ComplianceResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const autoFiredRef = useRef<string | null>(null);

  // Demo auto-submit: fire once when demo values arrive
  useEffect(() => {
    if (!demoEntityType || !demoResourceSource) return;
    const key = `${demoEntityType}:${demoResourceSource}`;
    if (key === autoFiredRef.current) return;
    autoFiredRef.current = key;
    const demoData: ABSRequest = { entity_type: demoEntityType, resource_source: demoResourceSource };
    setFormData(demoData);
    checkCompliance(demoData);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [demoEntityType, demoResourceSource]);

  const checkCompliance = async (data?: ABSRequest) => {
    const payload = data ?? formData;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/abs-check`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const json: ComplianceResponse = await res.json();
      setResult(json);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      <h2 className="font-headline-sm text-headline-sm text-on-surface">ABS Compliance Navigator</h2>
      
      <div className="bg-surface p-6 rounded-xl border border-outline-variant/30 space-y-4">
        <div>
          <label className="block text-ui-label-bold text-secondary mb-2">Entity Type</label>
          <select 
            value={formData.entity_type}
            onChange={e => setFormData({ ...formData, entity_type: e.target.value as "Indian" | "Foreign" })}
            className="w-full bg-surface-container-lowest border border-outline-variant/50 rounded-lg p-2"
          >
            <option value="Indian">Indian Entity</option>
            <option value="Foreign">Foreign Entity</option>
          </select>
        </div>
        
        <div>
          <label className="block text-ui-label-bold text-secondary mb-2">Resource Source</label>
          <select 
            value={formData.resource_source}
            onChange={e => setFormData({ ...formData, resource_source: e.target.value as "Cultivated" | "Wild" })}
            className="w-full bg-surface-container-lowest border border-outline-variant/50 rounded-lg p-2"
          >
            <option value="Cultivated">Cultivated Resource</option>
            <option value="Wild">Wild Resource</option>
          </select>
        </div>
        
        <button 
          onClick={() => checkCompliance()}
          disabled={loading}
          className="w-full bg-primary-container text-white rounded-lg py-2 font-ui-label-bold hover:bg-primary transition-colors"
        >
          {loading ? "Checking..." : "Verify Compliance"}
        </button>
      </div>

      {result && (
        <div className="bg-surface/80 p-6 rounded-xl border border-primary-container/30 space-y-4 shadow-sm animate-in fade-in zoom-in duration-200">
          <div className="flex items-center gap-2 text-primary-container">
            <CheckCircle className="w-5 h-5" />
            <span className="font-ui-label-bold text-lg">{result.classification}</span>
          </div>
          
          <div className="space-y-2">
            <div className="flex items-start gap-2">
              <FileText className="w-4 h-4 text-secondary mt-1" />
              <div>
                <p className="text-ui-label-sm text-secondary">Statutory Provision</p>
                <p className="font-body-md">{result.statutory_provision}</p>
              </div>
            </div>
            
            <div className="flex items-start gap-2">
              <Clock className="w-4 h-4 text-secondary mt-1" />
              <div>
                <p className="text-ui-label-sm text-secondary">Approval Timeline</p>
                <p className="font-body-md">{result.approval_timeline}</p>
              </div>
            </div>

            <div className="flex flex-col gap-1 mt-4">
              <p className="text-ui-label-sm text-secondary">Required Forms</p>
              <div className="flex gap-2">
                {result.required_forms.map(form => (
                  <span key={form} className="bg-primary-container/10 text-primary-container px-3 py-1 rounded-md text-sm font-medium border border-primary-container/20">
                    {form}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
