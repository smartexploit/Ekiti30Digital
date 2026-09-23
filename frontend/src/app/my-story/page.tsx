import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "My Ekiti Story — EKITI@30 DIGITAL",
  description: "Personal narratives, memories, and reflections from Ekiti people at home and in the diaspora.",
};

const stories = [
  {
    title: "October 1st, 1996 in Ado",
    author: "Dr. B. Adeyemi",
    origin: "Ado-Ekiti",
    year: "1996",
    excerpt: "The morning the announcement came over the radio, people walked into the streets. We were finally our own state...",
    status: "Verified"
  },
  {
    title: "The Warm Waters of Ikogosi",
    author: "Tolulope F.",
    origin: "Ekiti West",
    year: "2004",
    excerpt: "Visiting the confluence where the cold and warm springs meet without ever mixing — that was our childhood classroom...",
    status: "Single source"
  },
  {
    title: "A Legacy in Education",
    author: "Prof. O. Kayode",
    origin: "Ikole",
    year: "2015",
    excerpt: "Every household had books. It wasn't just a cliché; scholarship was the currency of pride in our community...",
    status: "Verified"
  }
];

export default function MyStoryPage() {
  return (
    <main className="wrap py-12">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-8 border-b border-line">
        <div>
          <div className="eyebrow-row">
            <span className="eyebrow-dot"></span> Oral History & Personal Archives
          </div>
          <h1 className="hero-title mt-2">
            My Ekiti <em>Story</em>
          </h1>
          <p className="hero-sub max-w-xl">
            Firsthand memories, family journeys, and personal records spanning thirty years of statehood.
          </p>
        </div>
        <a href="#submit" className="btn-primary self-start md:self-auto">
          Contribute Your Story
        </a>
      </div>

      <div className="mt-10 grid grid-cols-1 md:grid-cols-3 gap-6">
        {stories.map((story, i) => (
          <article key={i} className="border border-line rounded-xl p-6 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between text-xs mb-3">
                <span className="opacity-75 font-mono">{story.year}</span>
                <span className={story.status === "Verified" ? "status-verified" : "status-single"}>
                  {story.status}
                </span>
              </div>
              <h3 className="font-display font-semibold text-lg mb-2">{story.title}</h3>
              <p className="text-sm opacity-80 leading-relaxed">{story.excerpt}</p>
            </div>
            <div className="mt-6 pt-4 border-t border-line flex justify-between text-xs opacity-75">
              <span>{story.author}</span>
              <span>{story.origin}</span>
            </div>
          </article>
        ))}
      </div>
    </main>
  );
}