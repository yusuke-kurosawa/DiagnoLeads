/**
 * DiagnoLeads Assessment Widget Web Component
 */

import { DiagnoLeadsAPI, AssessmentData, Question, LeadData } from '../api/client';
import { GA4Tracker } from '../tracking/ga4';

export interface WidgetConfig {
  tenantId: string;
  assessmentId: string;
  apiBaseUrl?: string;
  ga4MeasurementId?: string;
  theme?: 'light' | 'dark';
  primaryColor?: string;
  onComplete?: (data: any) => void;
}

export class DiagnoLeadsWidget extends HTMLElement {
  private shadow: ShadowRoot;
  private config: WidgetConfig;
  private api: DiagnoLeadsAPI;
  private tracker: GA4Tracker;
  private assessment: AssessmentData | null = null;
  private responses: Record<string, any> = {};
  private currentQuestionIndex: number = 0;
  private totalScore: number = 0;

  constructor() {
    super();
    this.shadow = this.attachShadow({ mode: 'open' });

    // Get configuration from attributes
    this.config = {
      tenantId: this.getAttribute('tenant-id') || '',
      assessmentId: this.getAttribute('assessment-id') || '',
      apiBaseUrl: this.getAttribute('api-url') || 'http://localhost:8000',
      ga4MeasurementId: this.getAttribute('ga4-id') || undefined,
      theme: (this.getAttribute('theme') as 'light' | 'dark') || 'light',
      primaryColor: this.getAttribute('primary-color') || '#3b82f6',
    };

    this.api = new DiagnoLeadsAPI(this.config.apiBaseUrl, this.config.tenantId);
    this.tracker = new GA4Tracker(this.config.ga4MeasurementId);
  }

  async connectedCallback(): void {
    try {
      // Load assessment data
      this.assessment = await this.api.getAssessment(this.config.assessmentId);

      // Track widget loaded
      this.tracker.trackWidgetLoaded(this.config.assessmentId);

      // Render initial view
      this.render();
    } catch (error) {
      console.error('[DiagnoLeads] Failed to load assessment:', error);
      this.renderError('診断の読み込みに失敗しました。');
    }
  }

  private render(): void {
    if (!this.assessment) return;

    const currentQuestion = this.assessment.questions[this.currentQuestionIndex];

    this.shadow.innerHTML = `
      ${this.getStyles()}
      <div class="diagnoleads-widget">
        <div class="diagnoleads-container">
          ${this.renderHeader()}
          ${currentQuestion ? this.renderQuestion(currentQuestion) : this.renderLeadForm()}
          ${this.renderProgress()}
        </div>
      </div>
    `;

    // Attach event listeners
    this.attachEventListeners();
  }

  private renderHeader(): string {
    if (!this.assessment) return '';

    return `
      <div class="header">
        <h2 class="title">${this.assessment.title}</h2>
        <p class="description">${this.assessment.description}</p>
      </div>
    `;
  }

  private renderQuestion(question: Question): string {
    return `
      <div class="question-container">
        <div class="question-header">
          <span class="question-number">質問 ${this.currentQuestionIndex + 1} / ${
      this.assessment!.questions.length
    }</span>
          <h3 class="question-text">${question.text}</h3>
        </div>
        <div class="options">
          ${question.options
            .map(
              (option, index) => `
            <button
              class="option-button"
              data-question-id="${question.id}"
              data-option-id="${option.id}"
              data-option-score="${option.score}"
            >
              <span class="option-label">${String.fromCharCode(65 + index)}</span>
              <span class="option-text">${option.text}</span>
            </button>
          `
            )
            .join('')}
        </div>
      </div>
    `;
  }

  private renderLeadForm(): string {
    return `
      <div class="lead-form-container">
        <div class="completion-message">
          <h3 class="completion-title">診断が完了しました！</h3>
          <p class="completion-text">詳細な結果を受け取るために、以下の情報をご入力ください。</p>
          <div class="score-display">
            <span class="score-label">あなたのスコア:</span>
            <span class="score-value">${this.calculateAverageScore()}点</span>
          </div>
        </div>
        <form class="lead-form" id="diagnoleads-lead-form">
          <div class="form-group">
            <label for="name">お名前 <span class="required">*</span></label>
            <input type="text" id="name" name="name" required placeholder="山田 太郎" />
          </div>
          <div class="form-group">
            <label for="email">メールアドレス <span class="required">*</span></label>
            <input type="email" id="email" name="email" required placeholder="yamada@example.com" />
          </div>
          <div class="form-group">
            <label for="company">会社名</label>
            <input type="text" id="company" name="company" placeholder="株式会社○○" />
          </div>
          <div class="form-group">
            <label for="phone">電話番号</label>
            <input type="tel" id="phone" name="phone" placeholder="03-1234-5678" />
          </div>
          <button type="submit" class="submit-button">結果を受け取る</button>
        </form>
      </div>
    `;
  }

