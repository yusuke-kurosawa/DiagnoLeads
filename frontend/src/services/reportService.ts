import api from './api';

// Report Types
export interface ReportConfig {
  metrics: string[];
  filters?: {
    date_range?: { start: string; end: string };
    status?: string[];
    score_range?: { min: number; max: number };
    assessment_ids?: string[];
    [key: string]: any;
  };
  group_by?: 'status' | 'industry' | 'date' | 'assessment';
  visualization?: 'bar_chart' | 'line_chart' | 'pie_chart' | 'table';
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface ScheduleConfig {
  frequency: 'daily' | 'weekly' | 'monthly';
  day_of_week?: number; // 0=Monday, 6=Sunday
  day_of_month?: number; // 1-31
  time: string; // HH:MM format
  timezone?: string;
  recipients: string[];
}

export interface Report {
  id: string;
  tenant_id: string;
  name: string;
  description?: string;
  report_type: 'custom' | 'lead_analysis' | 'assessment_performance' | 'conversion_funnel' | 'ai_insights';
  config: ReportConfig;
  is_scheduled: boolean;
  schedule_config?: ScheduleConfig;
  is_public: boolean;
  created_by: string;
  updated_by?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateReportData {
  name: string;
  description?: string;
  report_type?: string;
  config: ReportConfig;
  is_scheduled?: boolean;
  schedule_config?: ScheduleConfig;
  is_public?: boolean;
}

export interface UpdateReportData {
  name?: string;
  description?: string;
  config?: ReportConfig;
  is_scheduled?: boolean;
  schedule_config?: ScheduleConfig;
  is_public?: boolean;
}

export interface ReportExecutionResult {
  report_id: string;
  report_name: string;
  executed_at: string;
  data_points: Array<Record<string, any>>;
  summary: {
    total_records: number;
    date_range?: { start: string; end: string };
    metrics: Record<string, number | string>;
  };
  config: ReportConfig;
}

export interface ExportFormat {
  format: 'csv' | 'excel' | 'pdf';
}

export const reportService = {
  /**
   * List all reports for a tenant
   */
  async list(tenantId: string, params?: { skip?: number; limit?: number; report_type?: string }) {
    const response = await api.get<Report[]>(
      `/tenants/${tenantId}/reports`,
      { params }
    );
    return response.data;
  },

  /**
   * Get a specific report by ID
   */
  async get(tenantId: string, reportId: string) {
    const response = await api.get<Report>(
      `/tenants/${tenantId}/reports/${reportId}`
    );
    return response.data;
  },

  /**
   * Create a new report
   */
  async create(tenantId: string, data: CreateReportData) {
    const response = await api.post<Report>(
      `/tenants/${tenantId}/reports`,
      data
    );
    return response.data;
  },

  /**
   * Update an existing report
   */
  async update(tenantId: string, reportId: string, data: UpdateReportData) {
    const response = await api.put<Report>(
      `/tenants/${tenantId}/reports/${reportId}`,
      data
    );
    return response.data;
  },

  /**
   * Delete a report
   */
  async delete(tenantId: string, reportId: string) {
    await api.delete(`/tenants/${tenantId}/reports/${reportId}`);
  },

  /**
   * Execute a report and get results
   */
  async execute(tenantId: string, reportId: string) {
    const response = await api.post<ReportExecutionResult>(
      `/tenants/${tenantId}/reports/${reportId}/execute`,
      {}
    );
    return response.data;
  },

  /**
   * Export report results
   * Returns a blob for download
   */
  async export(tenantId: string, reportId: string, format: 'csv' | 'excel' | 'pdf') {
    const response = await api.post(
      `/tenants/${tenantId}/reports/${reportId}/export`,
      { format },
      { responseType: 'blob' }
    );
    return response.data;
  },

  /**
   * Download exported report
   * Helper function to trigger browser download
   */
  downloadExport(blob: Blob, filename: string) {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  },
};
