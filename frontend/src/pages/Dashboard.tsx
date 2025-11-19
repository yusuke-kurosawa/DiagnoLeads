/**
 * Dashboard Page - Modern UI with Design System
 *
 * Main dashboard for authenticated users with Framer Motion animations
 */

import { useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';
import {
  BarChart3,
  Users,
  ClipboardList,
  Sparkles,
  TrendingUp,
  Target,
  Zap,
  ArrowRight
} from 'lucide-react';
import { useTrackDashboardEvents, useGoogleAnalytics } from '../hooks/useGoogleAnalytics';

export default function Dashboard() {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const { trackDashboardViewed } = useTrackDashboardEvents();
  const { trackEvent } = useGoogleAnalytics();

  // Track dashboard view on mount
  useEffect(() => {
    trackDashboardViewed('overview');
  }, [trackDashboardViewed]);

  const handleFeatureClick = (feature: { title: string; href: string }) => {
    if (feature.href === '#') return;

    // Track feature card click
    trackEvent('dashboard_feature_clicked', {
      feature_name: feature.title,
      feature_href: feature.href,
    });

    navigate(feature.href);
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
    <div className="min-h-screen bg-gray-50">


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
                    onClick={() => handleFeatureClick(feature)}
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


        </motion.div>
      </main>
    </div>
  );
}
