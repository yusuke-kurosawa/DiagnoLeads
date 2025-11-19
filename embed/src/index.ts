/**
 * DiagnoLeads Embed Widget - Entry Point
 *
 * Usage:
 * ```html
 * <script src="https://cdn.diagnoleads.com/widget/v1/diagnoleads-widget.umd.js"></script>
 * <diagnoleads-widget
 *   tenant-id="your-tenant-id"
 *   assessment-id="your-assessment-id"
 *   api-url="https://api.diagnoleads.com"
 *   ga4-id="G-XXXXXXXXXX"
 *   theme="light"
 *   primary-color="#3b82f6"
 * ></diagnoleads-widget>
 * ```
 */

import { DiagnoLeadsWidget, WidgetConfig } from './components/DiagnoLeadsWidget';
import { DiagnoLeadsAPI } from './api/client';
import { GA4Tracker } from './tracking/ga4';

// Export for programmatic usage
export { DiagnoLeadsWidget, DiagnoLeadsAPI, GA4Tracker };
export type { WidgetConfig };

// Global initialization function
declare global {
  interface Window {
    DiagnoLeads: {
      Widget: typeof DiagnoLeadsWidget;
      API: typeof DiagnoLeadsAPI;
      Tracker: typeof GA4Tracker;
      version: string;
    };
  }
}

// Set up global namespace
if (typeof window !== 'undefined') {
  window.DiagnoLeads = {
    Widget: DiagnoLeadsWidget,
    API: DiagnoLeadsAPI,
    Tracker: GA4Tracker,
    version: '1.0.0',
  };

  console.log('[DiagnoLeads] Widget v1.0.0 loaded');
}

// Auto-register Web Component
if (typeof customElements !== 'undefined' && !customElements.get('diagnoleads-widget')) {
  customElements.define('diagnoleads-widget', DiagnoLeadsWidget);
}

export default DiagnoLeadsWidget;
