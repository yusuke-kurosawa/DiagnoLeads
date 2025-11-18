/**
 * LeadForm Component Tests
 *
 * リードフォームのテストテンプレート
 * TODO: 実装を追加してください
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

// TODO: LeadFormコンポーネントをインポート
// import { LeadForm } from '../../leads/LeadForm';

describe('LeadForm', () => {
  it.skip('フォームが正しくレンダリングされる', () => {
    // TODO: コンポーネントの実装後、skipを削除
    // render(<LeadForm />);

    // expect(screen.getByLabelText(/名前/i)).toBeInTheDocument();
    // expect(screen.getByLabelText(/メールアドレス/i)).toBeInTheDocument();
    // expect(screen.getByLabelText(/会社名/i)).toBeInTheDocument();
  });

  it.skip('必須フィールドのバリデーションが機能する', async () => {
    // TODO: コンポーネントの実装後、skipを削除
    // render(<LeadForm />);

    // const submitButton = screen.getByRole('button', { name: /送信/i });
    // fireEvent.click(submitButton);

    // await waitFor(() => {
    //   expect(screen.getByText(/名前は必須です/i)).toBeInTheDocument();
    //   expect(screen.getByText(/メールアドレスは必須です/i)).toBeInTheDocument();
    // });
  });

  it.skip('メールアドレスのフォーマットバリデーションが機能する', async () => {
    // TODO: コンポーネントの実装後、skipを削除
    // const user = userEvent.setup();
    // render(<LeadForm />);

    // const emailInput = screen.getByLabelText(/メールアドレス/i);
    // await user.type(emailInput, 'invalid-email');

    // const submitButton = screen.getByRole('button', { name: /送信/i });
    // fireEvent.click(submitButton);

    // await waitFor(() => {
    //   expect(screen.getByText(/正しいメールアドレスを入力してください/i)).toBeInTheDocument();
    // });
  });

  it.skip('フォーム送信時にハンドラーが呼ばれる', async () => {
    // TODO: コンポーネントの実装後、skipを削除
    // const user = userEvent.setup();
    // const handleSubmit = vi.fn();

    // render(<LeadForm onSubmit={handleSubmit} />);

    // await user.type(screen.getByLabelText(/名前/i), '山田太郎');
    // await user.type(screen.getByLabelText(/メールアドレス/i), 'yamada@example.com');
    // await user.type(screen.getByLabelText(/会社名/i), '株式会社サンプル');

    // const submitButton = screen.getByRole('button', { name: /送信/i });
    // fireEvent.click(submitButton);

    // await waitFor(() => {
    //   expect(handleSubmit).toHaveBeenCalledWith({
    //     name: '山田太郎',
    //     email: 'yamada@example.com',
    //     company: '株式会社サンプル',
    //   });
    // });
  });
});
