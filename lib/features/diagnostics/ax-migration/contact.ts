/**
 * Contact field rules shared by the form (browser) and the API (server)
 */

/** Full-width digits and long-vowel dashes typed with a Japanese IME still make a phone number */
export const normalizePhone = (value: string) =>
  value
    .normalize('NFKC')
    .replace(/[ー‐‑–—―−]/g, '-')
    .trim();

export const PHONE_PATTERN = /^[0-9+\-() ]*$/;
