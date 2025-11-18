/**
 * DiagnoLeads API Client
 */

export interface AssessmentData {
  id: string;
  title: string;
  description: string;
  questions: Question[];
}

export interface Question {
  id: number;
  text: string;
  type: string;
  options: Option[];
}

export interface Option {
  id: string;
  text: string;
  score: number;
}

export interface LeadData {
  name: string;
  email: string;
  company?: string;
  phone?: string;
  responses: Record<string, any>;
  score: number;
}

export class DiagnoLeadsAPI {
  private baseUrl: string;
  private tenantId: string;

  constructor(baseUrl: string, tenantId: string) {
    this.baseUrl = baseUrl.replace(/\/$/, ''); // Remove trailing slash
    this.tenantId = tenantId;
  }

  async getAssessment(assessmentId: string): Promise<AssessmentData> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/tenants/${this.tenantId}/assessments/${assessmentId}/public`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch assessment: ${response.statusText}`);
    }

    return response.json();
  }

  async submitLead(assessmentId: string, leadData: LeadData): Promise<any> {
    const response = await fetch(
      `${this.baseUrl}/api/v1/tenants/${this.tenantId}/assessments/${assessmentId}/leads`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(leadData),
      }
    );

    if (!response.ok) {
      throw new Error(`Failed to submit lead: ${response.statusText}`);
    }

    return response.json();
  }
}
