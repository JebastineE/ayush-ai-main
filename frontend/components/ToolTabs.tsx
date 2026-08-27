import { MessageSquare, Gavel, Beaker, Shield } from "lucide-react";
import { cn } from "@/lib/utils";

interface ToolTabsProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export function ToolTabs({ activeTab, onTabChange }: ToolTabsProps) {
  const tabs = [
    { id: "chat", label: "Legal Assistant (RAG)", icon: MessageSquare },
    { id: "abs", label: "ABS Navigator (2024)", icon: Gavel },
    { id: "formulation", label: "Formulation Classifier", icon: Beaker },
    { id: "biopiracy", label: "Biopiracy Scanner", icon: Shield },
  ];

  return (
    <div className="h-14 border-b border-outline-variant/30 flex items-center bg-surface/50 backdrop-blur-md shrink-0 overflow-x-auto scrollbar-hide px-2 gap-1">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;
        
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={cn(
              "h-9 px-4 flex items-center gap-2 rounded-full shrink-0 transition-colors border",
              isActive 
                ? "bg-primary-container/10 text-primary-container border-transparent shadow-sm"
                : "border-transparent text-secondary hover:text-primary-container hover:bg-surface-container-low/50"
            )}
          >
            <Icon className="w-4 h-4 font-light" />
            <span className="font-ui-label-bold text-ui-label-bold">{tab.label}</span>
          </button>
        );
      })}
    </div>
  );
}
