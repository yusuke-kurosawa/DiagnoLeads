import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders, mockApiResponse, mockApiError } from '@/test/test-utils';
import { ABTestManager } from './ABTestManager';
import { apiClient } from '@/lib/apiClient';

vi.mock('@/lib/apiClient', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('ABTestManager', () => {
  const defaultProps = {
    assessmentId: 'test-assessment-id',
    tenantId: 'test-tenant-id',
  };

  const mockABTests = [
    {
      id: 'test-1',
      name: 'CTA文言テスト',
      description: 'CTAボタンの文言を最適化',
      test_type: 'cta_text',
      status: 'running',
      total_impressions: 1500,
      total_conversions: 225,
      overall_conversion_rate: 0.15,
      winner_variant_id: null,
      confidence: null,
      created_at: '2025-01-10T10:00:00Z',
      variants: [
        {
          id: 'variant-a',
          name: 'A',
          description: 'コントロール',
          is_control: true,
          impressions: 750,
          conversions: 105,
          conversion_rate: 0.14,
          thompson_score: 0.48,
          current_traffic_allocation: 0.45,
          confidence_interval_lower: 0.11,
          confidence_interval_upper: 0.17,
        },
        {
          id: 'variant-b',
          name: 'B',
          description: '新しい文言',
          is_control: false,
          impressions: 750,
          conversions: 120,
          conversion_rate: 0.16,
          thompson_score: 0.52,
          current_traffic_allocation: 0.55,
          confidence_interval_lower: 0.13,
          confidence_interval_upper: 0.19,
        },
      ],
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Loading and Display', () => {
    it('should display loading state initially', () => {
      vi.mocked(apiClient.get).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      renderWithProviders(
        <ABTestManager {...defaultProps} />
      );

      expect(screen.getByText(/読み込み中/i)).toBeInTheDocument();
    });

    it('should display empty state when no A/B tests exist', async () => {
      vi.mocked(apiClient.get).mockResolvedValue({ data: [] });

      renderWithProviders(
        <ABTestManager {...defaultProps} />
      );

      await waitFor(() => {
        expect(screen.getByText(/A\/Bテストがまだありません/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/新しいA\/Bテストを作成/i)).toBeInTheDocument();
    });

    it('should display A/B tests when they exist', async () => {
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockABTests });

      renderWithProviders(
        <ABTestManager {...defaultProps} />
      );

      await waitFor(() => {
        expect(screen.getByText('CTA文言テスト')).toBeInTheDocument();
      });

      expect(screen.getByText('CTAボタンの文言を最適化')).toBeInTheDocument();
      expect(screen.getByText('1,500')).toBeInTheDocument(); // Total impressions
      expect(screen.getByText('15.0%')).toBeInTheDocument(); // Overall CVR
    });

    it('should display correct variant information', async () => {
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockABTests });

      renderWithProviders(
        <ABTestManager {...defaultProps} />
      );

      await waitFor(() => {
        expect(screen.getByText('バリアント A')).toBeInTheDocument();
      });

      expect(screen.getByText('バリアント B')).toBeInTheDocument();
      expect(screen.getByText('コントロール')).toBeInTheDocument();
      expect(screen.getByText('新しい文言')).toBeInTheDocument();

      // Check traffic allocation
      expect(screen.getByText('45%')).toBeInTheDocument();
      expect(screen.getByText('55%')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('should display error message when API call fails', async () => {
      vi.mocked(apiClient.get).mockRejectedValue({
        response: {
          data: { detail: 'Failed to load A/B tests' },
          status: 500,
        },
      });

      renderWithProviders(
        <ABTestManager {...defaultProps} />
      );

      await waitFor(() => {
        expect(screen.getByText(/Failed to load A\/B tests/i)).toBeInTheDocument();
      });
    });

    it('should allow retry after error', async () => {
      vi.mocked(apiClient.get)
        .mockRejectedValueOnce({
          response: { data: { detail: 'Network error' }, status: 500 },
        })
        .mockResolvedValueOnce({ data: mockABTests });

      renderWithProviders(
        <ABTestManager {...defaultProps} />
      );

      await waitFor(() => {
        expect(screen.getByText(/Network error/i)).toBeInTheDocument();
      });

      const retryButton = screen.getByRole('button', { name: /再読み込み/i });
      await userEvent.click(retryButton);

      await waitFor(() => {
        expect(screen.getByText('CTA文言テスト')).toBeInTheDocument();
      });
    });
  });

  describe('Create A/B Test', () => {
    it('should open create modal when clicking create button', async () => {
      vi.mocked(apiClient.get).mockResolvedValue({ data: [] });

      renderWithProviders(
        <ABTestManager {...defaultProps} />
      );

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /新規A\/Bテスト作成/i })).toBeInTheDocument();
      });

      const createButton = screen.getByRole('button', { name: /新規A\/Bテスト作成/i });
      await userEvent.click(createButton);

      await waitFor(() => {
        expect(screen.getByText(/新規A\/Bテスト作成/i)).toBeInTheDocument();
      });
    });
  });

  describe('Test Status and Winner Display', () => {
    it('should display running status correctly', async () => {
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockABTests });

      renderWithProviders(
        <ABTestManager {...defaultProps} />
      );

      await waitFor(() => {
        expect(screen.getByText(/実行中/i)).toBeInTheDocument();
      });
    });

    it('should display winner when test is completed', async () => {
      const completedTest = {
        ...mockABTests[0],
        status: 'completed',
        winner_variant_id: 'variant-b',
        confidence: 0.97,
      };

      vi.mocked(apiClient.get).mockResolvedValue({ data: [completedTest] });

      renderWithProviders(
        <ABTestManager {...defaultProps} />
      );

      await waitFor(() => {
        expect(screen.getByText(/完了/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/勝者:/i)).toBeInTheDocument();
      expect(screen.getByText(/97%/i)).toBeInTheDocument(); // Confidence
    });
  });

  describe('Traffic Allocation Visualization', () => {
    it('should display traffic allocation bars for each variant', async () => {
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockABTests });

      renderWithProviders(
        <ABTestManager {...defaultProps} />
      );

      await waitFor(() => {
        expect(screen.getByText('45%')).toBeInTheDocument();
        expect(screen.getByText('55%')).toBeInTheDocument();
      });

      // Check that traffic allocation bars are rendered
      const bars = screen.getAllByRole('progressbar');
      expect(bars).toHaveLength(2);
    });
  });

  describe('Confidence Intervals', () => {
    it('should display confidence intervals for variants', async () => {
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockABTests });

      renderWithProviders(
        <ABTestManager {...defaultProps} />
      );

      await waitFor(() => {
        expect(screen.getByText(/11\.0% - 17\.0%/i)).toBeInTheDocument();
      });

      expect(screen.getByText(/13\.0% - 19\.0%/i)).toBeInTheDocument();
    });
  });

  describe('Test Deletion', () => {
    it('should delete test when delete button is clicked', async () => {
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockABTests });
      vi.mocked(apiClient.delete).mockResolvedValue({ data: { success: true } });

      const user = userEvent.setup();

      renderWithProviders(
        <ABTestManager {...defaultProps} />
      );

      await waitFor(() => {
        expect(screen.getByText('CTA文言テスト')).toBeInTheDocument();
      });

      const deleteButton = screen.getByRole('button', { name: /削除/i });
      await user.click(deleteButton);

      // Confirm deletion
      const confirmButton = screen.getByRole('button', { name: /削除する/i });
      await user.click(confirmButton);

      await waitFor(() => {
        expect(apiClient.delete).toHaveBeenCalledWith(
          `/tenants/${defaultProps.tenantId}/ab-tests/test-1`
        );
      });
    });
  });

  describe('Refresh Functionality', () => {
    it('should refresh data when refresh button is clicked', async () => {
      vi.mocked(apiClient.get)
        .mockResolvedValueOnce({ data: mockABTests })
        .mockResolvedValueOnce({
          data: [
            {
              ...mockABTests[0],
              total_impressions: 2000,
            },
          ],
        });

      const user = userEvent.setup();

      renderWithProviders(
        <ABTestManager {...defaultProps} />
      );

      await waitFor(() => {
        expect(screen.getByText('1,500')).toBeInTheDocument();
      });

      const refreshButton = screen.getByRole('button', { name: /更新/i });
      await user.click(refreshButton);

      await waitFor(() => {
        expect(screen.getByText('2,000')).toBeInTheDocument();
      });

      expect(apiClient.get).toHaveBeenCalledTimes(2);
    });
  });
});
