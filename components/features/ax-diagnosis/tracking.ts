/**
 * Push AX diagnosis events to the GA4 / GTM data layer when it is present.
 * Used to measure the funnel (start → complete → consultation) and hypothesis H1.
 */
type DataLayerWindow = Window & { dataLayer?: Record<string, unknown>[] };

export function trackAxEvent(event: string, params: Record<string, unknown> = {}): void {
  if (typeof window === 'undefined') return;
  const dataLayer = (window as DataLayerWindow).dataLayer;
  if (Array.isArray(dataLayer)) {
    dataLayer.push({ event, ...params });
  }
}
