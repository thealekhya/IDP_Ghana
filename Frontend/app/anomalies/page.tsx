"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import AuthUserMenu from "../AuthUserMenu";

export default function AnomaliesDashboard() {
  const [anomalies, setAnomalies] = useState<any[]>([]);

  useEffect(() => {
    fetch("/anomalies.json")
      .then((res) => res.json())
      .then((data) => setAnomalies(data))
      .catch((err) => console.error("Failed to load anomalies", err));
  }, []);

  const totalFlags = anomalies.length;
  const highSeverity = anomalies.filter((a) => a.severity === "HIGH").length;
  const regionsAffected = new Set(anomalies.map((a) => a.region)).size;

  return (
    <div className="min-h-screen bg-surface text-on-surface relative pb-20">
      {/* Fixed repeating grid background */}
      <div className="fixed inset-0 z-0 opacity-60 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] bg-repeat pointer-events-none"></div>
      
      {/* Background glowing orbs for fancy effect */}
      <div className="fixed top-0 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-[120px] pointer-events-none z-0"></div>
      <div className="fixed bottom-0 right-1/4 w-[500px] h-[500px] bg-secondary/10 rounded-full blur-[150px] pointer-events-none z-0"></div>

      <div className="max-w-[1400px] mx-auto px-4 sm:px-8 pt-8 relative z-10 space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 bg-surface-container-lowest/40 backdrop-blur-xl p-6 rounded-3xl border border-outline-variant/30 shadow-2xl">
          <div className="max-w-2xl">
            <h1 className="text-3xl md:text-5xl font-display font-black text-transparent bg-clip-text bg-gradient-to-br from-primary via-secondary to-tertiary mb-2 tracking-tight">
              Integrity Radar
            </h1>
            <p className="text-on-surface-variant font-body-md text-sm md:text-base leading-relaxed">
              Real-time monitoring of AI-detected medical capability discrepancies. Ensure every hospital actually has the equipment to support their claimed specialties.
            </p>
          </div>
          <div className="flex gap-3 shrink-0 items-center">
            <Link
              href="/map"
              className="px-5 py-2.5 bg-surface-container-high hover:bg-surface-container-highest border border-outline-variant/50 rounded-xl transition-all font-label-sm flex items-center gap-2 shadow-sm hover:shadow-md hover:-translate-y-0.5"
            >
              <span className="material-symbols-outlined text-[18px] text-secondary">map</span>
              Healthcare Map
            </Link>
            <Link
              href="/chat"
              className="px-5 py-2.5 bg-primary text-on-primary rounded-xl hover:bg-primary/90 transition-all font-label-sm flex items-center gap-2 shadow-lg shadow-primary/20 hover:shadow-xl hover:-translate-y-0.5"
            >
              <span className="material-symbols-outlined text-[18px]">chat</span>
              AI Agent
            </Link>
            <AuthUserMenu />
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div className="bg-surface-container-lowest/60 backdrop-blur-lg p-6 rounded-3xl border border-outline-variant/30 shadow-xl hover:shadow-2xl transition-all flex flex-col gap-3 relative overflow-hidden group">
            <div className="absolute -inset-4 bg-gradient-to-br from-primary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="flex items-center gap-2 text-on-surface-variant z-10">
              <span className="material-symbols-outlined text-primary p-1.5 bg-primary/10 rounded-lg text-sm">flag</span>
              <span className="font-label-sm uppercase tracking-widest font-bold text-xs">Total Flags</span>
            </div>
            <span className="text-5xl font-display font-black text-on-surface z-10">{totalFlags}</span>
          </div>

          <div className="bg-error-container/20 backdrop-blur-lg p-6 rounded-3xl border border-error/20 shadow-xl hover:shadow-2xl transition-all flex flex-col gap-3 relative overflow-hidden group">
            <div className="absolute -inset-4 bg-gradient-to-br from-error/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="flex items-center gap-2 text-error z-10">
              <span className="material-symbols-outlined p-1.5 bg-error/10 rounded-lg text-sm">gpp_bad</span>
              <span className="font-label-sm uppercase tracking-widest font-bold text-xs">High Severity</span>
            </div>
            <span className="text-5xl font-display font-black text-error z-10">{highSeverity}</span>
          </div>

          <div className="bg-surface-container-lowest/60 backdrop-blur-lg p-6 rounded-3xl border border-outline-variant/30 shadow-xl hover:shadow-2xl transition-all flex flex-col gap-3 relative overflow-hidden group">
            <div className="absolute -inset-4 bg-gradient-to-br from-secondary/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <div className="flex items-center gap-2 text-on-surface-variant z-10">
              <span className="material-symbols-outlined text-secondary p-1.5 bg-secondary/10 rounded-lg text-sm">my_location</span>
              <span className="font-label-sm uppercase tracking-widest font-bold text-xs">Regions Affected</span>
            </div>
            <span className="text-5xl font-display font-black text-on-surface z-10">{regionsAffected}</span>
          </div>
        </div>

        {/* Data Table */}
        <div className="bg-surface-container-lowest/80 backdrop-blur-xl rounded-3xl overflow-hidden border border-outline-variant/30 shadow-2xl">
          <div className="px-6 py-4 border-b border-outline-variant/30 bg-surface-dim/20 flex justify-between items-center">
            <h2 className="font-display text-xl font-bold flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-[20px]">data_alert</span>
              Anomaly Log
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[900px]">
              <thead>
                <tr className="bg-surface-dim/40">
                  <th className="p-4 pl-6 font-label-sm uppercase tracking-widest text-on-surface-variant font-bold text-[10px]">Facility Name</th>
                  <th className="p-4 font-label-sm uppercase tracking-widest text-on-surface-variant font-bold text-[10px]">Location</th>
                  <th className="p-4 font-label-sm uppercase tracking-widest text-on-surface-variant font-bold text-[10px] text-center">Claimed Specialty</th>
                  <th className="p-4 font-label-sm uppercase tracking-widest text-on-surface-variant font-bold text-[10px] w-[35%]">AI Resolution Details</th>
                  <th className="p-4 pr-6 font-label-sm uppercase tracking-widest text-on-surface-variant font-bold text-[10px] text-right">Severity</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/20">
                {anomalies.map((a, idx) => (
                  <tr key={idx} className="hover:bg-surface-container-low/50 transition-colors group">
                    <td className="p-4 pl-6 align-top">
                      <strong className="block font-headline-sm text-sm text-on-surface mb-0.5 group-hover:text-primary transition-colors">
                        {a.facility_name}
                      </strong>
                      <span className="inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider text-on-surface-variant bg-surface-dim px-2 py-0.5 rounded-md">
                        {a.facility_type}
                      </span>
                    </td>
                    <td className="p-4 align-top">
                      <div className="flex flex-col gap-0.5">
                        <span className="font-body-sm font-medium text-sm">{a.city}</span>
                        <span className="text-[11px] text-on-surface-variant">{a.region}</span>
                      </div>
                    </td>
                    <td className="p-4 align-top text-center">
                      <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border border-outline-variant/30 bg-surface shadow-sm font-label-sm font-bold text-on-surface text-xs tracking-wide">
                        <div className="w-1.5 h-1.5 rounded-full bg-secondary shadow-[0_0_6px_rgba(var(--secondary-rgb),0.8)]"></div>
                        {a.claimed_specialty}
                      </div>
                    </td>
                    <td className="p-4 align-top">
                      <div className="bg-error-container/10 border border-error/10 p-2.5 rounded-xl">
                        <p className="font-body-sm text-on-surface text-xs leading-relaxed flex items-start gap-2">
                          <span className="material-symbols-outlined text-error text-[16px] shrink-0">info</span>
                          {a.reason}
                        </p>
                      </div>
                    </td>
                    <td className="p-4 pr-6 align-top text-right">
                      {a.severity === "HIGH" ? (
                        <span className="inline-flex items-center justify-center gap-1 text-error font-bold text-[11px] bg-error-container/30 border border-error/20 px-2 py-1 rounded-md shadow-sm">
                          <span className="material-symbols-outlined text-[12px]">cancel</span> HIGH
                        </span>
                      ) : (
                        <span className="inline-flex items-center justify-center gap-1 text-orange-500 font-bold text-[11px] bg-orange-500/10 border border-orange-500/20 px-2 py-1 rounded-md shadow-sm">
                          <span className="material-symbols-outlined text-[12px]">warning</span> MEDIUM
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
                {anomalies.length === 0 && (
                  <tr>
                    <td colSpan={5} className="p-12 text-center text-on-surface-variant font-body-sm">
                      <span className="material-symbols-outlined text-3xl mb-3 block opacity-50">data_exploration</span>
                      Scanning database for anomalies...
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
