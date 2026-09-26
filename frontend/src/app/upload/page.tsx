import type { Metadata } from "next";
import { getServerSession } from "next-auth";
import { redirect } from "next/navigation";

import { UploadForm } from "@/components/upload/UploadForm";
import { authOptions } from "@/lib/auth";

export const metadata: Metadata = {
  title: "Share a photo or video — EKITI@30 DIGITAL",
  robots: { index: false },
};

export default async function UploadPage() {
  if (!(await getServerSession(authOptions))) redirect("/login?callbackUrl=/upload");

  return (
    <main className="adire-bg flex flex-1 items-start justify-center px-4 py-12 sm:px-5 sm:py-16">
      <UploadForm />
    </main>
  );
}
