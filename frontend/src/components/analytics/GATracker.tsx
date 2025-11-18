/**
 * GATracker Component
 *
 * Automatically tracks page views when route changes.
 * Should be placed inside Router but outside Routes.
 */
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useGoogleAnalytics } from '../../hooks/useGoogleAnalytics';

export const GATracker: React.FC = () => {
  const location = useLocation();
  const { trackPageView, isInitialized } = useGoogleAnalytics();

  useEffect(() => {
    if (isInitialized) {
      // Track page view on route change
      trackPageView(location.pathname + location.search);
    }
  }, [location, trackPageView, isInitialized]);

  // This component doesn't render anything
  return null;
};
