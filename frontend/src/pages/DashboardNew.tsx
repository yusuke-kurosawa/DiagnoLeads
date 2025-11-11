import { useAuthStore } from '../store/authStore';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  BarChart3, 
  Users, 
  ClipboardList, 
  Sparkles, 
  LogOut,
  TrendingUp,
  Target,
  Zap,
  ArrowRight
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="sticky top-0 z-50 backdrop-blur-lg bg-white/80 border-b border-gray-200/50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shadow-lg">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  DiagnoLeads
                </h1>
                <p className="text-xs text-muted-foreground">AI-Powered Lead Generation</p>
              </div>
            </div>
            <Button variant="outline" onClick={handleLogout} className="gap-2">
              <LogOut className="w-4 h-4" />
              ログアウト
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Welcome Section */}
        <Card className="border-0 shadow-xl bg-gradient-to-br from-blue-600 to-indigo-600 text-white overflow-hidden">
          <CardHeader className="pb-4">
            <div className="flex justify-between items-start">
              <div>
                <CardTitle className="text-3xl text-white mb-2">
                  ようこそ、{user?.name}さん！👋
                </CardTitle>
                <CardDescription className="text-blue-100 text-base">
                  今日も素晴らしいリードを獲得しましょう
                </CardDescription>
              </div>
              <Badge variant="secondary" className="bg-white/20 text-white border-0">
                {user?.role}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
              {quickStats.map((stat, idx) => (
                <div key={idx} className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
                  <div className="flex items-start justify-between mb-2">
                    <stat.icon className="w-5 h-5 text-blue-100" />
                    <span className={`text-xs font-semibold ${stat.positive ? 'text-green-300' : 'text-red-300'}`}>
                      {stat.change}
                    </span>
                  </div>
                  <div className="text-2xl font-bold text-white mb-1">{stat.value}</div>
                  <div className="text-sm text-blue-100">{stat.label}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Feature Cards */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">機能一覧</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {features.map((feature, idx) => (
              <Card
                key={idx}
                className="group hover:shadow-2xl transition-all duration-300 cursor-pointer border-0 overflow-hidden"
                onClick={() => feature.href !== '#' && navigate(feature.href)}
              >
                <div className={`h-2 bg-gradient-to-r ${feature.gradient}`} />
                <CardHeader>
                  <div className="flex items-start justify-between mb-4">
                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform`}>
                      <feature.icon className="w-6 h-6 text-white" />
                    </div>
                    {feature.badge && (
                      <Badge variant="secondary" className="bg-gradient-to-r from-yellow-400 to-orange-400 text-white border-0">
                        {feature.badge}
                      </Badge>
                    )}
                  </div>
                  <CardTitle className="text-xl group-hover:text-blue-600 transition-colors">
                    {feature.title}
                  </CardTitle>
                  <CardDescription className="text-base">
                    {feature.description}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div>
                        <div className="text-xs text-muted-foreground">{feature.stats.label}</div>
                        <div className="text-2xl font-bold text-gray-900">{feature.stats.value}</div>
                      </div>
                    </div>
                    <Button variant="ghost" size="icon" className="group-hover:translate-x-1 transition-transform">
                      <ArrowRight className="w-5 h-5" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Getting Started */}
        <Card className="border-blue-200 bg-gradient-to-br from-blue-50 to-indigo-50">
          <CardHeader>
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div>
                <CardTitle className="text-blue-900">はじめましょう！</CardTitle>
                <CardDescription>DiagnoLeadsで最高のリード獲得体験を</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-bold flex-shrink-0">
                  1
                </div>
                <div>
                  <p className="font-medium text-gray-900">診断を作成</p>
                  <p className="text-sm text-gray-600">AIビルダーでトピックを入力するだけ</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-bold flex-shrink-0">
                  2
                </div>
                <div>
                  <p className="font-medium text-gray-900">Webサイトに埋め込み</p>
                  <p className="text-sm text-gray-600">ワンクリックでコードをコピー</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-bold flex-shrink-0">
                  3
                </div>
                <div>
                  <p className="font-medium text-gray-900">リードを獲得</p>
                  <p className="text-sm text-gray-600">AIが自動で分析・スコアリング</p>
                </div>
              </div>
            </div>
            <Button className="w-full mt-6 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700">
              診断作成を開始
            </Button>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
