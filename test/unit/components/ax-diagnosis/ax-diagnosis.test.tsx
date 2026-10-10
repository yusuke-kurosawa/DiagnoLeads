/**
 * AX migration diagnosis v2 components (real next-intl messages, fetch mocked)
 */
import { AxDiagnosisFlow } from '@/components/features/ax-diagnosis/ax-diagnosis-flow';
import { AxDiagnosisResult } from '@/components/features/ax-diagnosis/ax-diagnosis-result';
import { axMigrationDefinition } from '@/lib/features/diagnostics/ax-migration/definition';
import { evaluateAxMigration, toPublicResult } from '@/lib/features/diagnostics/ax-migration/evaluate';
import messages from '@/locales/ja/common.json';
import { as400Answers } from '@/test/fixtures/ax-migration';
import { cleanup, render, screen, waitFor, within } from '@testing-library/react';
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
  evaluateAxMigration({ ...as400Answers, source_docs: 'source_missing' })
);

const fetchMock = vi.fn();

beforeEach(() => {
  fetchMock.mockReset();
  window.localStorage.clear();
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

type User = ReturnType<typeof userEvent.setup>;

const next = (user: User) => user.click(screen.getByRole('button', { name: /次へ/ }));
const inGroup = (name: RegExp) => within(screen.getByRole('group', { name }));

async function answerAs400(user: User) {
  await user.click(screen.getByTestId('platform-as400'));
  await user.click(inGroup(/直せる（改修できる）人/).getByLabelText(/当面は続けられる/));
  await user.click(inGroup(/保守期限/).getByLabelText('1〜3年以内'));
  await user.click(inGroup(/データのやり取り/).getByLabelText('いくつかある（3〜9）'));
  await next(user);
  await user.click(inGroup(/プログラムはおよそ何本/).getByLabelText('500〜1,999本'));
  await user.click(inGroup(/どんな言語・方法/).getByLabelText(/RPG IV/));
  await user.click(inGroup(/仕様書は手元/).getByLabelText(/ソースが一部見当たらない/));
  await next(user);
  await user.click(inGroup(/いま感じている課題/).getByLabelText(/扱える人が減って/));
  await user.click(inGroup(/切り替えを目指す時期/).getByLabelText('1〜2年以内'));
  await user.click(inGroup(/業種/).getByLabelText('製造業'));
  await user.click(inGroup(/あなたの立場/).getByLabelText('情報システム部門の責任者'));
  await next(user);
}

async function fillContact(user: User) {
  await user.type(screen.getByLabelText(/会社名/), '三田製作所');
  await user.type(screen.getByLabelText(/お名前/), '山田 太郎');
  await user.type(screen.getByLabelText(/会社のメールアドレス/), 'yamada@example.jp');
  await user.click(screen.getByLabelText('個人情報の取り扱いに同意する'));
}

describe('AxDiagnosisFlow', () => {
  it('starts with the migration path and moves on when one is chosen', async () => {
    const user = userEvent.setup();
    render(withIntl(<AxDiagnosisFlow locale="ja" />));

    expect(screen.getByText('当てはまるものを選ぶと、次の質問に進みます。')).toBeInTheDocument();
    expect(screen.getByText('STEP 1 / 5')).toBeInTheDocument();
    for (const id of ['as400', 'acos', 'access', 'other']) {
      expect(screen.getByTestId(`platform-${id}`)).toBeInTheDocument();
    }

    await user.click(screen.getByTestId('platform-acos'));
    const heading = screen.getByRole('heading', { name: /STEP 2 \/ 5\s*機種と運用/ });
    expect(heading).toHaveFocus();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('names the unanswered questions', async () => {
    const user = userEvent.setup();
    render(withIntl(<AxDiagnosisFlow locale="ja" />));
    await user.click(screen.getByTestId('platform-as400'));
    await next(user);

    // Shown under each question (and repeated for screen readers in the legend)
    expect(document.getElementById('q-maintenance-error')).toHaveTextContent(
      'いずれか1つを選んでください'
    );
    // The group name carries the error once (no repeat through aria-describedby)
    const group = screen.getByRole('group', { name: /直せる（改修できる）人/ });
    expect(group).toHaveAccessibleName(/いずれか1つを選んでください/);
    expect(group.getAttribute('aria-describedby') ?? '').not.toContain('error');
    expect(document.querySelectorAll('p[id^="q-"][id$="-error"]')).toHaveLength(3);
    expect(screen.getByRole('heading', { name: /STEP 2 \/ 5/ })).toBeInTheDocument();
  });

  it('asks the Access questions in the words of the department', async () => {
    const user = userEvent.setup();
    render(withIntl(<AxDiagnosisFlow locale="ja" />));
    await user.click(screen.getByTestId('platform-access'));

    expect(screen.getByRole('group', { name: /直せる（変更できる）人/ })).toBeInTheDocument();
    expect(screen.getByRole('group', { name: /お使いのAccess/ })).toBeInTheDocument();
    // Follow-up questions are not part of the diagnosis itself
    expect(screen.queryByRole('group', { name: /データはどこに置いて/ })).not.toBeInTheDocument();
  });

  it('clears the other choices for an exclusive option and says so', async () => {
    const user = userEvent.setup();
    render(withIntl(<AxDiagnosisFlow locale="ja" />));
    await user.click(screen.getByTestId('platform-as400'));
    await user.click(inGroup(/直せる（改修できる）人/).getByLabelText(/社内に3名以上/));
    await user.click(inGroup(/保守期限/).getByLabelText('3年以上先'));
    await user.click(inGroup(/データのやり取り/).getByLabelText('ほとんどない（0〜2）'));
    await next(user);

    const languages = inGroup(/どんな言語・方法/);
    await user.click(languages.getByLabelText('COBOL'));
    await user.click(languages.getByLabelText('わからない'));
    expect(languages.getByLabelText('COBOL')).not.toBeChecked();
    expect(languages.getByLabelText('わからない')).toBeChecked();
    expect(screen.getByText('ほかの選択を外しました')).toBeInTheDocument();
  });

  it('drops the answers of a path when another one is chosen', async () => {
    const user = userEvent.setup();
    render(withIntl(<AxDiagnosisFlow locale="ja" />));
    await user.click(screen.getByTestId('platform-as400'));
    await user.click(inGroup(/直せる（改修できる）人/).getByLabelText(/社内に3名以上/));
    await user.click(screen.getByRole('button', { name: /戻る/ }));
    expect(screen.getByTestId('platform-as400')).toHaveAttribute('aria-pressed', 'true');

    await user.click(screen.getByTestId('platform-acos'));
    // The same question on the ACOS path keeps its answer
    expect(inGroup(/直せる（改修できる）人/).getByLabelText(/社内に3名以上/)).toBeChecked();
    await user.click(screen.getByRole('button', { name: /戻る/ }));
    await user.click(screen.getByTestId('platform-access'));
    const saved = JSON.parse(window.localStorage.getItem('diagnoleads:ax-diagnosis') ?? '{}');
    expect(saved.answers).toEqual({ platform: 'access' });
  });

  it('offers to continue a diagnosis saved in this browser', async () => {
    window.localStorage.setItem(
      'diagnoleads:ax-diagnosis',
      JSON.stringify({
        version: axMigrationDefinition.version,
        savedAt: Date.now(),
        step: 2,
        answers: { platform: 'as400', maintenance: 'few', support_end: '1_3y', integrations: 'some' },
      })
    );
    const user = userEvent.setup();
    render(withIntl(<AxDiagnosisFlow locale="ja" />));

    await user.click(await screen.findByRole('button', { name: '続きから' }));
    expect(screen.getByRole('heading', { name: /STEP 3 \/ 5\s*規模と作り/ })).toBeInTheDocument();
  });

  it('ignores saved answers older than a week', async () => {
    window.localStorage.setItem(
      'diagnoleads:ax-diagnosis',
      JSON.stringify({
        version: axMigrationDefinition.version,
        savedAt: Date.now() - 8 * 24 * 60 * 60 * 1000,
        step: 1,
        answers: { platform: 'as400' },
      })
    );
    render(withIntl(<AxDiagnosisFlow locale="ja" />));
    await waitFor(() => expect(window.localStorage.getItem('diagnoleads:ax-diagnosis')).toBeNull());
    expect(screen.queryByRole('button', { name: '続きから' })).not.toBeInTheDocument();
  });

  it('asks for the phone number only when a consultation is wanted', async () => {
    const user = userEvent.setup();
    render(withIntl(<AxDiagnosisFlow locale="ja" />));
    await answerAs400(user);

    expect(screen.getByRole('heading', { name: /最後に、ご連絡先/ })).toBeInTheDocument();
    expect(screen.queryByRole('textbox', { name: /電話番号/ })).not.toBeInTheDocument();
    await user.click(screen.getByRole('checkbox', { name: /無料の個別相談を希望する/ }));
    expect(screen.getByRole('textbox', { name: /電話番号/ })).toBeInTheDocument();
  });

  it('checks the phone number and sends the contact step with Enter', async () => {
    fetchMock.mockResolvedValue(
      jsonResponse(201, { submissionId: 'sub-1', consultationRequested: true, result: publicResult })
    );
    const user = userEvent.setup();
    render(withIntl(<AxDiagnosisFlow locale="ja" />));
    await answerAs400(user);
    await fillContact(user);
    await user.click(screen.getByRole('checkbox', { name: /無料の個別相談を希望する/ }));
    const phone = screen.getByRole('textbox', { name: /電話番号/ });
    await user.type(phone, '03-1234-5678 内線12{Enter}');
    expect(document.getElementById('contact-phone-error')).toHaveTextContent(
      '電話番号は数字とハイフンで入力してください'
    );
    expect(fetchMock).not.toHaveBeenCalled();

    // Full-width digits typed with a Japanese IME are fine
    await user.clear(phone);
    await user.type(phone, '０３ー１２３４ー５６７８{Enter}');
    expect(await screen.findByRole('heading', { name: '診断結果' })).toBeInTheDocument();
    expect(JSON.parse(fetchMock.mock.calls[0][1].body).contact.phone).toBe('０３ー１２３４ー５６７８');
  });

  it('names the options that clear the others in the multiple-choice note', async () => {
    const user = userEvent.setup();
    render(withIntl(<AxDiagnosisFlow locale="ja" />));
    await user.click(screen.getByTestId('platform-access'));
    await user.click(inGroup(/直せる（変更できる）人/).getByLabelText(/社内の複数人/));
    await user.click(inGroup(/お使いのAccess/).getByLabelText(/Microsoft 365/));
    await next(user);
    expect(
      screen.getByText('複数選択できます（「どれも当てはまらない（入力・検索・印刷が中心）」を選ぶと、ほかの選択は外れます）')
    ).toBeInTheDocument();
  });

  it('walks the steps with the browser history and leaves a finished diagnosis behind', async () => {
    fetchMock.mockResolvedValue(
      jsonResponse(201, { submissionId: 'sub-1', consultationRequested: false, result: publicResult })
    );
    const user = userEvent.setup();
    render(withIntl(<AxDiagnosisFlow locale="ja" />));
    await answerAs400(user);
    expect(window.history.state.ax.step).toBe(4);

    window.history.back();
    expect(await screen.findByRole('heading', { name: /STEP 4 \/ 5/ })).toBeInTheDocument();
    // The in-page back button walks the same entries
    await user.click(screen.getByRole('button', { name: /戻る/ }));
    expect(await screen.findByRole('heading', { name: /STEP 3 \/ 5/ })).toBeInTheDocument();
    window.history.go(2);
    expect(await screen.findByRole('heading', { name: /最後に、ご連絡先/ })).toBeInTheDocument();

    await fillContact(user);
    await user.click(screen.getByRole('button', { name: /診断結果を見る/ }));
    expect(await screen.findByRole('heading', { name: '診断結果' })).toBeInTheDocument();
    // The step entries are rewound, so the browser's back button leaves the result
    await waitFor(() => expect(window.history.state.ax.step).toBe(0));

    // Another system is a new diagnosis: the finished one's entries no longer show steps
    await user.click(screen.getByRole('button', { name: '別のシステムも診断する' }));
    expect(screen.getByText('STEP 1 / 5')).toBeInTheDocument();
    window.history.forward();
    await new Promise((resolve) => setTimeout(resolve, 20));
    expect(screen.getByText('STEP 1 / 5')).toBeInTheDocument();
    expect(screen.getByTestId('platform-as400')).toBeInTheDocument();
  });

  it('submits the answers of the chosen path and shows the result', async () => {
    fetchMock.mockResolvedValue(
      jsonResponse(201, { submissionId: 'sub-1', consultationRequested: false, result: publicResult })
    );
    const user = userEvent.setup();
    render(withIntl(<AxDiagnosisFlow locale="ja" />));
    await answerAs400(user);
    await fillContact(user);
    await user.click(screen.getByRole('button', { name: /診断結果を見る/ }));

    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe('/api/diagnostics/ax-migration');
    const body = JSON.parse(init.body);
    expect(body.answers).toEqual({
      platform: 'as400',
      maintenance: 'few',
      support_end: '1_3y',
      integrations: 'some',
      as400_programs: '500_1999',
      as400_languages: ['rpg4'],
      source_docs: 'source_missing',
      challenges: ['people'],
      timeline: '1_2y',
      industry: 'manufacturing',
      role: 'it_manager',
    });
    expect(body.contact).toEqual({
      company: '三田製作所',
      name: '山田 太郎',
      email: 'yamada@example.jp',
    });

    expect(await screen.findByRole('heading', { name: '診断結果' })).toHaveFocus();
    expect(screen.getByText('移行元：AS/400（IBM i）')).toBeInTheDocument();
    expect(screen.getByTestId('ax-result-checkpoints')).toHaveTextContent('見つからないソース');
    // Saved answers are removed once the diagnosis is sent
    expect(window.localStorage.getItem('diagnoleads:ax-diagnosis')).toBeNull();
  });
});

describe('AxDiagnosisResult', () => {
  const renderResult = (overrides: Partial<Parameters<typeof AxDiagnosisResult>[0]> = {}) =>
    render(
      withIntl(
        <AxDiagnosisResult
          company="三田製作所"
          platform="as400"
          locale="ja"
          answers={as400Answers}
          submissionId="sub-1"
          result={publicResult}
          consultationRequested={false}
          onDiagnoseAnother={vi.fn()}
          {...overrides}
        />
      )
    );

  it('explains the levels and offers a consultation at the top and the bottom', () => {
    renderResult();
    expect(screen.getByTestId('ax-result-reasons')).toHaveTextContent('判定のポイント');
    expect(screen.getAllByRole('button', { name: /無料の個別相談を申し込む/ })).toHaveLength(2);
    expect(screen.getByText(/いまここ/)).toBeInTheDocument();
  });

  it('lists what to check in-house when the respondent did not know', () => {
    renderResult();
    expect(screen.queryByTestId('ax-result-unknowns')).not.toBeInTheDocument();

    cleanup();
    renderResult({ answers: { ...as400Answers, integrations: 'unknown', as400_languages: ['unknown'] } });
    const unknowns = screen.getByTestId('ax-result-unknowns');
    expect(unknowns).toHaveTextContent('社内で確認すると、結果の精度が上がる項目');
    expect(within(unknowns).getAllByRole('listitem').map((item) => item.textContent)).toEqual([
      '他のシステムや取引先とのデータのやり取りは、いくつありますか？',
      'どんな言語・方法で作られていますか？',
    ]);
  });

  it('records a consultation request and confirms it', async () => {
    fetchMock.mockResolvedValue(jsonResponse(200, { ok: true, alreadyRequested: false }));
    const user = userEvent.setup();
    renderResult();
    await user.click(screen.getAllByRole('button', { name: /無料の個別相談を申し込む/ })[0]);

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/diagnostics/ax-migration/consultation',
      expect.objectContaining({ body: JSON.stringify({ submissionId: 'sub-1' }) })
    );
    expect(await screen.findByText('個別相談のお申し込みを受け付けました')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /無料の個別相談を申し込む/ })).not.toBeInTheDocument();
  });

  it('shows a failed consultation request next to the button that was pressed', async () => {
    fetchMock.mockResolvedValue(jsonResponse(500, {}));
    const user = userEvent.setup();
    renderResult();
    const [top] = screen.getAllByRole('button', { name: /無料の個別相談を申し込む/ });
    await user.click(top);
    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('受け付けできませんでした');
    // Same box as the top button, and the button keeps the focus
    expect(top.closest('div.rounded-2xl')).toContainElement(alert);
    expect(top).toHaveFocus();
  });

  it('refines the result with the optional follow-up questions', async () => {
    const refined = toPublicResult(
      evaluateAxMigration({ ...as400Answers, source_docs: 'source_missing', gaiji: 'many' })
    );
    fetchMock.mockResolvedValue(jsonResponse(200, { result: refined }));
    const user = userEvent.setup();
    renderResult();

    const followUp = screen.getByTestId('ax-follow-up');
    expect(within(followUp).getByText(/結果の精度を上げる追加質問（任意・7問）/)).toBeInTheDocument();
    await user.click(within(followUp).getByRole('button', { name: /追加質問/ }));
    const submit = within(followUp).getByRole('button', { name: '回答して結果を更新する' });
    // Not sendable before anything is answered (and it keeps the focus while sending)
    expect(submit).toHaveAttribute('aria-disabled', 'true');
    await user.click(submit);
    expect(fetchMock).not.toHaveBeenCalled();

    await user.click(within(followUp).getByRole('group', { name: /外字/ }).querySelector('label') as HTMLElement);
    await user.click(submit);

    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe('/api/diagnostics/ax-migration/details');
    expect(JSON.parse(init.body)).toEqual({ submissionId: 'sub-1', answers: { gaiji: 'none' } });
    const done = await screen.findByText(/結果を更新しました/);
    // The confirmation takes the focus, so it is read out
    expect(done.closest('output')).toHaveFocus();
  });

  it('lets the respondent check another system', async () => {
    const onDiagnoseAnother = vi.fn();
    const user = userEvent.setup();
    renderResult({ onDiagnoseAnother });
    await user.click(screen.getByRole('button', { name: '別のシステムも診断する' }));
    expect(onDiagnoseAnother).toHaveBeenCalled();
  });
});
