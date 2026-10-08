import { env } from '@/lib/env';
import { isEmailConfigured, sendEmail } from '@/lib/features/email';
import { notifyOrganizationMembers } from '@/lib/features/notifications/notification-service';
import { triggerWebhooks } from '@/lib/features/webhooks/services/webhook-service';
import { addBusinessDays, format } from 'date-fns';
import { AX_MIGRATION_CONFIG } from './config';
import type { AxMigrationResult } from './evaluate';

const LEVEL_LABELS = { low: '低', medium: '中', high: '高' } as const;
const CHALLENGE_LABELS = {
  people: 'ヒト（担い手不足・属人化）',
  cost: 'カネ（保守・延命コスト）',
  agility: 'モノ（市場変化への対応）',
  data: '情報（データ活用）',
} as const;

export interface AxMigrationNotification {
  organizationId: string;
  leadId: string;
  submissionId: string;
  company: string;
  name: string;
  email: string;
  result: Pick<
    AxMigrationResult,
    'difficulty' | 'urgency' | 'challenges' | 'mql' | 'sqlSignals' | 'leadScore'
  >;
  consultationRequested: boolean;
  leadCreated: boolean;
  requestedAt: Date;
}

/**
 * 相談申込への連絡期限（土日を除く営業日。祝日は考慮しない）
 */
export function consultationDeadline(
  requestedAt: Date,
  businessDays = AX_MIGRATION_CONFIG.consultationResponseBusinessDays
): Date {
  return addBusinessDays(requestedAt, businessDays);
}

export function buildSalesMessage(n: AxMigrationNotification): { title: string; message: string } {
  const summary = [
    `移行難易度: ${LEVEL_LABELS[n.result.difficulty.level]}`,
    `緊急度: ${LEVEL_LABELS[n.result.urgency.level]}`,
    `主な課題: ${CHALLENGE_LABELS[n.result.challenges.primary]}`,
    `MQL: ${n.result.mql.qualified ? '該当' : '非該当'}`,
    `SQL候補: ${n.result.sqlSignals.candidate ? 'あり' : 'なし'}`,
  ].join(' / ');

  if (n.consultationRequested) {
    const deadline = format(consultationDeadline(n.requestedAt), 'yyyy/MM/dd');
    return {
      title: `【相談申込】${n.company} ${n.name} 様（${deadline} までに連絡）`,
      message: `AXマイグレーション診断から相談申込がありました。MQL判定を経ずに営業へ引き渡します。${summary}`,
    };
  }
  return {
    title: `【AX診断】${n.company} ${n.name} 様が診断を完了しました`,
    message: summary,
  };
}

/**
 * Notify sales after a diagnosis or a consultation request.
 * Failures are logged and never break the respondent's flow.
 */
export async function notifyAxMigrationSubmission(n: AxMigrationNotification): Promise<void> {
  const { title, message } = buildSalesMessage(n);
  const data = {
    leadId: n.leadId,
    submissionId: n.submissionId,
    diagnosticKey: 'ax-migration',
    consultationRequested: n.consultationRequested,
  };

  const tasks: Promise<unknown>[] = [
    triggerWebhooks(n.organizationId, 'diagnostic.submitted', {
      ...data,
      email: n.email,
      company: n.company,
      name: n.name,
      score: n.result.leadScore,
      mql: n.result.mql.qualified,
      sqlCandidate: n.result.sqlSignals.candidate,
      difficulty: n.result.difficulty.level,
      urgency: n.result.urgency.level,
      primaryChallenge: n.result.challenges.primary,
    }),
  ];

  // Notify in-app for consultation requests, MQLs and new leads; skip repeat answers that change nothing
  if (n.consultationRequested || n.result.mql.qualified || n.leadCreated) {
    tasks.push(
      notifyOrganizationMembers(
        n.organizationId,
        n.consultationRequested ? 'consultation_requested' : 'lead_created',
        title,
        message,
        data
      )
    );
  }

  const salesEmail = env.AX_DIAGNOSIS_SALES_EMAIL;
  if (n.consultationRequested && salesEmail && isEmailConfigured()) {
    const leadUrl = `${process.env.NEXT_PUBLIC_APP_URL ?? ''}/ja/leads?leadId=${n.leadId}`;
    tasks.push(
      sendEmail({
        to: salesEmail.split(',').map((address) => address.trim()),
        subject: title,
        text: `${message}\n\n会社名: ${n.company}\n氏名: ${n.name}\nメール: ${n.email}\nリード: ${leadUrl}`,
        html: `<p>${message}</p><ul><li>会社名: ${escapeHtml(n.company)}</li><li>氏名: ${escapeHtml(n.name)}</li><li>メール: ${escapeHtml(n.email)}</li></ul><p><a href="${leadUrl}">リードを開く</a></p>`,
      })
    );
  }

  const results = await Promise.allSettled(tasks);
  for (const r of results) {
    if (r.status === 'rejected') {
      console.error('AX diagnosis notification failed:', r.reason);
    }
  }
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
