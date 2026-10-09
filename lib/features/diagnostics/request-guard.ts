import { type NextRequest, NextResponse } from 'next/server';

/**
 * Basic checks for the public diagnosis endpoints (no authentication):
 * - JSON only (rejects text/plain "simple requests" that cross-site forms can send)
 * - same-origin only when the browser sends an Origin header
 * - bounded body size
 * Returns an error response, or null when the request may proceed.
 */
export function checkPublicJsonRequest(req: NextRequest, maxBytes: number): NextResponse | null {
  const contentType = req.headers.get('content-type') ?? '';
  if (!contentType.toLowerCase().startsWith('application/json')) {
    return NextResponse.json({ error: 'Unsupported Media Type' }, { status: 415 });
  }

  const origin = req.headers.get('origin');
  if (origin && !isAllowedOrigin(origin, req)) {
    return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
  }

  const length = Number(req.headers.get('content-length') ?? '0');
  if (Number.isFinite(length) && length > maxBytes) {
    return NextResponse.json({ error: 'Payload Too Large' }, { status: 413 });
  }

  return null;
}

function isAllowedOrigin(origin: string, req: NextRequest): boolean {
  let originHost: string;
  try {
    originHost = new URL(origin).host;
  } catch {
    return false;
  }
  const allowed = new Set<string>([req.nextUrl.host]);
  const forwardedHost = req.headers.get('x-forwarded-host');
  if (forwardedHost) allowed.add(forwardedHost);
  const appUrl = process.env.NEXT_PUBLIC_APP_URL;
  if (appUrl) {
    try {
      allowed.add(new URL(appUrl).host);
    } catch {
      // ignore malformed configuration
    }
  }
  return allowed.has(originHost);
}
