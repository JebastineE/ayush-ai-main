"use client";

import { useState, useRef, useEffect } from "react";
import { Globe, Bell, Settings, ChevronDown, Check } from "lucide-react";
import { cn } from "@/lib/utils";

interface NavbarProps {
  jurisdiction: "india" | "international";
  onJurisdictionChange: (j: "india" | "international") => void;
  language: string;
  onLanguageChange: (lang: string) => void;
}

const LANGUAGES: Array<{ code: string; label: string; native: string }> = [
  { code: "en", label: "English", native: "English" },
  { code: "hi", label: "Hindi", native: "हिन्दी" },
  { code: "bn", label: "Bengali", native: "বাংলা" },
  { code: "ta", label: "Tamil", native: "தமிழ்" },
  { code: "te", label: "Telugu", native: "తెలుగు" },
  { code: "mr", label: "Marathi", native: "मराठी" },
  { code: "gu", label: "Gujarati", native: "ગુજરાતી" },
  { code: "kn", label: "Kannada", native: "ಕನ್ನಡ" },
  { code: "ml", label: "Malayalam", native: "മലയാളം" },
  { code: "pa", label: "Punjabi", native: "ਪੰਜਾਬੀ" },
];

export function Navbar({
  jurisdiction,
  onJurisdictionChange,
  language,
  onLanguageChange,
}: NavbarProps) {
  const [langOpen, setLangOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const currentLang = LANGUAGES.find((l) => l.code === language) || LANGUAGES[0];

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setLangOpen(false);
      }
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  return (
    <header className="bg-surface/70 backdrop-blur-md dark:bg-background/80 border-b border-outline-variant/30 flex justify-between items-center h-16 px-gutter w-full sticky top-0 z-50 shrink-0 shadow-sm">
      <div className="flex items-center gap-6">
        <h1 className="font-headline-md text-headline-md text-primary-container dark:text-inverse-primary tracking-tight">
          IP-SAKTI Sahayak{" "}
          <span className="text-secondary text-sm font-normal">(v6.0)</span>
        </h1>

        {/* Jurisdiction Toggle */}
        <div className="hidden md:flex bg-surface-container-low/50 backdrop-blur-sm rounded-full p-1 gap-1 border border-outline-variant/50 shadow-sm">
          <button
            onClick={() => onJurisdictionChange("india")}
            className={cn(
              "font-ui-label-bold text-ui-label-bold px-4 py-1.5 transition-colors rounded-full text-sm",
              jurisdiction === "india"
                ? "bg-primary-container/10 text-primary-container shadow-sm"
                : "text-secondary hover:text-primary-container hover:bg-surface-container-high/50"
            )}
          >
            🇮🇳 India Law
          </button>
          <button
            onClick={() => onJurisdictionChange("international")}
            className={cn(
              "font-ui-label-bold text-ui-label-bold px-4 py-1.5 transition-colors rounded-full text-sm",
              jurisdiction === "international"
                ? "bg-primary-container/10 text-primary-container shadow-sm"
                : "text-secondary hover:text-primary-container hover:bg-surface-container-high/50"
            )}
          >
            🌐 International Treaties
          </button>
        </div>
      </div>

      <div className="flex items-center gap-4">
        {/* Bhashini Language Selector */}
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setLangOpen((o) => !o)}
            className={cn(
              "flex items-center gap-2 px-3 py-1.5 rounded-full border cursor-pointer transition-all shadow-sm text-sm",
              language !== "en"
                ? "bg-teal-500/10 border-teal-500/30 text-teal-700 hover:bg-teal-500/20"
                : "bg-surface-container-low/50 backdrop-blur-sm border-outline-variant/50 text-on-surface hover:bg-surface-container-high"
            )}
          >
            <Globe className="w-4 h-4" />
            <span className="font-ui-label-bold text-ui-label-bold">
              {language === "en"
                ? "Translate (Gemini)"
                : `${currentLang.native} (${currentLang.label})`}
            </span>
            {language !== "en" && (
              <span className="w-1.5 h-1.5 rounded-full bg-teal-500 animate-pulse" />
            )}
            <ChevronDown
              className={cn(
                "w-3.5 h-3.5 transition-transform",
                langOpen && "rotate-180"
              )}
            />
          </button>

          {/* Language Dropdown */}
          {langOpen && (
            <div className="absolute right-0 top-full mt-2 w-52 bg-surface/95 backdrop-blur-md border border-outline-variant/40 rounded-xl shadow-xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-150">
              <div className="px-3 pt-2.5 pb-1">
                <p className="text-xs font-semibold text-secondary uppercase tracking-wider">
                  Gemini Translation
                </p>
                <p className="text-xs text-secondary/70 mt-0.5">
                  {language === "en"
                    ? "Select to enable Gemini translation"
                    : "Active — queries will be auto-translated"}
                </p>
              </div>
              <div className="py-1">
                {LANGUAGES.map((lang) => (
                  <button
                    key={lang.code}
                    onClick={() => {
                      onLanguageChange(lang.code);
                      setLangOpen(false);
                    }}
                    className={cn(
                      "w-full flex items-center justify-between px-3 py-2 text-sm transition-colors",
                      language === lang.code
                        ? "bg-primary-container/10 text-primary-container"
                        : "text-on-surface hover:bg-surface-container-low"
                    )}
                  >
                    <span>
                      <span className="font-medium">{lang.native}</span>
                      <span className="text-secondary ml-1.5 text-xs">
                        {lang.label}
                      </span>
                    </span>
                    {language === lang.code && (
                      <Check className="w-3.5 h-3.5 text-primary-container" />
                    )}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        <button className="text-secondary hover:text-primary-container transition-colors hover:bg-surface-container-high/50 p-2 rounded-full flex items-center justify-center">
          <Bell className="w-5 h-5 font-light" />
        </button>
        <button className="text-secondary hover:text-primary-container transition-colors hover:bg-surface-container-high/50 p-2 rounded-full flex items-center justify-center">
          <Settings className="w-5 h-5 font-light" />
        </button>

        <div className="w-8 h-8 rounded-full overflow-hidden border border-outline-variant/50 ml-2 shadow-sm">
          <img
            alt="User avatar"
            className="w-full h-full object-cover"
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuD-SEycd0Hbc1LdBVZALQICUw_U43oVv2s_7CraEyiAbcYeexorAg_TA_9LOtlOGEkoiHcTsvg-OErwBE7JOkp3b8jUogZT__j9qFwA3kP7NWUSvjv9sEc_Kn7Tn2qgi9J17QaVxrZ3ZY_YyoE-ZlnkomNPCSlFJIrDLCtJpZ_4VrS5EzYmlLVe7iyrVzmGuHBhY9-Ckckvq6pTjoRW9lBfOQAl3xDGssPPZ5VPTt4nJd1DSbqOaubm0Q"
          />
        </div>
      </div>
    </header>
  );
}
