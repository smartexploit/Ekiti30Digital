import Hero from "@/components/Hero";
import LeadersStrip from "@/components/LeadersStrip";
import LandmarksStrip from "@/components/LandmarksStrip";
import MomentsSpine from "@/components/MomentsSpine";
import FeatureGrid from "@/components/FeatureGrid";
import Footer from "@/components/Footer";
import { MyStoryForm } from "@/components/MyStoryForm";

export default function Home() {
  return (
    <>
      <main className="flex-1">
        <Hero />
        <LeadersStrip />
        <LandmarksStrip />
        <MomentsSpine />
        <MyStoryForm />
        <FeatureGrid />
      </main>
      <Footer />
    </>
  );
}