  private renderProgress(): string {
    const totalQuestions = this.assessment?.questions.length || 0;
    const progress = (this.currentQuestionIndex / totalQuestions) * 100;

    return `
      <div class="progress-bar">
        <div class="progress-fill" style="width: ${progress}%"></div>
      </div>
    `;
  }

  private renderError(message: string): void {
    this.shadow.innerHTML = `
      ${this.getStyles()}
      <div class="diagnoleads-widget">
        <div class="diagnoleads-container">
          <div class="error-message">
            <p>${message}</p>
          </div>
        </div>
      </div>
    `;
  }

  private attachEventListeners(): void {
    // Option button clicks
    const optionButtons = this.shadow.querySelectorAll('.option-button');
    optionButtons.forEach((button) => {
      button.addEventListener('click', this.handleOptionClick.bind(this));
    });

    // Lead form submission
    const leadForm = this.shadow.getElementById('diagnoleads-lead-form');
    if (leadForm) {
      leadForm.addEventListener('submit', this.handleLeadFormSubmit.bind(this));
    }
  }

  private handleOptionClick(event: Event): void {
    const button = event.currentTarget as HTMLButtonElement;
    const questionId = button.getAttribute('data-question-id');
    const optionId = button.getAttribute('data-option-id');
    const optionScore = parseInt(button.getAttribute('data-option-score') || '0', 10);

    if (!questionId || !optionId) return;

    // Save response
    this.responses[questionId] = {
      option_id: optionId,
      score: optionScore,
    };
    this.totalScore += optionScore;

    // Track event
    const currentQuestion = this.assessment!.questions[this.currentQuestionIndex];
    this.tracker.trackQuestionAnswered(
      this.config.assessmentId,
      currentQuestion.id,
      currentQuestion.text
    );

    // Move to next question or show lead form
    if (this.currentQuestionIndex === 0) {
      this.tracker.trackAssessmentStarted(
        this.config.assessmentId,
        this.assessment!.title
      );
    }

    this.currentQuestionIndex++;

    if (this.currentQuestionIndex < this.assessment!.questions.length) {
      this.render();
    } else {
      // All questions answered - show lead form
      const avgScore = this.calculateAverageScore();
      this.tracker.trackAssessmentCompleted(
        this.config.assessmentId,
        this.assessment!.title,
        avgScore
      );
      this.render();
    }
  }

  private async handleLeadFormSubmit(event: Event): Promise<void> {
    event.preventDefault();

    const form = event.target as HTMLFormElement;
    const formData = new FormData(form);

    const leadData: LeadData = {
      name: formData.get('name') as string,
      email: formData.get('email') as string,
      company: formData.get('company') as string || undefined,
      phone: formData.get('phone') as string || undefined,
      responses: this.responses,
      score: this.calculateAverageScore(),
    };

    try {
      // Submit lead
      const result = await this.api.submitLead(this.config.assessmentId, leadData);

      // Track conversion
      this.tracker.trackLeadSubmitted(
        this.config.assessmentId,
        leadData.email,
        leadData.score
      );

      // Call onComplete callback if provided
      if (this.config.onComplete) {
        this.config.onComplete(result);
      }

      // Show thank you message
      this.renderThankYou(result);
    } catch (error) {
      console.error('[DiagnoLeads] Failed to submit lead:', error);
      alert('送信に失敗しました。もう一度お試しください。');
    }
  }

