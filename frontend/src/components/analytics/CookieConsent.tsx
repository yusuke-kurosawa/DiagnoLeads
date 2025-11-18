/**
 * CookieConsent Component
 *
 * GDPR/CCPA compliant cookie consent banner for Google Analytics.
 * Users must consent before GA4 tracking begins.
 */
import { useState, useEffect } from 'react';
import { Cookie, X } from 'lucide-react';

const CONSENT_KEY = 'diagnoleads_cookie_consent';

interface CookieConsentProps {
  onAccept?: () => void;
  onDecline?: () => void;
}

export const CookieConsent: React.FC<CookieConsentProps> = ({
  onAccept,
  onDecline,
}) => {
  const [showBanner, setShowBanner] = useState(false);

  useEffect(() => {
    // Check if user has already made a choice
    const consent = localStorage.getItem(CONSENT_KEY);
    if (!consent) {
      setShowBanner(true);
    }
  }, []);

  const handleAccept = () => {
    localStorage.setItem(CONSENT_KEY, 'accepted');
    setShowBanner(false);
    if (onAccept) {
      onAccept();
    }
    // Reload to initialize GA4 with consent
    window.location.reload();
  };

  const handleDecline = () => {
    localStorage.setItem(CONSENT_KEY, 'declined');
    setShowBanner(false);
    if (onDecline) {
      onDecline();
    }
  };

  if (!showBanner) {
    return null;
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-3 flex-1">
            <Cookie className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-sm font-semibold text-gray-900 mb-1">
                Cookieの使用について
              </h3>
              <p className="text-sm text-gray-600">
                DiagnoLeadsは、サービスの改善とユーザー体験の向上のため、Google
                Analytics 4を使用してサイトの使用状況を分析しています。
                継続してご利用いただく場合、Cookieの使用に同意したものとみなされます。
              </p>
              <a
                href="/privacy-policy"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-600 underline hover:text-blue-700 mt-1 inline-block"
              >
                プライバシーポリシーを確認
              </a>
            </div>
          </div>

          <div className="flex items-center gap-2 flex-shrink-0">
            <button
              onClick={handleDecline}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
            >
              拒否
            </button>
            <button
              onClick={handleAccept}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors"
            >
              同意する
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Check if user has given cookie consent
 */
export const hasCookieConsent = (): boolean => {
  const consent = localStorage.getItem(CONSENT_KEY);
  return consent === 'accepted';
};

/**
 * Reset cookie consent (for testing or user preference change)
 */
export const resetCookieConsent = (): void => {
  localStorage.removeItem(CONSENT_KEY);
};
