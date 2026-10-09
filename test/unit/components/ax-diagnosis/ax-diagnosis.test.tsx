/**
 * AX migration diagnosis components (real next-intl messages, fetch mocked)
 */
import { AxDiagnosisFlow } from '@/components/features/ax-diagnosis/ax-diagnosis-flow';
import { AxDiagnosisResult } from '@/components/features/ax-diagnosis/ax-diagnosis-result';
import { evaluateAxMigration, toPublicResult } from '@/lib/features/diagnostics/ax-migration/evaluate';
import messages from '@/locales/ja/common.json';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { NextIntlClientProvider } from 'next-intl';
import type { ReactNode } from 'react';
import { afterEach, beforeAll, beforeEach, describe, expect, it, vi } from 'vitest';

beforeAll(() => {
  Element.prototype.scrollIntoView = vi.fn();
  globalThis.ResizeObserver ??= class {
    observe() {}
    unobserve() {}
    disconnect() {}
  } as unknown as typeof ResizeObserver;
});

const withIntl = (ui: ReactNode) => (
  <NextIntlClientProvider locale="ja" messages={messages} timeZone="Asia/Tokyo">
    {ui}
  </NextIntlClientProvider>
);

const publicResult = toPublicResult(
  evaluateAxMigration({
    industry: 'manufacturing',
    revenue: '10b_30b',
    system: 'as400',
    languages: ['rpg', 'cl'],
    years: 'gte20',
    programs: '500_2000',
    integrations: 'some',
    maintenance: 'few',
    documents: 'partial',
    challenges: ['people', 'cost'],
    timeline: '1_2y',
    role: 'it_manager',
  })
);

const fetchMock = vi.fn();

beforeEach(() => {
  fetchMock.mockReset();
  vi.stubGlobal('fetch', fetchMock);
  vi.stubGlobal('requestAnimationFrame', (cb: FrameRequestCallback) => {
    cb(0);
    return 0;
  });
});

afterEach(() => {
  vi.unstubAllGlobals();
  window.history.replaceState(null, '', '/');
});

const jsonResponse = (status: number, body: unknown) =>
  ({ ok: status >= 200 && status < 300, status, json: async () => body }) as Response;

async function answerAll(user: ReturnType<typeof userEvent.setup>) {
  const next = () => user.click(screen.getByRole('button', { name: '次へ' }));
  await user.click(screen.getByLabelText('製造業'));
  await user.click(screen.getByLabelText('100億〜300億円'));
  await next();
  await user.click(screen.getByLabelText('AS/400（IBM i）'));
  await user.click(screen.getByLabelText('RPG'));
  await user.click(screen.getByLabelText('20年以上'));
  await user.click(screen.getByLabelText('500〜2,000本'));
  await user.click(screen.getByLabelText('3〜5'));
  await next();
  await user.click(screen.getByLabelText('社内の1〜2名に頼っている'));
  await user.click(screen.getByLabelText('一部が古い・足りない'));
  await user.click(screen.getByLabelText('扱える技術者が減り、仕様がブラックボックス化している'));
  await next();
  await user.click(screen.getByLabelText('1〜2年以内'));
  await user.click(screen.getByLabelText('情報システム部門の責任者'));
  await next();
}

async function fillContact(user: ReturnType<typeof userEvent.setup>) {
  await user.type(screen.getByLabelText(/会社名/), '三田製作所');
  await user.type(screen.getByLabelText(/お名前/), '山田 太郎');
  await user.type(screen.getByLabelText(/メールアドレス/), 'yamada@example.jp');
  await user.click(screen.getByLabelText('個人情報の取り扱いに同意する'));
}