  private renderThankYou(result: any): void {
    this.shadow.innerHTML = `
      ${this.getStyles()}
      <div class="diagnoleads-widget">
        <div class="diagnoleads-container">
          <div class="thank-you-message">
            <h2 class="thank-you-title">ありがとうございました！</h2>
            <p class="thank-you-text">
              診断結果をメールでお送りしました。<br>
              ご登録いただいたメールアドレスをご確認ください。
            </p>
            <div class="score-summary">
              <p class="score-label">総合スコア</p>
              <p class="score-value-large">${this.calculateAverageScore()}点</p>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  private calculateAverageScore(): number {
    const scores = Object.values(this.responses).map((r: any) => r.score);
    if (scores.length === 0) return 0;
    const sum = scores.reduce((a, b) => a + b, 0);
    return Math.round(sum / scores.length);
  }

  private getStyles(): string {
    const primaryColor = this.config.primaryColor;
    const isDark = this.config.theme === 'dark';

    return `
      <style>
        * {
          box-sizing: border-box;
          margin: 0;
          padding: 0;
        }

        .diagnoleads-widget {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
          width: 100%;
          max-width: 600px;
          margin: 0 auto;
          color: ${isDark ? '#e5e7eb' : '#1f2937'};
          background-color: ${isDark ? '#1f2937' : '#ffffff'};
        }

        .diagnoleads-container {
          padding: 2rem;
          border-radius: 8px;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          background-color: ${isDark ? '#1f2937' : '#ffffff'};
        }

        .header {
          margin-bottom: 2rem;
          text-align: center;
        }

        .title {
          font-size: 1.75rem;
          font-weight: 700;
          margin-bottom: 0.5rem;
          color: ${primaryColor};
        }

        .description {
          font-size: 1rem;
          color: ${isDark ? '#9ca3af' : '#6b7280'};
        }

        .question-container {
          margin-bottom: 2rem;
        }

        .question-header {
          margin-bottom: 1.5rem;
        }

        .question-number {
          font-size: 0.875rem;
          font-weight: 600;
          color: ${primaryColor};
          display: block;
          margin-bottom: 0.5rem;
        }

        .question-text {
          font-size: 1.25rem;
          font-weight: 600;
          line-height: 1.6;
        }

        .options {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .option-button {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding: 1rem;
          background-color: ${isDark ? '#374151' : '#f9fafb'};
          border: 2px solid ${isDark ? '#4b5563' : '#e5e7eb'};
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
          text-align: left;
          font-size: 1rem;
          color: ${isDark ? '#e5e7eb' : '#1f2937'};
        }

        .option-button:hover {
          border-color: ${primaryColor};
          background-color: ${isDark ? '#4b5563' : '#f3f4f6'};
          transform: translateY(-2px);
        }

        .option-label {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 2rem;
          height: 2rem;
          background-color: ${primaryColor};
          color: white;
          border-radius: 50%;
          font-weight: 700;
          flex-shrink: 0;
        }

        .option-text {
          flex: 1;
          line-height: 1.5;
        }

        .lead-form-container {
          margin-top: 2rem;
        }

        .completion-message {
          text-align: center;
          margin-bottom: 2rem;
        }

        .completion-title {
          font-size: 1.5rem;
          font-weight: 700;
          color: ${primaryColor};
          margin-bottom: 0.5rem;
        }

        .completion-text {
          color: ${isDark ? '#9ca3af' : '#6b7280'};
          margin-bottom: 1rem;
        }

        .score-display {
          display: inline-block;
          padding: 1rem 2rem;
          background-color: ${isDark ? '#374151' : '#f3f4f6'};
          border-radius: 8px;
          margin-top: 1rem;
        }

        .score-label {
          font-size: 0.875rem;
          color: ${isDark ? '#9ca3af' : '#6b7280'};
          margin-right: 0.5rem;
        }

        .score-value {
          font-size: 1.5rem;
          font-weight: 700;
          color: ${primaryColor};
        }

        .lead-form {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .form-group {
          display: flex;
          flex-direction: column;
        }

        label {
          font-weight: 600;
          margin-bottom: 0.5rem;
          font-size: 0.875rem;
        }

        .required {
          color: #ef4444;
        }

        input {
          padding: 0.75rem;
          border: 2px solid ${isDark ? '#4b5563' : '#e5e7eb'};
          border-radius: 6px;
          font-size: 1rem;
          background-color: ${isDark ? '#374151' : '#ffffff'};
          color: ${isDark ? '#e5e7eb' : '#1f2937'};
        }

        input:focus {
          outline: none;
          border-color: ${primaryColor};
        }

        .submit-button {
          padding: 1rem 2rem;
          background-color: ${primaryColor};
          color: white;
          border: none;
          border-radius: 6px;
          font-size: 1rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          margin-top: 1rem;
        }

        .submit-button:hover {
          opacity: 0.9;
          transform: translateY(-1px);
        }

        .progress-bar {
          width: 100%;
          height: 8px;
          background-color: ${isDark ? '#374151' : '#e5e7eb'};
          border-radius: 4px;
          overflow: hidden;
          margin-top: 2rem;
        }

        .progress-fill {
          height: 100%;
          background-color: ${primaryColor};
          transition: width 0.3s ease;
        }

        .thank-you-message {
          text-align: center;
          padding: 2rem 0;
        }

        .thank-you-title {
          font-size: 2rem;
          font-weight: 700;
          color: ${primaryColor};
          margin-bottom: 1rem;
        }

        .thank-you-text {
          font-size: 1rem;
          color: ${isDark ? '#9ca3af' : '#6b7280'};
          line-height: 1.6;
          margin-bottom: 2rem;
        }

        .score-summary {
          padding: 2rem;
          background-color: ${isDark ? '#374151' : '#f3f4f6'};
          border-radius: 8px;
          margin-top: 2rem;
        }

        .score-value-large {
          font-size: 3rem;
          font-weight: 700;
          color: ${primaryColor};
        }

        .error-message {
          text-align: center;
          padding: 2rem;
          color: #ef4444;
        }
      </style>
    `;
  }
}

// Register custom element
if (typeof customElements !== 'undefined') {
  customElements.define('diagnoleads-widget', DiagnoLeadsWidget);
}
