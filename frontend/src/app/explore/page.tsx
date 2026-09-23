import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Explore Ekiti — EKITI@30 DIGITAL",
  description: "Interactive directory of the 16 Local Government Areas, landmarks, and institutions.",
};

const lgas = [
  "Ado-Ekiti", "Efon", "Ekiti East", "Ekiti South-West", "Ekiti West", "Emure",
  "Gbonyin", "Ido-Osi", "Ijero", "Ikere", "Ikole", "Ilejemeje", "Irepodun/Ifelodun",
  "Ise/Orun", "Moba", "Oye"
];

const featuredSites = [
  { name: "Ikogosi Warm Springs", lga: "Ekiti West", type: "Natural Wonder", status: "Verified" },
  { name: "Arinta Waterfalls", lga: "Ipole-Iloro", type: "Eco-Tourism", status: "Verified" },
  { name: "Olota of Ikere Palace", lga: "Ikere-Ekiti", type: "Historic Heritage", status: "Single source" },
  { name: "Ewi's Palace", lga: "Ado-Ekiti", type: "Cultural Landmark", status: "Verified" }
];

export default function ExplorePage() {
  return (
    <main className="wrap py-12">
      <div className="eyebrow-row">
        <span className="eyebrow-dot"></span> 16 Local Government Areas & Landmarks
      </div>
      <h1 className="hero-title mt-2">
        Explore <em>Ekiti</em>
      </h1>
      <p className="hero-sub max-w-2xl">
        From the rolling hills of Efon to the springs of Ikogosi, discover the geography,
        heritage, and institutions mapped across our sixteen local governments.
      </p>

      {/* LGA Pills */}
      <div className="mt-8 flex flex-wrap gap-2">
        {lgas.map((lga) => (
          <span key={lga} className="px-3 py-1 text-xs border border-line rounded-full cursor-pointer hover:border-foreground transition">
            {lga}
          </span>
        ))}
      </div>

      {/* Map & Landmark Grid */}
      <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-2 border border-line rounded-xl p-8 min-h-[380px] flex flex-col justify-between">
          <div className="flex justify-between items-center text-xs opacity-75">
            <span>Geospatial Directory Layer</span>
            <span className="status-verified">16 LGAs Mapped</span>
          </div>
          <div className="text-center py-16 opacity-50 font-mono text-sm">
            [ Interactive Leaflet / Mapbox GIS View ]
          </div>
          <div className="text-xs opacity-75">
            Coordinates: 7.6211° N, 5.2215° E • Capital: Ado-Ekiti
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="font-display font-semibold text-lg border-b border-line pb-2">Key Heritage Sites</h3>
          {featuredSites.map((site) => (
            <div key={site.name} className="border border-line rounded-xl p-4">
              <div className="flex justify-between items-start">
                <span className="text-[11px] uppercase tracking-wider opacity-75">{site.type}</span>
                <span className={`text-[10px] ${site.status === "Verified" ? "status-verified" : "status-single"}`}>
                  {site.status}
                </span>
              </div>
              <h4 className="font-semibold text-base mt-2">{site.name}</h4>
              <p className="text-xs opacity-75 mt-1">{site.lga} LGA</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}