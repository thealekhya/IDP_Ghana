"use client";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { useEffect, useRef } from "react";

// Helper to create custom HTML markers with a 3D-styled SVG icon
const createCustomIcon = (isActive: boolean) => {
  // Red gradient for active, dark metallic gray for inactive
  const stop1 = isActive ? "#ff7eb3" : "#94a3b8";
  const stop2 = isActive ? "#ff0844" : "#475569";
  const stop3 = isActive ? "#b2002d" : "#1e293b";
  const innerColor = isActive ? "#ff7eb3" : "#cbd5e1";

  const svgIcon = `
    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="pinGradient-${isActive}" x1="20%" y1="0%" x2="80%" y2="100%">
          <stop offset="0%" stop-color="${stop1}" />
          <stop offset="50%" stop-color="${stop2}" />
          <stop offset="100%" stop-color="${stop3}" />
        </linearGradient>
        <filter id="shadow-${isActive}" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="6" stdDeviation="4" flood-color="#000000" flood-opacity="0.7"/>
          <feDropShadow dx="0" dy="1" stdDeviation="1" flood-color="#000000" flood-opacity="0.9"/>
        </filter>
        <radialGradient id="highlight-${isActive}" cx="30%" cy="30%" r="50%">
          <stop offset="0%" stop-color="#ffffff" stop-opacity="0.6"/>
          <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
        </radialGradient>
      </defs>
      
      <!-- Base Pin Shape -->
      <path d="M12 2C7.58 2 4 5.58 4 10C4 15.25 12 22 12 22C12 22 20 15.25 20 10C20 5.58 16.42 2 12 2Z" fill="url(#pinGradient-${isActive})" filter="url(#shadow-${isActive})"/>
      
      <!-- 3D Glossy Highlight -->
      <path d="M12 2C7.58 2 4 5.58 4 10C4 15.25 12 22 12 22C12 22 20 15.25 20 10C20 5.58 16.42 2 12 2Z" fill="url(#highlight-${isActive})"/>
      
      <!-- Inner Dark Hole / Pulse effect -->
      <circle cx="12" cy="10" r="3.5" fill="#111111" />
      <circle cx="12" cy="10" r="1.5" fill="${innerColor}" />
    </svg>
  `;

  return L.divIcon({
    className: 'custom-leaflet-icon bg-transparent border-none',
    html: `<div class="transition-transform hover:scale-125 cursor-pointer" style="transform-origin: bottom center;">${svgIcon}</div>`,
    iconSize: [40, 40],
    iconAnchor: [20, 38], // Anchor precisely at the bottom tip
  });
};

function HospitalMarkers({ activeHospitals }: { activeHospitals: any[] }) {
  const map = useMap();

  return (
    <>
      {activeHospitals.map(hospital => {
        // For the UI demo, we simulate ~25% of hospitals being inactive based on their ID
        const isActive = hospital.id % 4 !== 0;
        const statusText = isActive ? "Active Service - Providing Care" : "Inactive - Service Disrupted";
        
        return (
          <Marker 
            key={hospital.id} 
            position={[hospital.lat, hospital.lng]} 
            icon={createCustomIcon(isActive)}
            eventHandlers={{
              click: () => {
                map.flyTo([hospital.lat, hospital.lng], 14, {
                  animate: true,
                  duration: 1.5
                });
              }
            }}
          >
            <Popup minWidth={260} maxWidth={320}>
              <div className="flex flex-col text-gray-800 -m-1 font-sans">
                <strong className="text-lg font-bold mb-1 leading-tight text-gray-900">{hospital.name}</strong>
                <span className={`text-[10px] font-bold uppercase tracking-wider ${isActive ? 'text-green-600' : 'text-red-600'} flex items-center gap-1 mb-2`}>
                   {isActive ? '●' : '▲'} {statusText}
                </span>
                
                <div className="border-t border-gray-200 my-2"></div>
                
                {(hospital.phone || hospital.email) && (
                  <div className="flex flex-col gap-1.5 mb-3 text-sm">
                    {hospital.phone && (
                      <div className="flex items-center gap-2 text-gray-700">
                        📞 {hospital.phone}
                      </div>
                    )}
                    {hospital.email && (
                      <div className="flex items-center gap-2">
                        ✉️ <a href={`mailto:${hospital.email}`} className="text-blue-600 hover:underline">{hospital.email}</a>
                      </div>
                    )}
                  </div>
                )}
                
                {hospital.specialties && hospital.specialties.length > 0 && (
                  <div className="mb-3">
                    <span className="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1.5">Services & Specialties</span>
                    <div className="flex flex-wrap gap-1.5">
                      {hospital.specialties.slice(0, 6).map((spec: string, idx: number) => (
                        <span key={idx} className="bg-gray-100 border border-gray-200 px-2 py-0.5 rounded-md text-xs text-gray-700">
                          {spec.replace(/([A-Z])/g, ' $1').replace(/^./, (str) => str.toUpperCase()).trim()}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </Popup>
          </Marker>
        );
      })}
    </>
  );
}

// Auto-fit the map viewport to show all filtered markers
function FitBounds({ hospitals, totalCount }: { hospitals: any[]; totalCount: number }) {
  const map = useMap();
  const isInitialLoad = useRef(true);
  const prevLength = useRef(hospitals.length);

  useEffect(() => {
    // Skip the very first render (initial data load)
    if (isInitialLoad.current) {
      isInitialLoad.current = false;
      prevLength.current = hospitals.length;
      return;
    }

    // Only fly when the set of hospitals actually changed
    if (hospitals.length === prevLength.current) return;
    prevLength.current = hospitals.length;

    if (hospitals.length === 0) return;

    // If showing all hospitals again, reset to Ghana overview
    if (hospitals.length === totalCount) {
      map.flyTo([7.9465, -1.0232], 6.5, { animate: true, duration: 1.2 });
      return;
    }

    // If only 1 result, fly directly to it
    if (hospitals.length === 1) {
      map.flyTo([hospitals[0].lat, hospitals[0].lng], 12, { animate: true, duration: 1.5 });
      return;
    }

    // Multiple results: compute bounds and fly to fit them
    const bounds = L.latLngBounds(
      hospitals.map(h => [h.lat, h.lng] as [number, number])
    );
    map.flyToBounds(bounds, {
      padding: [60, 60],
      maxZoom: 13,
      animate: true,
      duration: 1.5
    });
  }, [hospitals, totalCount, map]);

  return null;
}

export default function LeafletMap({ activeHospitals = [], totalCount = 0 }: { activeHospitals?: any[]; totalCount?: number }) {
  const maptilerKey = process.env.NEXT_PUBLIC_MAPTILER_KEY || "";
  const mapStyle = "hybrid"; 
  
  const ghanaCenter: [number, number] = [7.9465, -1.0232];

  return (
    <MapContainer
      center={ghanaCenter}
      zoom={6.5}
      style={{ width: "100%", height: "100%", zIndex: 0 }}
      zoomControl={false}
      attributionControl={false}
    >
      <TileLayer
        url={`https://api.maptiler.com/maps/${mapStyle}/256/{z}/{x}/{y}.jpg?key=${maptilerKey}`}
      />
      <HospitalMarkers activeHospitals={activeHospitals} />
      <FitBounds hospitals={activeHospitals} totalCount={totalCount} />
    </MapContainer>
  );
}