describe('AxDiagnosisFlow', () => {
  it('starts at the intro and moves focus to the step heading', async () => {
    const user = userEvent.setup();
    render(withIntl(<AxDiagnosisFlow locale="ja" />));
    expect(
      screen.getByRole('heading', { name: '今の基幹システムのまま、AI時代の経営判断はできますか？' })
    ).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: '診断をはじめる' }));
    const heading = screen.getByRole('heading', { name: '会社について' });
    expect(heading).toHaveFocus();
    expect(screen.getByText('ステップ 1 / 5')).toBeInTheDocument();
  });

  it('shows errors and focuses the first unanswered question', async () => {
    const user = userEvent.setup();
    render(withIntl(<AxDiagnosisFlow locale="ja" />));
    await user.click(screen.getByRole('button', { name: '診断をはじめる' }));
    await user.click(screen.getByRole('button', { name: '次へ' }));

    expect(screen.getAllByText('回答を選んでください')).toHaveLength(2);
    expect(screen.getByText('ステップ 1 / 5')).toBeInTheDocument();
    expect(screen.getByLabelText('製造業')).toHaveFocus();
  });

  it('keeps "I don\'t know" exclusive in multiple-choice questions', async () => {
    const user = userEvent.setup();
    render(withIntl(<AxDiagnosisFlow locale="ja" />));
    await user.click(screen.getByRole('button', { name: '診断をはじめる' }));
    await user.click(screen.getByLabelText('製造業'));
    await user.click(screen.getByLabelText('100億〜300億円'));
    await user.click(screen.getByRole('button', { name: '次へ' }));

    const languages = screen.getByRole('group', { name: /主な開発言語/ });
    await user.click(within(languages).getByLabelText('RPG'));
    await user.click(within(languages).getByLabelText('わからない'));
    expect(within(languages).getByLabelText('RPG')).not.toBeChecked();
    await user.click(within(languages).getByLabelText('COBOL'));
    expect(within(languages).getByLabelText('わからない')).not.toBeChecked();
  });

  it('requires consent, submits answers with tracking and shows the result', async () => {
    window.history.replaceState(null, '', '/ja/ax-diagnosis?utm_source=google&utm_medium=cpc&ref=partner-a');
    const user = userEvent.setup();
    render(withIntl(<AxDiagnosisFlow locale="ja" />));
    await user.click(screen.getByRole('button', { name: '診断をはじめる' }));
    await answerAll(user);

    await user.click(screen.getByRole('button', { name: '診断結果を見る' }));
    expect(screen.getByText('個人情報の取り扱いへの同意が必要です')).toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalled();

    fetchMock.mockResolvedValueOnce(
      jsonResponse(200, { submissionId: 'sub-1', consultationRequested: false, result: publicResult })
    );
    await fillContact(user);
    await user.click(screen.getByRole('button', { name: '診断結果を見る' }));

    const heading = await screen.findByRole('heading', { name: '診断結果' });
    expect(heading).toHaveFocus();
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe('/api/diagnostics/ax-migration');
    const body = JSON.parse(init.body);
    expect(body.answers.system).toBe('as400');
    expect(body.privacyConsent).toBe(true);
    expect(body.tracking).toMatchObject({ utmSource: 'google', utmMedium: 'cpc', ref: 'partner-a' });
    expect(body).not.toHaveProperty('score');
  });

  it('shows a rate-limit message on 429', async () => {
    const user = userEvent.setup();
    render(withIntl(<AxDiagnosisFlow locale="ja" />));
    await user.click(screen.getByRole('button', { name: '診断をはじめる' }));
    await answerAll(user);
    await fillContact(user);
    fetchMock.mockResolvedValueOnce(jsonResponse(429, {}));
    await user.click(screen.getByRole('button', { name: '診断結果を見る' }));
    expect(
      await screen.findByText('短時間に送信が集中しています。1分ほど待ってからお試しください。')
    ).toBeInTheDocument();
  });

  it('goes back to the question the server rejected', async () => {
    const user = userEvent.setup();
    render(withIntl(<AxDiagnosisFlow locale="ja" />));
    await user.click(screen.getByRole('button', { name: '診断をはじめる' }));
    await answerAll(user);
    await fillContact(user);
    fetchMock.mockResolvedValueOnce(
      jsonResponse(400, { issues: [{ questionId: 'system', code: 'invalid_option' }] })
    );
    await user.click(screen.getByRole('button', { name: '診断結果を見る' }));
    expect(await screen.findByText('ステップ 2 / 5')).toBeInTheDocument();
    expect(screen.getByText('送信できませんでした。時間をおいてもう一度お試しください。')).toBeInTheDocument();
  });
});

describe('AxDiagnosisResult', () => {
  it('shows levels, the primary challenge and requests a consultation once', async () => {
    const user = userEvent.setup();
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { ok: true, alreadyRequested: false }));
    render(
      withIntl(
        <AxDiagnosisResult
          company="三田製作所"
          submissionId="sub-1"
          result={publicResult}
          consultationRequested={false}
          onRestart={vi.fn()}
        />
      )
    );

    expect(screen.getByTestId('ax-result-difficulty')).toHaveAttribute('data-level', 'medium');
    expect(screen.getByText('ヒト：人に依存した基幹システム')).toBeInTheDocument();
    expect(screen.queryByText('無料', { exact: true })).not.toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: '無料の個別相談を申し込む' }));
    await waitFor(() =>
      expect(screen.getByText('個別相談のお申し込みを受け付けました')).toBeInTheDocument()
    );
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/diagnostics/ax-migration/consultation',
      expect.objectContaining({ method: 'POST', body: JSON.stringify({ submissionId: 'sub-1' }) })
    );
  });

  it('shows an error when the consultation request fails', async () => {
    const user = userEvent.setup();
    fetchMock.mockResolvedValueOnce(jsonResponse(500, {}));
    render(
      withIntl(
        <AxDiagnosisResult
          company="x"
          submissionId="sub-1"
          result={publicResult}
          consultationRequested={false}
          onRestart={vi.fn()}
        />
      )
    );
    await user.click(screen.getByRole('button', { name: '無料の個別相談を申し込む' }));
    expect(
      await screen.findByText('受け付けできませんでした。時間をおいてもう一度お試しください。')
    ).toBeInTheDocument();
  });

  it('explains a weak estimate and the "no challenge" case', () => {
    render(
      withIntl(
        <AxDiagnosisResult
          company="x"
          submissionId="sub-1"
          result={{
            ...publicResult,
            needsHearing: true,
            challenges: { ...publicResult.challenges, primary: null, selected: ['none'] },
          }}
          consultationRequested
          onRestart={vi.fn()}
        />
      )
    );
    expect(screen.getByText(/「わからない」の回答が多いため/)).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { name: '現時点で大きな課題は感じていないとのご回答でした' })
    ).toBeInTheDocument();
    expect(screen.getByText('個別相談のお申し込みを受け付けました')).toBeInTheDocument();
  });
});
