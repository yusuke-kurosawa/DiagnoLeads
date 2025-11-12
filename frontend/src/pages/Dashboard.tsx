/**
 * Dashboard Page - Modern UI with Design System
 *
 * Main dashboard for authenticated users with Framer Motion animations
 */

import { useAuthStore } from '../store/authStore';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  BarChart3, 
  Users, 
  ClipboardList, 
  Sparkles, 
  TrendingUp,
  Target,
  Zap,
  ArrowRight,
  LogOut,
  Plus
} from 'lucide-react';

export default function Dashboard() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const features = [
    {
      icon: ClipboardList,
      title: '診断作成',
      description: 'AI駆動のノーコードビルダーで簡単に診断を作成',
      gradient: 'from-blue-500 to-cyan-500',
      href: `/tenants/${user?.tenant_id}/assessments`,
      stats: { label: '公開中', value: '5件' }
    },
    {
      icon: Users,
      title: 'リード管理',
      description: '診断から収集したリードを一元管理・分析',
      gradient: 'from-purple-500 to-pink-500',
      href: `/tenants/${user?.tenant_id}/leads`,
      stats: { label: '今月獲得', value: '47件' }
    },
    {
      icon: BarChart3,
      title: 'アナリティクス',
      description: 'リアルタイムでパフォーマンスを可視化',
      gradient: 'from-orange-500 to-red-500',
      href: `/tenants/${user?.tenant_id}/analytics`,
      stats: { label: 'CVR', value: '18.5%' }
    },
    {
      icon: Sparkles,
      title: 'AI分析',
      description: 'Claude APIでリードの課題を自動検出',
      gradient: 'from-green-500 to-emerald-500',
      href: '#',
      stats: { label: 'ホットリード', value: '12件' },
      badge: 'Beta'
    },
  ];

  const quickStats = [
    { icon: Target, label: '今月の診断完了', value: '234', change: '+12.3%', positive: true },
    { icon: TrendingUp, label: 'コンバージョン率', value: '18.5%', change: '+2.1%', positive: true },
    { icon: Zap, label: '平均スコア', value: '78点', change: '-1.2%', positive: false },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  } as const;

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.3
      }
    }
  } as const;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <motion.header 
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4 }}
        className="sticky top-0 z-50 backdrop-blur-lg bg-white/80 border-b border-gray-200/50 shadow-sm"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <motion.div 
                whileHover={{ rotate: 180, scale: 1.1 }}
                transition={{ duration: 0.3 }}
                className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-600 to-primary-700 flex items-center justify-center shadow-primary"
              >
                <Sparkles className="w-6 h-6 text-white" />
              </motion.div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-primary-700 bg-clip-text text-transparent">
                  DiagnoLeads
                </h1>
                <p className="text-xs text-gray-500">AI-Powered Lead Generation</p>
              </div>
            </div>
            <Button variant="outline" onClick={handleLogout} leftIcon={<LogOut className="w-4 h-4" />} className="border-gray-300 text-gray-700 hover:bg-gray-100">
              ログアウト
            </Button>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="space-y-8"
        >
          {/* Welcome Section */}
          <motion.div variants={itemVariants}>
            <div className="border-0 shadow-xl bg-gray-50 text-gray-900 overflow-hidden rounded-lg p-6">
              <div className="flex justify-between items-start">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900 mb-2">
                    ようこそ、{user?.name}さん！👋
                  </h1>
                  <p className="text-gray-600 text-base">
                    今日も素晴らしいリードを獲得しましょう
                  </p>
                </div>
                <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium border-0">
                  {user?.role}
                </span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                {quickStats.map((stat, idx) => (
                  <motion.div
                    key={idx}
                    whileHover={{ scale: 1.05 }}
                    className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm cursor-pointer"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <stat.icon className="w-5 h-5 text-blue-600" />
                      <span className={`text-xs font-semibold ${stat.positive ? 'text-green-600' : 'text-red-600'}`}>
                        {stat.change}
                      </span>
                    </div>
                    <div className="text-2xl font-bold text-gray-900 mb-1">{stat.value}</div>
                    <div className="text-sm text-gray-600">{stat.label}</div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>

          {/* Feature Cards */}
          <motion.div variants={itemVariants}>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">機能一覧</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {features.map((feature, idx) => (
                <motion.div
                  key={idx}
                  variants={itemVariants}
                  whileHover={{ y: -8 }}
                  transition={{ duration: 0.2 }}
                >
                  <div
                    className="bg-white rounded-lg border border-gray-200 shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden h-full cursor-pointer"
                    onClick={() => feature.href !== '#' && navigate(feature.href)}
                  >
                    <div className={`h-2 bg-gradient-to-r ${feature.gradient}`} />
                    <div className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <motion.div 
                          whileHover={{ rotate: 360, scale: 1.2 }}
                          transition={{ duration: 0.5 }}
                          className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center shadow-lg`}
                        >
                          <feature.icon className="w-6 h-6 text-white" />
                        </motion.div>
                        {feature.badge && (
                          <Badge className="bg-gradient-to-r from-yellow-400 to-orange-500 text-white border-0">
                            {feature.badge}
                          </Badge>
                        )}
                      </div>
                      <h3 className="text-xl font-bold text-gray-900 hover:text-blue-600 transition-colors mb-2">
                        {feature.title}
                      </h3>
                      <p className="text-base text-gray-600 mb-4">
                        {feature.description}
                      </p>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div>
                            <div className="text-xs text-gray-500">{feature.stats.label}</div>
                            <div className="text-2xl font-bold text-gray-900">{feature.stats.value}</div>
                          </div>
                        </div>
                        <motion.div whileHover={{ x: 5 }}>
                          <ArrowRight className="w-5 h-5 text-gray-400" />
                        </motion.div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Getting Started */}
          <motion.div variants={itemVariants}>
            <div className="border border-gray-200 bg-white rounded-lg p-6 shadow-md">
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center shadow-md">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-gray-900">はじめましょう！</h2>
                  <p className="text-gray-600">DiagnoLeadsで最高のリード獲得体験を</p>
                </div>
              </div>
              <div className="space-y-3">
                {[
                  { step: 1, title: '診断を作成', desc: 'AIビルダーでトピックを入力するだけ' },
                  { step: 2, title: 'Webサイトに埋め込み', desc: 'ワンクリックでコードをコピー' },
                  { step: 3, title: 'リードを獲得', desc: 'AIが自動で分析・スコアリング' }
                ].map((item) => (
                  <motion.div
                    key={item.step}
                    whileHover={{ x: 10 }}
                    className="flex items-start space-x-3 cursor-pointer"
                  >
                    <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-bold flex-shrink-0">
                      {item.step}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{item.title}</p>
                      <p className="text-sm text-gray-600">{item.desc}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
              <Button 
                variant="primary" 
                fullWidth 
                className="mt-6 bg-blue-600 text-white hover:bg-blue-700"
                onClick={() => user?.tenant_id && navigate(`/tenants/${user.tenant_id}/assessments`)}
              >
                診断作成を開始
              </Button>
            </div>
          </motion.div>
        </motion.div>
      </main>
    </div>
  );
}
