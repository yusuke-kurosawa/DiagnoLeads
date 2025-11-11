/**
 * Components Showcase Page - Demo all UI components
 * 全コンポーネントのインタラクティブデモページ
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogHeader, DialogTitle, DialogDescription, DialogBody, DialogFooter } from '@/components/ui/dialog';
import { ConfirmDialog } from '@/components/ui/confirm-dialog';
import { AlertDialog } from '@/components/ui/alert-dialog';
import { useToast } from '@/contexts/ToastContext';
import {
  CheckCircle,
  XCircle,
  AlertCircle,
  Info,
  Mail,
  Lock,
  Search,
  Plus,
  Trash,
  Edit,
  Download,
} from 'lucide-react';

export default function ComponentsShowcase() {
  const { toast, success, error, warning, info } = useToast();
  const [modalOpen, setModalOpen] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [alertOpen, setAlertOpen] = useState(false);
  const [alertVariant, setAlertVariant] = useState<'success' | 'error' | 'warning' | 'info'>('success');

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12 text-center"
        >
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary-600 to-primary-700 bg-clip-text text-transparent mb-4">
            DiagnoLeads Component Library
          </h1>
          <p className="text-lg text-gray-600">
            モダンで洗練されたUIコンポーネント集
          </p>
        </motion.div>

        <div className="space-y-12">
          {/* Buttons Section */}
          <Card variant="elevated">
            <CardHeader>
              <CardTitle>Buttons</CardTitle>
              <CardDescription>6種類のvariant、6サイズ、アイコン、ローディング状態</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Variants */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">Variants</h3>
                <div className="flex flex-wrap gap-3">
                  <Button variant="primary">Primary</Button>
                  <Button variant="secondary">Secondary</Button>
                  <Button variant="outline">Outline</Button>
                  <Button variant="ghost">Ghost</Button>
                  <Button variant="destructive">Destructive</Button>
                  <Button variant="success">Success</Button>
                </div>
              </div>

              {/* Sizes */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">Sizes</h3>
                <div className="flex flex-wrap items-center gap-3">
                  <Button size="xs">Extra Small</Button>
                  <Button size="sm">Small</Button>
                  <Button size="md">Medium</Button>
                  <Button size="lg">Large</Button>
                  <Button size="xl">Extra Large</Button>
                  <Button size="icon"><Plus className="w-5 h-5" /></Button>
                </div>
              </div>

              {/* With Icons */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">With Icons</h3>
                <div className="flex flex-wrap gap-3">
                  <Button leftIcon={<Plus className="w-4 h-4" />}>追加</Button>
                  <Button variant="destructive" leftIcon={<Trash className="w-4 h-4" />}>削除</Button>
                  <Button variant="outline" leftIcon={<Edit className="w-4 h-4" />}>編集</Button>
                  <Button variant="success" rightIcon={<Download className="w-4 h-4" />}>ダウンロード</Button>
                </div>
              </div>

              {/* Loading */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">Loading State</h3>
                <Button loading>送信中...</Button>
              </div>
            </CardContent>
          </Card>

          {/* Badges Section */}
          <Card variant="elevated">
            <CardHeader>
              <CardTitle>Badges</CardTitle>
              <CardDescription>7種類のvariant、3サイズ、アイコン、ドットインジケーター</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Variants */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">Variants</h3>
                <div className="flex flex-wrap gap-3">
                  <Badge variant="default">Default</Badge>
                  <Badge variant="primary">Primary</Badge>
                  <Badge variant="success">Success</Badge>
                  <Badge variant="warning">Warning</Badge>
                  <Badge variant="error">Error</Badge>
                  <Badge variant="info">Info</Badge>
                  <Badge variant="outline">Outline</Badge>
                </div>
              </div>

              {/* Sizes */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">Sizes</h3>
                <div className="flex flex-wrap items-center gap-3">
                  <Badge size="sm">Small</Badge>
                  <Badge size="md">Medium</Badge>
                  <Badge size="lg">Large</Badge>
                </div>
              </div>

              {/* With Icons */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">With Icons</h3>
                <div className="flex flex-wrap gap-3">
                  <Badge variant="success" leftIcon={<CheckCircle className="w-3 h-3" />}>完了</Badge>
                  <Badge variant="error" leftIcon={<XCircle className="w-3 h-3" />}>失敗</Badge>
                  <Badge variant="warning" leftIcon={<AlertCircle className="w-3 h-3" />}>警告</Badge>
                  <Badge variant="info" leftIcon={<Info className="w-3 h-3" />}>情報</Badge>
                </div>
              </div>

              {/* Dot Indicator */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">Dot Indicator</h3>
                <div className="flex flex-wrap gap-3">
                  <Badge dot variant="success">オンライン</Badge>
                  <Badge dot variant="error">オフライン</Badge>
                  <Badge dot variant="warning">保留中</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Input Section */}
          <Card variant="elevated">
            <CardHeader>
              <CardTitle>Input Fields</CardTitle>
              <CardDescription>3種類のvariant、3サイズ、アイコン、ラベル、ヘルパーテキスト</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Basic */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">Basic</h3>
                <Input placeholder="基本的な入力フィールド" />
              </div>

              {/* With Label & Icons */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Input
                  label="メールアドレス"
                  leftIcon={<Mail className="w-5 h-5" />}
                  type="email"
                  placeholder="you@example.com"
                  helperText="ログインに使用するメールアドレス"
                />
                <Input
                  label="パスワード"
                  leftIcon={<Lock className="w-5 h-5" />}
                  type="password"
                  placeholder="••••••••"
                  required
                />
              </div>

              {/* States */}
              <div className="space-y-4">
                <h3 className="text-sm font-medium text-gray-700">States</h3>
                <Input
                  leftIcon={<Search className="w-5 h-5" />}
                  placeholder="検索..."
                />
                <Input
                  error
                  helperText="このフィールドは必須です"
                  placeholder="エラー状態"
                />
                <Input
                  variant="success"
                  helperText="入力内容が正しいです"
                  placeholder="成功状態"
                />
              </div>

              {/* Sizes */}
              <div className="space-y-3">
                <h3 className="text-sm font-medium text-gray-700">Sizes</h3>
                <Input inputSize="sm" placeholder="Small" />
                <Input inputSize="md" placeholder="Medium (Default)" />
                <Input inputSize="lg" placeholder="Large" />
              </div>
            </CardContent>
          </Card>

          {/* Toast Section */}
          <Card variant="elevated">
            <CardHeader>
              <CardTitle>Toast Notifications</CardTitle>
              <CardDescription>5種類のvariant、自動消去、進捗バー、アクションボタン</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-3">
                <Button onClick={() => success('成功', '操作が正常に完了しました')}>
                  Success Toast
                </Button>
                <Button onClick={() => error('エラー', '操作に失敗しました')}>
                  Error Toast
                </Button>
                <Button onClick={() => warning('警告', 'この操作には注意が必要です')}>
                  Warning Toast
                </Button>
                <Button onClick={() => info('情報', '新しい更新があります')}>
                  Info Toast
                </Button>
                <Button
                  onClick={() =>
                    toast({
                      title: 'アクション付き',
                      description: 'この通知にはアクションボタンがあります',
                      action: <Button size="sm" variant="outline">元に戻す</Button>,
                    })
                  }
                >
                  With Action
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Dialog Section */}
          <Card variant="elevated">
            <CardHeader>
              <CardTitle>Dialogs & Modals</CardTitle>
              <CardDescription>モーダルダイアログ、確認ダイアログ、アラートダイアログ</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-wrap gap-3">
                <Button onClick={() => setModalOpen(true)}>
                  Modal Dialog
                </Button>
                <Button variant="destructive" onClick={() => setConfirmOpen(true)}>
                  Confirm Dialog
                </Button>
                <Button
                  variant="success"
                  onClick={() => {
                    setAlertVariant('success');
                    setAlertOpen(true);
                  }}
                >
                  Success Alert
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setAlertVariant('error');
                    setAlertOpen(true);
                  }}
                >
                  Error Alert
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Card Variants Section */}
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Card Variants</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card variant="default">
                <CardHeader>
                  <CardTitle>Default</CardTitle>
                  <CardDescription>標準カード</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600">border + shadow-sm</p>
                </CardContent>
              </Card>

              <Card variant="elevated">
                <CardHeader>
                  <CardTitle>Elevated</CardTitle>
                  <CardDescription>浮き上がるカード</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600">shadow-lg + hover effect</p>
                </CardContent>
              </Card>

              <Card variant="outlined">
                <CardHeader>
                  <CardTitle>Outlined</CardTitle>
                  <CardDescription>枠線カード</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600">border-2 + no shadow</p>
                </CardContent>
              </Card>

              <Card variant="filled">
                <CardHeader>
                  <CardTitle>Filled</CardTitle>
                  <CardDescription>塗りつぶしカード</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600">bg-gray-50</p>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>

      {/* Modal Examples */}
      <Dialog open={modalOpen} onClose={() => setModalOpen(false)}>
        <DialogHeader onClose={() => setModalOpen(false)}>
          <DialogTitle>モーダルダイアログ</DialogTitle>
          <DialogDescription>これは標準的なモーダルダイアログです</DialogDescription>
        </DialogHeader>
        <DialogBody>
          <p className="text-gray-600">
            モーダルダイアログはユーザーの注意を引くために使用されます。
            背景をクリックするかESCキーで閉じることができます。
          </p>
        </DialogBody>
        <DialogFooter>
          <Button variant="outline" onClick={() => setModalOpen(false)}>
            キャンセル
          </Button>
          <Button onClick={() => setModalOpen(false)}>
            OK
          </Button>
        </DialogFooter>
      </Dialog>

      <ConfirmDialog
        open={confirmOpen}
        onClose={() => setConfirmOpen(false)}
        onConfirm={() => {
          success('確認完了', '操作を実行しました');
        }}
        variant="destructive"
        title="本当に削除しますか？"
        description="この操作は取り消せません。すべてのデータが削除されます。"
        confirmText="削除する"
        cancelText="キャンセル"
      />

      <AlertDialog
        open={alertOpen}
        onClose={() => setAlertOpen(false)}
        variant={alertVariant}
        title={alertVariant === 'success' ? '成功しました' : 'エラーが発生しました'}
        description={
          alertVariant === 'success'
            ? '操作が正常に完了しました。'
            : '予期しないエラーが発生しました。もう一度お試しください。'
        }
      />
    </div>
  );
}
