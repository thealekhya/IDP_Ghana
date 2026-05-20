"use client";
import Link from "next/link";
import dynamic from "next/dynamic";
import { useState, useEffect, useMemo, useRef } from "react";
import AuthUserMenu from "../AuthUserMenu";

const LeafletMap = dynamic(() => import("./LeafletMap"), { ssr: false });

export default function MapPage() {
  const [hospitals, setHospitals] = useState<any[]>([]);
  
  // Filter states
  const [openDropdown, setOpenDropdown] = useState<"capabilities" | "equipment" | "procedure" | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedFilters, setSelectedFilters] = useState<{
    capabilities: string | null;
    equipment: string | null;
    procedure: string | null;
  }>({
    capabilities: null,
    equipment: null,
    procedure: null
  });
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch('/hospitals_data.json')
      .then(res => res.json())
      .then(data => setHospitals(data))
      .catch(err => console.error(err));
  }, []);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setOpenDropdown(null);
        setSearchQuery("");
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  // Extract unique lists for dropdowns — filter out empty/noise strings
  const options = useMemo(() => {
    const caps = new Set<string>();
    const equip = new Set<string>();
    const proc = new Set<string>();
    
    hospitals.forEach(h => {
      if (h.capabilities && Array.isArray(h.capabilities)) h.capabilities.forEach((x: string) => { if (x && x.trim().length > 3) caps.add(x); });
      if (h.equipment && Array.isArray(h.equipment)) h.equipment.forEach((x: string) => { if (x && x.trim().length > 3) equip.add(x); });
      if (h.procedure && Array.isArray(h.procedure)) h.procedure.forEach((x: string) => { if (x && x.trim().length > 3) proc.add(x); });
    });
    
    return {
      capabilities: Array.from(caps).sort(),
      equipment: Array.from(equip).sort(),
      procedure: Array.from(proc).sort()
    };
  }, [hospitals]);

  // Apply filters
  const activeHospitals = useMemo(() => {
    return hospitals.filter(h => {
      let pass = true;
      if (selectedFilters.capabilities) {
        if (!h.capabilities || !h.capabilities.includes(selectedFilters.capabilities)) pass = false;
      }
      if (selectedFilters.equipment) {
        if (!h.equipment || !h.equipment.includes(selectedFilters.equipment)) pass = false;
      }
      if (selectedFilters.procedure) {
        if (!h.procedure || !h.procedure.includes(selectedFilters.procedure)) pass = false;
      }
      return pass;
    });
  }, [hospitals, selectedFilters]);

  const toggleDropdown = (type: "capabilities" | "equipment" | "procedure") => {
    setOpenDropdown(openDropdown === type ? null : type);
    setSearchQuery("");
  };

  const selectFilter = (type: "capabilities" | "equipment" | "procedure", val: string | null) => {
    setSelectedFilters(prev => ({ ...prev, [type]: val }));
    setOpenDropdown(null);
    setSearchQuery("");
  };

  // Filter dropdown options by search query
  const getFilteredOptions = (type: "capabilities" | "equipment" | "procedure") => {
    const list = options[type];
    if (!searchQuery) return list.slice(0, 80); // cap at 80 for perf
    return list.filter(o => o.toLowerCase().includes(searchQuery.toLowerCase())).slice(0, 80);
  };

  // Truncate helper
  const truncate = (str: string, max: number) => str.length > max ? str.substring(0, max) + "…" : str;

  // Active filter count
  const activeFilterCount = [selectedFilters.capabilities, selectedFilters.equipment, selectedFilters.procedure].filter(Boolean).length;

  return (
    <div className="bg-background text-on-background font-body-md text-body-md h-screen overflow-hidden flex flex-col antialiased">
      {/* TopNavBar (Mobile Only) */}
      <nav className="md:hidden bg-surface/80 dark:bg-surface-dim/80 backdrop-blur-md border-b border-outline-variant/30 fixed top-0 left-0 w-full z-50 flex justify-between items-center px-4 h-16">
        <div className="font-headline-md text-headline-md font-bold text-primary dark:text-primary-fixed-dim tracking-tight">
          Sankofa AI
        </div>
        <div className="flex gap-4">
          <AuthUserMenu />
        </div>
      </nav>

      <div className="flex flex-1 h-full pt-16 md:pt-0">
        {/* SideNavBar (Desktop) */}
        <aside className="hidden lg:flex flex-col h-full fixed left-0 top-0 pt-20 pb-8 px-4 w-64 z-40 bg-surface-container-low dark:bg-inverse-surface border-r border-outline-variant/20">
          <div className="flex items-center gap-3 mb-8">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              alt="Sankofa Bird Logo"
              className="w-8 h-8 object-cover rounded-sm"
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuAum3m4zs7-RJwCvcE-JhB52nMps1jxy5l6iws17tBu7dqk-2DBg_g9DMWGtUplT-8rBP24vOEiCssdLx_z5p0vVGVrE7blpPfqn4ZxMS7RlN9ZdZmoNL4myqjDp5a8AysE-PzNu5cgBVJ22l02Hk40awEKg157eHAff7lDCcjfJWwdOZpYID1ENseIzcAsQi-xx78TpgAP8L164Q0o07wrvIaz-TObPX6mDkip4L8bb-18SEMZky5Q6QQnB2YVfnz7dWXKZb2HtAEn"
            />
            <div>
              <h1 className="font-headline-md text-[20px] leading-[28px] font-bold text-primary dark:text-primary-fixed-dim">
                Sankofa AI
              </h1>
              <p className="font-label-sm text-label-sm text-on-surface-variant">
                Ghana Medical Intelligence
              </p>
            </div>
          </div>
          <nav className="flex-1 flex flex-col gap-2">
            <Link className="flex items-center gap-3 px-3 py-2 text-on-surface-variant hover:bg-surface-container-high transition-all rounded-lg" href="/chat">
              <span className="material-symbols-outlined">add_comment</span>
              <span className="font-label-sm uppercase tracking-wider">New Chat</span>
            </Link>
            <Link className="flex items-center gap-3 px-3 py-2 bg-secondary-container text-on-secondary-container rounded-lg font-bold translate-x-1 transition-transform" href="/map">
              <span className="material-symbols-outlined">map</span>
              <span className="font-label-sm uppercase tracking-wider">Healthcare Map</span>
            </Link>
            <Link className="flex items-center gap-3 px-3 py-2 text-on-surface-variant hover:bg-surface-container-high transition-all rounded-lg" href="/anomalies">
              <span className="material-symbols-outlined">data_alert</span>
              <span className="font-label-sm uppercase tracking-wider">Data Integrity</span>
            </Link>
            <Link className="flex items-center gap-3 px-3 py-2 text-on-surface-variant hover:bg-surface-container-high transition-all rounded-lg" href="/home">
              <span className="material-symbols-outlined">analytics</span>
              <span className="font-label-sm uppercase tracking-wider">Data Insights</span>
            </Link>
          </nav>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 flex flex-col lg:ml-64 relative h-full">
          <div className="hidden md:flex absolute top-4 right-4 z-30 items-center gap-3">
            <AuthUserMenu />
          </div>

          {/* Map Container */}
          <div className="absolute inset-0 z-0 bg-surface-container-high">
            <LeafletMap activeHospitals={activeHospitals} totalCount={hospitals.length} />
            <div className="absolute inset-0 bg-surface/20 pointer-events-none mix-blend-overlay"></div>
          </div>

          {/* === LAYER 1: Map Insights Panel (z-10) === */}
          <div className="absolute top-4 right-4 bottom-4 z-10 pointer-events-none flex flex-col gap-4 w-80 hidden md:flex">
            {/* Spacer so panel starts below filters */}
            <div className="h-14 shrink-0"></div>
            <div className="pointer-events-auto flex-1 bg-surface/90 backdrop-blur-xl border border-outline-variant/30 rounded-xl shadow-lg flex flex-col overflow-hidden">
              <div className="p-4 border-b border-outline-variant/20 flex justify-between items-center bg-surface">
                <h2 className="font-headline-md text-[20px] leading-[28px] text-on-surface">
                  Map Insights
                </h2>
                <span className="bg-primary/10 text-primary px-3 py-1 rounded-full text-xs font-bold">
                  {activeHospitals.length} Results
                </span>
              </div>
              <div className="p-4 overflow-y-auto flex-1 flex flex-col gap-6">
                {/* Active Filters Summary */}
                {activeFilterCount > 0 && (
                  <section>
                    <h3 className="font-label-sm text-[11px] text-on-surface-variant mb-2 uppercase tracking-wider">Active Filters</h3>
                    <div className="flex flex-wrap gap-1.5">
                      {selectedFilters.capabilities && (
                        <span className="bg-secondary-container text-on-secondary-container px-2 py-1 rounded-lg text-[10px] flex items-center gap-1">
                          <span className="font-bold">Cap:</span> {truncate(selectedFilters.capabilities, 25)}
                          <button onClick={() => selectFilter("capabilities", null)} className="ml-1 hover:text-error">✕</button>
                        </span>
                      )}
                      {selectedFilters.equipment && (
                        <span className="bg-secondary-container text-on-secondary-container px-2 py-1 rounded-lg text-[10px] flex items-center gap-1">
                          <span className="font-bold">Equip:</span> {truncate(selectedFilters.equipment, 25)}
                          <button onClick={() => selectFilter("equipment", null)} className="ml-1 hover:text-error">✕</button>
                        </span>
                      )}
                      {selectedFilters.procedure && (
                        <span className="bg-secondary-container text-on-secondary-container px-2 py-1 rounded-lg text-[10px] flex items-center gap-1">
                          <span className="font-bold">Proc:</span> {truncate(selectedFilters.procedure, 25)}
                          <button onClick={() => selectFilter("procedure", null)} className="ml-1 hover:text-error">✕</button>
                        </span>
                      )}
                    </div>
                  </section>
                )}
                {/* Risk Regions */}
                <section>
                  <h3 className="font-label-sm text-[11px] text-on-surface-variant mb-3 uppercase tracking-wider">
                    Top Regions at Risk
                  </h3>
                  <ul className="flex flex-col gap-2">
                    <li className="flex justify-between items-center p-2 rounded hover:bg-surface-container-low transition-colors cursor-pointer group">
                      <span className="font-body-md text-sm text-on-surface group-hover:text-primary transition-colors">Northern Region</span>
                      <span className="bg-error-container text-on-error-container px-2 py-0.5 rounded font-label-sm text-[10px]">High</span>
                    </li>
                    <li className="flex justify-between items-center p-2 rounded hover:bg-surface-container-low transition-colors cursor-pointer group">
                      <span className="font-body-md text-sm text-on-surface group-hover:text-primary transition-colors">Upper East</span>
                      <span className="bg-tertiary-container text-on-tertiary-container px-2 py-0.5 rounded font-label-sm text-[10px]">Critical</span>
                    </li>
                    <li className="flex justify-between items-center p-2 rounded hover:bg-surface-container-low transition-colors cursor-pointer group">
                      <span className="font-body-md text-sm text-on-surface group-hover:text-primary transition-colors">Volta Region</span>
                      <span className="bg-secondary-container text-on-secondary-container px-2 py-0.5 rounded font-label-sm text-[10px]">Watch</span>
                    </li>
                  </ul>
                </section>
                <hr className="border-outline-variant/20" />
                {/* Facility Stats */}
                <section>
                  <h3 className="font-label-sm text-[11px] text-on-surface-variant mb-3 uppercase tracking-wider">
                    Facility Statistics
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-surface-container-lowest p-3 rounded-lg border border-outline-variant/30 text-center">
                      <div className="font-display text-3xl font-bold text-tertiary">42</div>
                      <div className="font-label-sm text-[10px] text-on-surface-variant mt-1 uppercase tracking-wider">Suspicious</div>
                    </div>
                    <div className="bg-surface-container-lowest p-3 rounded-lg border border-outline-variant/30 text-center">
                      <div className="font-display text-3xl font-bold text-primary">156</div>
                      <div className="font-label-sm text-[10px] text-on-surface-variant mt-1 uppercase tracking-wider">Deserts</div>
                    </div>
                  </div>
                </section>
              </div>
            </div>
          </div>

          {/* === LAYER 2: Filter Dropdowns (z-20, above Map Insights) === */}
          <div ref={dropdownRef} className="absolute top-4 right-4 z-20 flex gap-3 items-start">
            
            {/* Clear All (only when filters active) */}
            {activeFilterCount > 0 && (
              <button 
                onClick={() => { setSelectedFilters({ capabilities: null, equipment: null, procedure: null }); }}
                className="bg-error/90 text-on-error px-3 py-2 rounded-full text-[11px] uppercase tracking-wider font-bold shadow-lg hover:bg-error transition-all flex items-center gap-1"
              >
                <span className="material-symbols-outlined text-[14px]">close</span>
                Clear
              </button>
            )}

            {/* Capability Dropdown */}
            <div className="relative">
              <button 
                onClick={() => toggleDropdown("capabilities")}
                className={`border px-4 py-2 rounded-full font-label-sm text-[11px] uppercase tracking-wider flex items-center gap-2 transition-all shadow-lg ${selectedFilters.capabilities ? 'bg-secondary text-on-secondary border-secondary' : 'bg-surface text-on-surface border-outline-variant hover:bg-surface-container'}`}
              >
                Capability
                <span className="material-symbols-outlined text-[16px]">{openDropdown === 'capabilities' ? 'arrow_drop_up' : 'arrow_drop_down'}</span>
              </button>
              {openDropdown === "capabilities" && (
                <div className="absolute top-full right-0 mt-2 w-80 bg-surface border border-outline-variant/50 rounded-xl shadow-2xl flex flex-col max-h-[400px] overflow-hidden">
                  {/* Search */}
                  <div className="p-2 border-b border-outline-variant/20">
                    <input
                      type="text"
                      placeholder="Search capabilities…"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-full bg-surface-container-low border border-outline-variant/30 rounded-lg px-3 py-2 text-xs text-on-surface placeholder:text-on-surface-variant/50 outline-none focus:border-primary"
                      autoFocus
                    />
                  </div>
                  <div className="overflow-y-auto flex-1 custom-scrollbar">
                    <button onClick={() => selectFilter("capabilities", null)} className="w-full text-left px-4 py-2.5 text-xs border-b border-outline-variant/10 hover:bg-surface-container-low font-bold text-primary">
                      ← Show All Facilities
                    </button>
                    {getFilteredOptions("capabilities").map(opt => (
                      <button key={opt} onClick={() => selectFilter("capabilities", opt)} className={`w-full text-left px-4 py-2 text-xs hover:bg-surface-container-low transition-colors ${selectedFilters.capabilities === opt ? 'bg-secondary-container/50 font-bold text-on-secondary-container' : 'text-on-surface'}`}>
                        {truncate(opt, 60)}
                      </button>
                    ))}
                    {getFilteredOptions("capabilities").length === 0 && (
                      <div className="px-4 py-6 text-xs text-on-surface-variant italic text-center">No matches found</div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Equipment Dropdown */}
            <div className="relative">
              <button 
                onClick={() => toggleDropdown("equipment")}
                className={`border px-4 py-2 rounded-full font-label-sm text-[11px] uppercase tracking-wider flex items-center gap-2 transition-all shadow-lg ${selectedFilters.equipment ? 'bg-secondary text-on-secondary border-secondary' : 'bg-surface text-on-surface border-outline-variant hover:bg-surface-container'}`}
              >
                Equipment
                <span className="material-symbols-outlined text-[16px]">{openDropdown === 'equipment' ? 'arrow_drop_up' : 'arrow_drop_down'}</span>
              </button>
              {openDropdown === "equipment" && (
                <div className="absolute top-full right-0 mt-2 w-80 bg-surface border border-outline-variant/50 rounded-xl shadow-2xl flex flex-col max-h-[400px] overflow-hidden">
                  <div className="p-2 border-b border-outline-variant/20">
                    <input
                      type="text"
                      placeholder="Search equipment…"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-full bg-surface-container-low border border-outline-variant/30 rounded-lg px-3 py-2 text-xs text-on-surface placeholder:text-on-surface-variant/50 outline-none focus:border-primary"
                      autoFocus
                    />
                  </div>
                  <div className="overflow-y-auto flex-1 custom-scrollbar">
                    <button onClick={() => selectFilter("equipment", null)} className="w-full text-left px-4 py-2.5 text-xs border-b border-outline-variant/10 hover:bg-surface-container-low font-bold text-primary">
                      ← Show All Facilities
                    </button>
                    {getFilteredOptions("equipment").map(opt => (
                      <button key={opt} onClick={() => selectFilter("equipment", opt)} className={`w-full text-left px-4 py-2 text-xs hover:bg-surface-container-low transition-colors ${selectedFilters.equipment === opt ? 'bg-secondary-container/50 font-bold text-on-secondary-container' : 'text-on-surface'}`}>
                        {truncate(opt, 60)}
                      </button>
                    ))}
                    {getFilteredOptions("equipment").length === 0 && (
                      <div className="px-4 py-6 text-xs text-on-surface-variant italic text-center">No matches found</div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Procedure Dropdown */}
            <div className="relative">
              <button 
                onClick={() => toggleDropdown("procedure")}
                className={`border px-4 py-2 rounded-full font-label-sm text-[11px] uppercase tracking-wider flex items-center gap-2 transition-all shadow-lg ${selectedFilters.procedure ? 'bg-secondary text-on-secondary border-secondary' : 'bg-surface text-on-surface border-outline-variant hover:bg-surface-container'}`}
              >
                Procedure
                <span className="material-symbols-outlined text-[16px]">{openDropdown === 'procedure' ? 'arrow_drop_up' : 'arrow_drop_down'}</span>
              </button>
              {openDropdown === "procedure" && (
                <div className="absolute top-full right-0 mt-2 w-80 bg-surface border border-outline-variant/50 rounded-xl shadow-2xl flex flex-col max-h-[400px] overflow-hidden">
                  <div className="p-2 border-b border-outline-variant/20">
                    <input
                      type="text"
                      placeholder="Search procedures…"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-full bg-surface-container-low border border-outline-variant/30 rounded-lg px-3 py-2 text-xs text-on-surface placeholder:text-on-surface-variant/50 outline-none focus:border-primary"
                      autoFocus
                    />
                  </div>
                  <div className="overflow-y-auto flex-1 custom-scrollbar">
                    <button onClick={() => selectFilter("procedure", null)} className="w-full text-left px-4 py-2.5 text-xs border-b border-outline-variant/10 hover:bg-surface-container-low font-bold text-primary">
                      ← Show All Facilities
                    </button>
                    {getFilteredOptions("procedure").map(opt => (
                      <button key={opt} onClick={() => selectFilter("procedure", opt)} className={`w-full text-left px-4 py-2 text-xs hover:bg-surface-container-low transition-colors ${selectedFilters.procedure === opt ? 'bg-secondary-container/50 font-bold text-on-secondary-container' : 'text-on-surface'}`}>
                        {truncate(opt, 60)}
                      </button>
                    ))}
                    {getFilteredOptions("procedure").length === 0 && (
                      <div className="px-4 py-6 text-xs text-on-surface-variant italic text-center">No matches found</div>
                    )}
                  </div>
                </div>
              )}
            </div>

          </div>
        </main>
      </div>
    </div>
  );
}
