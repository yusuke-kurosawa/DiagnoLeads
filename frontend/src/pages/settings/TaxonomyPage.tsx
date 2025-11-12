import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { Layers, Settings } from 'lucide-react';
import TaxonomyManagement from '../../components/admin/TaxonomyManagement';

type TaxonomyTab = 'topics' | 'industries';

export default function TaxonomyPage() {
  const { tenantId } = useParams<{ tenantId: string }>();
  const [activeTab, setActiveTab] = useState<TaxonomyTab>('topics');

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 text-center mb-2">分類設定</h1>
          <p className="text-center text-gray-600">トピックと業界を管理</p>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
          <div className="flex border-b border-gray-200">
            {/* Topic Tab */}
            <button
              onClick={() => setActiveTab('topics')}
              className={`flex-1 px-6 py-3 font-medium text-center transition-colors flex items-center justify-center gap-2 ${
                activeTab === 'topics'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Layers size={18} />
              トピック
            </button>

            {/* Industry Tab */}
            <button
              onClick={() => setActiveTab('industries')}
              className={`flex-1 px-6 py-3 font-medium text-center transition-colors flex items-center justify-center gap-2 ${
                activeTab === 'industries'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Settings size={18} />
              業界
            </button>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'topics' && (
              <TaxonomyManagement type="topics" />
            )}

            {activeTab === 'industries' && (
              <TaxonomyManagement type="industries" />
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
