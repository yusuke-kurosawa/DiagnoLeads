/**
 * Google Analytics 4 Tracking Integration
 */

import { getClientId } from '../utils/helpers';

export interface GA4Event {
  event_name: string;
  event_params: Record<string, any>;
}

export class GA4Tracker {
  private measurementId: string;
  private clientId: string;
  private enabled: boolean = false;

  constructor(measurementId?: string) {
    this.measurementId = measurementId || '';
    this.clientId = getClientId();
    this.enabled = !!measurementId && typeof window !== 'undefined';

    if (this.enabled) {
      this.initGA4();
    }
  }

  private initGA4(): void {
    // Check if gtag is already loaded
    if (typeof (window as any).gtag !== 'undefined') {
      return;
    }

    // Load Google Analytics script
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${this.measurementId}`;
    document.head.appendChild(script);

    // Initialize gtag
    (window as any).dataLayer = (window as any).dataLayer || [];
    function gtag(...args: any[]) {
      (window as any).dataLayer.push(arguments);
    }
    (window as any).gtag = gtag;

    gtag('js', new Date());
    gtag('config', this.measurementId, {
      send_page_view: false, // Don't auto-send page view
      client_id: this.clientId,
    });
  }

  track(eventName: string, eventParams: Record<string, any> = {}): void {
    if (!this.enabled) {
      console.log('[DiagnoLeads] GA4 tracking disabled');
      return;
    }

    try {
      if (typeof (window as any).gtag !== 'undefined') {
        (window as any).gtag('event', eventName, {
          ...eventParams,
          client_id: this.clientId,
        });
        console.log(`[DiagnoLeads] GA4 event tracked: ${eventName}`, eventParams);
      }
    } catch (error) {
      console.error('[DiagnoLeads] GA4 tracking error:', error);
    }
  }

  // Predefined events for DiagnoLeads widget
  trackWidgetLoaded(assessmentId: string): void {
    this.track('widget_loaded', {
      assessment_id: assessmentId,
      widget_version: '1.0.0',
    });
  }

  trackAssessmentStarted(assessmentId: string, assessmentTitle: string): void {
    this.track('assessment_started', {
      assessment_id: assessmentId,
      assessment_title: assessmentTitle,
    });
  }

  trackQuestionAnswered(
    assessmentId: string,
    questionId: number,
    questionText: string
  ): void {
    this.track('question_answered', {
      assessment_id: assessmentId,
      question_id: questionId,
      question_text: questionText,
    });
  }

  trackAssessmentCompleted(
    assessmentId: string,
    assessmentTitle: string,
    score: number
  ): void {
    this.track('assessment_completed', {
      assessment_id: assessmentId,
      assessment_title: assessmentTitle,
      score: score,
      value: score, // For conversion value
    });
  }

  trackLeadSubmitted(
    assessmentId: string,
    leadEmail: string,
    leadScore: number
  ): void {
    this.track('lead_submitted', {
      assessment_id: assessmentId,
      lead_email_hash: this.hashEmail(leadEmail),
      lead_score: leadScore,
      value: leadScore,
    });
  }

  private hashEmail(email: string): string {
    // Simple hash for privacy - in production, use proper hashing
    let hash = 0;
    for (let i = 0; i < email.length; i++) {
      const char = email.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash).toString(16);
  }
}
