"use client";

import { AnimatePresence, motion, useAnimationControls } from "motion/react";
import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Spinner } from "@/components/ui/Spinner";
import { SuccessCheck } from "@/components/ui/SuccessCheck";

type Status = "idle" | "submitting" | "success";

export function LoginForm({ callbackUrl }: { callbackUrl: string }) {
  const router = useRouter();
  const card = useAnimationControls();
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setError(null);
    setStatus("submitting");

    let message: string | null = null;
    try {
      const result = await signIn("credentials", {
        email: String(form.get("email") ?? ""),
        password: String(form.get("password") ?? ""),
        redirect: false,
      });
      if (result?.ok && !result.error) {
        setStatus("success");
        // Let the checkmark play before leaving the page.
        setTimeout(() => {
          router.replace(callbackUrl);
          router.refresh();
        }, 900);
        return;
      }
      message =
        result?.error === "CredentialsSignin"
          ? "That email and password don't match an account. Check them and try again."
          : "Sign-in isn't available right now. Please try again in a moment.";
    } catch {
      message = "Couldn't reach the server. Check your connection and try again.";
    }

    setStatus("idle");
    setError(message);
    card.start({ x: [0, -10, 9, -6, 4, 0], transition: { duration: 0.45 } });
  }

  const busy = status !== "idle";

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className="w-full max-w-md"
    >
      <motion.div animate={card} className="form-card overflow-hidden">
        <div className="form-card-band" />
        <div className="px-7 pb-8 pt-7 sm:px-9">
          <AnimatePresence mode="wait" initial={false}>
            {status === "success" ? (
              <motion.div
                key="success"
                initial={{ opacity: 0, scale: 0.96 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex flex-col items-center py-10 text-center"
                role="status"
              >
                <SuccessCheck />
                <p className="mt-5 font-display text-xl text-forest">Ẹ káàbọ̀ — you&apos;re in.</p>
                <p className="mt-1 text-sm text-ink-soft">Taking you to the review desk…</p>
              </motion.div>
            ) : (
              <motion.div key="form" exit={{ opacity: 0, scale: 0.98 }}>
                <div className="eyebrow-row mb-3">
                  <span className="eyebrow-dot" /> Ẹ káàbọ̀ · Welcome back
                </div>
                <h1 className="font-display text-3xl font-medium tracking-tight">
                  Sign in to <em className="text-forest-2">review</em>
                </h1>
                <p className="mt-2 text-sm text-ink-soft">
                  For the EKITI@30 team. Accounts are issued by the project admins — there&apos;s
                  no public sign-up yet.
                </p>

                <form onSubmit={handleSubmit} className="mt-7 flex flex-col gap-5" noValidate>
                  <div className="field">
                    <label htmlFor="email" className="field-label">Email</label>
                    <input
                      id="email"
                      name="email"
                      type="email"
                      autoComplete="email"
                      required
                      disabled={busy}
                      aria-invalid={error ? true : undefined}
                      className="input"
                      placeholder="you@example.com"
                    />
                  </div>

                  <div className="field">
                    <label htmlFor="password" className="field-label">Password</label>
                    <div className="relative">
                      <input
                        id="password"
                        name="password"
                        type={showPassword ? "text" : "password"}
                        autoComplete="current-password"
                        required
                        disabled={busy}
                        aria-invalid={error ? true : undefined}
                        className="input pr-16"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword((v) => !v)}
                        className="absolute inset-y-0 right-2 my-auto h-8 rounded px-2 text-xs font-semibold text-ink-soft hover:text-forest"
                        aria-pressed={showPassword}
                      >
                        {showPassword ? "Hide" : "Show"}
                      </button>
                    </div>
                  </div>

                  <AnimatePresence>
                    {error && (
                      <motion.div
                        key="error"
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        className="overflow-hidden"
                      >
                        <div className="alert alert-error" role="alert">
                          <span aria-hidden="true">●</span>
                          <span>{error}</span>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  <motion.button
                    type="submit"
                    disabled={busy}
                    whileHover={busy ? undefined : { y: -1 }}
                    whileTap={busy ? undefined : { scale: 0.97 }}
                    className="btn-primary mt-1 flex items-center justify-center gap-2"
                  >
                    {status === "submitting" ? (
                      <>
                        <Spinner /> Signing in…
                      </>
                    ) : (
                      "Sign in"
                    )}
                  </motion.button>
                </form>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </motion.div>
  );
}
