import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import type { LoginCredentials } from '../types/auth';

export default function Login() {
  const { login, isLoading } = useAuthStore();

  const [formData, setFormData] = useState<LoginCredentials>({
    email: '',
    password: '',
  });
  const [error, setError] = useState<string>('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    console.log('🔐 Login attempt started...');

    try {
      await login(formData);
      console.log('✅ Login successful! Token and user stored.');
      
      // Use window.location for reliable full page redirect
      console.log('🚀 Redirecting to dashboard...');
      window.location.href = '/dashboard';
    } catch (err: unknown) {
      console.error('❌ Login failed:', err);
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'ログインに失敗しました。もう一度お試しください。');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 py-12 px-4">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">DiagnoLeads</h2>
          <p className="mt-2 text-sm text-gray-600">
            AI-Powered Lead Generation Platform
          </p>
        </div>

        {/* Login Card */}
        <div className="bg-white py-8 px-6 shadow rounded-lg">
          {/* Error Message */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded text-sm">
              {error}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                メールアドレス
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="you@example.com"
              />
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                パスワード
              </label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                minLength={8}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="••••••••"
              />
            </div>

            {/* Submit Button */}
            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? 'サインイン中...' : 'サインイン'}
              </button>
            </div>
          </form>

          {/* Register Link */}
          <div className="mt-6 text-center text-sm">
            <span className="text-gray-600">アカウントをお持ちでないですか？ </span>
            <Link to="/register" className="font-medium text-blue-600 hover:text-blue-500">
              新規登録
            </Link>
          </div>

          {/* Demo Info */}
          <div className="mt-6 space-y-3 border-t pt-4">
            <p className="text-xs font-semibold text-gray-700 text-center">📋 デモアカウント</p>
            
            {/* Admin Account */}
            <div className="p-3 bg-purple-50 rounded border border-purple-200">
              <p className="text-xs font-medium text-purple-900 mb-2">👤 テナント管理者</p>
              <div className="text-xs text-purple-700 space-y-1">
                <p>📧 <code className="bg-white px-1 rounded">admin@demo.example.com</code></p>
                <p>🔐 <code className="bg-white px-1 rounded">Admin@Demo123</code></p>
              </div>
            </div>

            {/* User Account */}
            <div className="p-3 bg-blue-50 rounded border border-blue-200">
              <p className="text-xs font-medium text-blue-900 mb-2">👥 一般ユーザー</p>
              <div className="text-xs text-blue-700 space-y-1">
                <p>📧 <code className="bg-white px-1 rounded">user@demo.example.com</code></p>
                <p>🔐 <code className="bg-white px-1 rounded">User@Demo123</code></p>
              </div>
            </div>

            {/* System Account */}
            <div className="p-3 bg-red-50 rounded border border-red-200">
              <p className="text-xs font-medium text-red-900 mb-2">⚙️ システム管理者</p>
              <div className="text-xs text-red-700 space-y-1">
                <p>📧 <code className="bg-white px-1 rounded">system@demo.example.com</code></p>
                <p>🔐 <code className="bg-white px-1 rounded">System@Demo123</code></p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
