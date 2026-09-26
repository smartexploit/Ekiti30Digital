"use client";

import { motion } from "motion/react";
import { signOut } from "next-auth/react";
import { useState } from "react";

import { Spinner } from "@/components/ui/Spinner";

export function SignOutButton() {
  const [pending, setPending] = useState(false);

  return (
    <motion.button
      type="button"
      disabled={pending}
      whileTap={pending ? undefined : { scale: 0.97 }}
      onClick={() => {
        setPending(true);
        signOut({ callbackUrl: "/login" });
      }}
      className="btn-secondary flex items-center gap-2"
    >
      {pending && <Spinner size={14} />}
      {pending ? "Signing out…" : "Sign out"}
    </motion.button>
  );
}
