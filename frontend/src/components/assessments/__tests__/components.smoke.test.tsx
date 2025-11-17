import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderWithProviders } from '@/test/test-utils';
import { ABTestManager } from '../ABTestManager';
import { SMSCampaignManager } from '../SMSCampaignManager';
import { QRCodeDownload } from '../QRCodeDownload';
import { apiClient } from '@/lib/apiClient';

vi.mock('@/lib/apiClient', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('Phase 1 Components - Smoke Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('ABTestManager', () => {
    it('should render without crashing', () => {
      vi.mocked(apiClient.get).mockResolvedValue({ data: [] });

      const { container } = renderWithProviders(
        <ABTestManager
          assessmentId="test-assessment-id"
          tenantId="test-tenant-id"
        />
      );

      expect(container).toBeTruthy();
    });

    it('should call API to load A/B tests on mount', () => {
      vi.mocked(apiClient.get).mockResolvedValue({ data: [] });

      renderWithProviders(
        <ABTestManager
          assessmentId="test-assessment-id"
          tenantId="test-tenant-id"
        />
      );

      expect(apiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('/ab-tests')
      );
    });
  });

  describe('SMSCampaignManager', () => {
    it('should render without crashing', () => {
      vi.mocked(apiClient.get).mockResolvedValue({ data: [] });

      const { container } = renderWithProviders(
        <SMSCampaignManager
          assessmentId="test-assessment-id"
          tenantId="test-tenant-id"
        />
      );

      expect(container).toBeTruthy();
    });

    it('should call API to load campaigns on mount', () => {
      vi.mocked(apiClient.get).mockResolvedValue({ data: [] });

      renderWithProviders(
        <SMSCampaignManager
          assessmentId="test-assessment-id"
          tenantId="test-tenant-id"
        />
      );

      expect(apiClient.get).toHaveBeenCalledWith(
        expect.stringContaining('/sms/campaigns')
      );
    });
  });

  describe('QRCodeDownload', () => {
    it('should render without crashing', () => {
      const { container } = renderWithProviders(
        <QRCodeDownload
          qrCodeId="test-qr-id"
          tenantId="test-tenant-id"
          qrCodeUrl="https://example.com/qr/test"
        />
      );

      expect(container).toBeTruthy();
    });
  });
});
