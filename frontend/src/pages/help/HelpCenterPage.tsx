import React, { useCallback } from 'react';
import { BookOpen, Search, ChevronRight } from 'lucide-react';
import { useHelpStore } from '../../store/helpStore';
import { helpCategories, faqItems } from '../../data/helpCategories';
import { useHelpSearch } from '../../hooks/useHelpSearch';

/**
 * Help Center Page
 * Provides comprehensive help documentation and FAQ for all features
 */
export function HelpCenterPage() {
  const { openHelp } = useHelpStore();

  const {
    searchQuery,
    setSearchQuery,
    filteredCategories,
    filteredFaq,
    expandedFaq,
    setExpandedFaq,
  } = useHelpSearch({ categories: helpCategories, faqItems });

  const handleHelpItemClick = useCallback(
    (key: string) => {
      openHelp(key);
    },
    [openHelp]
  );

  const handleFaqToggle = useCallback(
    (index: number) => {
      setExpandedFaq(expandedFaq === index ? null : index);
    },
    [expandedFaq, setExpandedFaq]
  );

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-lg p-8 text-white">
        <div className="flex items-center gap-3 mb-4">
          <BookOpen className="w-8 h-8" />
          <h1 className="text-3xl font-bold">ヘルプセンター</h1>
        </div>
        <p className="text-blue-100 mb-6">
          DiagnoLeadsの使い方やよくある質問をご確認いただけます
        </p>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="ヘルプを検索..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-3 rounded-lg border-0 text-gray-900 placeholder-gray-500 focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Help Categories */}
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-gray-900">機能ガイド</h2>
        {filteredCategories.map((category, categoryIndex) => (
          <div key={categoryIndex} className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center gap-2 mb-4">
              <div className="text-blue-600">
                <category.icon className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">
                {category.title}
              </h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {category.items.map((item) => (
                <button
                  key={item.key}
                  onClick={() => handleHelpItemClick(item.key)}
                  className="flex items-center justify-between p-4 bg-gray-50 hover:bg-blue-50 border border-gray-200 hover:border-blue-300 rounded-lg transition-colors text-left group"
                >
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 group-hover:text-blue-600 mb-1">
                      {item.title}
                    </h4>
                    <p className="text-sm text-gray-600">{item.description}</p>
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-blue-600 ml-2" />
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* FAQ Section */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          よくある質問（FAQ）
        </h2>

        <div className="space-y-3">
          {filteredFaq.map((item, index) => (
            <div
              key={index}
              className="border border-gray-200 rounded-lg overflow-hidden"
            >
              <button
                onClick={() => handleFaqToggle(index)}
                className="w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 transition-colors text-left"
              >
                <span className="font-medium text-gray-900">{item.question}</span>
                <ChevronRight
                  className={`w-5 h-5 text-gray-400 transition-transform ${
                    expandedFaq === index ? 'rotate-90' : ''
                  }`}
                />
              </button>
              {expandedFaq === index && (
                <div className="p-4 bg-white border-t border-gray-200">
                  <p className="text-gray-600 leading-relaxed">{item.answer}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Contact Support */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          問題が解決しませんか？
        </h3>
        <p className="text-gray-600 mb-4">
          サポートチームがお手伝いします。お気軽にお問い合わせください。
        </p>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
          サポートに問い合わせる
        </button>
      </div>
    </div>
  );
}
