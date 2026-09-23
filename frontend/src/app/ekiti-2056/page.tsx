import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Ekiti 2056 — EKITI@30 DIGITAL",
  description: "Citizen ideas, policy blueprints, and aspirations for the next 30 years.",
};

const pillars = [
  { name: "Knowledge Economy & Tech", count: "48 Ideas" },
  { name: "Agritech & Food Security", count: "34 Ideas" },
  { name: "Eco-Tourism & Heritage", count: "27 Ideas" },
  { name: "Infrastructure & Clean Energy", count: "19 Ideas" },
];

export default function Ekiti2056Page() {
  return (
    <main className="wrap py-12">
      <div className="eyebrow-row">
        <span className="eyebrow-dot"></span> The Next 30 Years
      </div>
      <h1 className="hero-title mt-2">
        Ekiti <em>2056</em>
      </h1>
      <p className="hero-sub max-w-2xl">
        Looking back at 30 years gives us the foundation to look forward. What should
        Ekiti State look like when it turns 60? Submit your blueprint for the future.
      </p>

      {/* Pillar Cards */}
      <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4">
        {pillars.map((pillar) => (
          <div key={pillar.name} className="border border-line rounded-xl p-4">
            <h4 className="font-display font-semibold text-sm">{pillar.name}</h4>
            <span className="text-xs opacity-75 font-mono mt-1 block">{pillar.count}</span>
          </div>
        ))}
      </div>

      {/* Callout Action */}
      <div className="mt-12 border border-line rounded-xl p-8 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div>
          <h3 className="font-display font-bold text-xl">Submit your vision for Ekiti 2056</h3>
          <p className="text-sm opacity-75 mt-1">
            Proposals and ideas will be compiled into the citizen policy archive for Member 8 review.
          </p>
        </div>
        <button className="btn-primary whitespace-nowrap">
          Submit Proposal
        </button>
      </div>
    </main>
  );
}