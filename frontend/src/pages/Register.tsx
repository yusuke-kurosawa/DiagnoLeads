/**
 * Register Page
 *
 * New user and tenant registration page
 */

import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import type { RegisterData } from '../types/auth';

export default function Register() {
  const navigate = useNavigate();
  const { register, isLoading } = useAuthStore();

  const [formData, setFormData] = useState<RegisterData>({
    email: '',
    password: '',
    name: '',
    tenant_name: '',
    tenant_slug: '',
  });
  const [error, setError] = useState<string>('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Auto-generate slug from tenant name
    if (name === 'tenant_name') {
      const slug = value
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-+|-+$/g, '');
      setFormData((prev) => ({
        ...prev,
        tenant_slug: slug,
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      await register(formData);
      navigate('/dashboard');
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || '登録に失敗しました。もう一度お試しください。');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 py-12">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8">
        {/* Logo/Title */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">DiagnoLeads</h1>
          <p className="text-gray-600 mt-2">新規アカウント登録</p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded">
            {error}
          </div>
        )}

        {/* Register Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700">
              お名前
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="山田 太郎"
            />
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
              メールアドレス
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">
              パスワード（8文字以上）
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              minLength={8}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="••••••••"
            />
          </div>

          <div className="border-t pt-4 mt-4">
            <h3 className="text-sm font-medium text-gray-700 mb-3">組織情報</h3>

            <div className="space-y-4">
              <div>
                <label htmlFor="tenant_name" className="block text-sm font-medium text-gray-700">
                  組織名
                </label>
                <input
                  type="text"
                  id="tenant_name"
                  name="tenant_name"
                  value={formData.tenant_name}
                  onChange={handleChange}
                  required
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="株式会社サンプル"
                />
              </div>

              <div>
                <label htmlFor="tenant_slug" className="block text-sm font-medium text-gray-700">
                  組織ID（URL用）
                </label>
                <input
                  type="text"
                  id="tenant_slug"
                  name="tenant_slug"
                  value={formData.tenant_slug}
                  onChange={handleChange}
                  required
                  pattern="^[a-z0-9-]+$"
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="sample-corp"
                />
                <p className="mt-1 text-xs text-gray-500">
                  英小文字、数字、ハイフンのみ使用可能
                </p>
              </div>
            </div>
          </div>

          <div className="pt-4">
            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? '登録中...' : 'アカウント登録'}
            </button>
          </div>
        </form>

        {/* Login Link */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            すでにアカウントをお持ちですか？{' '}
            <Link to="/login" className="font-medium text-blue-600 hover:text-blue-500">
              サインイン
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
