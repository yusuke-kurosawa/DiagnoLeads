/**
 * useGoogleAnalytics Hook
 *
 * Custom hook for Google Analytics 4 tracking in DiagnoLeads.
 * Automatically initializes GA4 with tenant's configuration.
 */
import { useEffect, useCallback } from 'react';
import ReactGA from 'react-ga4';
import { useAuthStore } from '../store/authStore';
import googleAnalyticsService from '../services/googleAnalyticsService';

interface UseGoogleAnalyticsReturn {
  trackPageView: (path: string, title?: string) => void;
  trackEvent: (eventName: string, params?: Record<string, any>) => void;
  isInitialized: boolean;
}

export const useGoogleAnalytics = (): UseGoogleAnalyticsReturn => {
  const { user } = useAuthStore();

  useEffect(() => {
    const initGA = async () => {
      if (!user?.tenant_id) {
        console.log('GA4: No tenant ID found, skipping initialization');
        return;
      }

      try {
        // Fetch GA4 configuration from backend
        const config = await googleAnalyticsService.getGoogleAnalyticsIntegration(
          user.tenant_id
        );

        // Only initialize if enabled and configured for frontend tracking
        if (config.enabled && config.track_frontend && config.measurement_id) {
          // Initialize ReactGA4
          ReactGA.initialize(config.measurement_id, {
            gaOptions: {
              send_page_view: false, // We'll send page views manually
            },
            gtagOptions: {
              debug_mode: import.meta.env.DEV, // Enable debug in development
            },
          });

          // Set user properties for cross-session tracking
          ReactGA.set({
            tenant_id: user.tenant_id,
            user_id: user.id,
            user_role: user.role,
          });

          console.log(
            `GA4: Initialized with Measurement ID: ${config.measurement_id}`
          );
        } else {
          console.log('GA4: Tracking disabled or not configured');
        }
      } catch (err: any) {
        if (err.response?.status === 404) {
          console.log('GA4: Integration not configured for this tenant');
        } else {
          console.error('GA4: Failed to initialize:', err);
        }
      }
    };

    initGA();
  }, [user?.tenant_id]);

  /**
   * Track page view
   */
  const trackPageView = useCallback(
    (path: string, title?: string) => {
      try {
        ReactGA.send({
          hitType: 'pageview',
          page: path,
          title: title || document.title,
        });

        console.log(`GA4: Page view tracked - ${path}`);
      } catch (err) {
        console.error('GA4: Failed to track page view:', err);
      }
    },
    []
  );

  /**
   * Track custom event
   */
  const trackEvent = useCallback(
    (eventName: string, params: Record<string, any> = {}) => {
      try {
        // Add tenant_id to all events
        const eventParams = {
          ...params,
          tenant_id: user?.tenant_id,
          timestamp: new Date().toISOString(),
        };

        ReactGA.event(eventName, eventParams);

        console.log(`GA4: Event tracked - ${eventName}`, eventParams);
      } catch (err) {
        console.error(`GA4: Failed to track event ${eventName}:`, err);
      }
    },
    [user?.tenant_id]
  );

  return {
    trackPageView,
    trackEvent,
    isInitialized: !!user?.tenant_id,
  };
};

/**
 * Convenience hooks for common events
 */

export const useTrackAssessmentEvents = () => {
  const { trackEvent } = useGoogleAnalytics();

  return {
    trackAssessmentCreated: (assessmentId: string, title: string, method: 'manual' | 'ai') => {
      trackEvent('assessment_created', {
        assessment_id: assessmentId,
        assessment_title: title,
        creation_method: method,
      });
    },

    trackAssessmentPublished: (assessmentId: string) => {
      trackEvent('assessment_published', {
        assessment_id: assessmentId,
      });
    },

    trackAssessmentDeleted: (assessmentId: string) => {
      trackEvent('assessment_deleted', {
        assessment_id: assessmentId,
      });
    },
  };
};

export const useTrackLeadEvents = () => {
  const { trackEvent } = useGoogleAnalytics();

  return {
    trackLeadStatusChanged: (
      leadId: string,
      oldStatus: string,
      newStatus: string
    ) => {
      trackEvent('lead_status_changed', {
        lead_id: leadId,
        old_status: oldStatus,
        new_status: newStatus,
      });
    },

    trackLeadViewed: (leadId: string, leadScore: number) => {
      trackEvent('lead_viewed', {
        lead_id: leadId,
        lead_score: leadScore,
      });
    },
  };
};

export const useTrackDashboardEvents = () => {
  const { trackEvent } = useGoogleAnalytics();

  return {
    trackDashboardViewed: (viewType: 'overview' | 'analytics' | 'leads') => {
      trackEvent('dashboard_viewed', {
        view_type: viewType,
      });
    },
  };
};
