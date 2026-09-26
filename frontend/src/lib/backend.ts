/**
 * Server-side forwarding to the FastAPI backend.
 *
 * The browser never calls protected backend routes itself: it calls a
 * Next.js route handler, which uses this to attach the signed-in user's
 * token (read from the httpOnly session cookie) and pass the request on.
 */

import { getServerSession } from "next-auth";

import { authOptions, getBackendAuthHeader } from "@/lib/auth";
import { API_URL } from "@/lib/config";

/**
 * POST the incoming request's JSON body to `path` on the backend as the
 * signed-in user, and relay the backend's status and body unchanged.
 */
export async function forwardJsonPost(request: Request, path: string): Promise<Response> {
  if (!(await getServerSession(authOptions))) {
    return Response.json({ detail: "Not signed in" }, { status: 401 });
  }

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return Response.json({ detail: "Request body must be JSON" }, { status: 400 });
  }

  let upstream: Response;
  try {
    upstream = await fetch(`${API_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...(await getBackendAuthHeader()) },
      body: JSON.stringify(body),
      cache: "no-store",
      signal: AbortSignal.timeout(30_000),
    });
  } catch {
    return Response.json({ detail: "The upload service can't be reached" }, { status: 504 });
  }

  return new Response(await upstream.text(), {
    status: upstream.status,
    headers: { "Content-Type": upstream.headers.get("content-type") ?? "application/json" },
  });
}
