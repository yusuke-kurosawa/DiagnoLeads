/**
 * Unit tests for useHelpSearch hook
 */

import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useHelpSearch } from '../useHelpSearch';
import { type HelpCategory, type FAQItem } from '../../types/help';
import { HelpCircle } from 'lucide-react';

const mockCategories: HelpCategory[] = [
  {
    title: 'テストカテゴリー',
    icon: HelpCircle,
    items: [
      {
        key: 'test-1',
        title: 'テスト項目1',
        description: 'これはテストです',
      },
      {
        key: 'test-2',
        title: '別の項目',
        description: '検索テスト用',
      },
    ],
  },
];

const mockFaqItems: FAQItem[] = [
  {
    question: '質問1',
    answer: '回答1',
  },
  {
    question: '質問2',
    answer: '回答2',
  },
];

describe('useHelpSearch', () => {
  it('should initialize with empty search query', () => {
    const { result } = renderHook(() =>
      useHelpSearch({ categories: mockCategories, faqItems: mockFaqItems })
    );

    expect(result.current.searchQuery).toBe('');
    expect(result.current.filteredCategories).toEqual(mockCategories);
    expect(result.current.filteredFaq).toEqual(mockFaqItems);
    expect(result.current.expandedFaq).toBeNull();
  });

  it('should filter categories based on search query', () => {
    const { result } = renderHook(() =>
      useHelpSearch({ categories: mockCategories, faqItems: mockFaqItems })
    );

    act(() => {
      result.current.setSearchQuery('テスト項目');
    });

    expect(result.current.filteredCategories).toHaveLength(1);
    expect(result.current.filteredCategories[0].items).toHaveLength(1);
    expect(result.current.filteredCategories[0].items[0].key).toBe('test-1');
  });

  it('should filter FAQ items based on search query', () => {
    const { result } = renderHook(() =>
      useHelpSearch({ categories: mockCategories, faqItems: mockFaqItems })
    );

    act(() => {
      result.current.setSearchQuery('質問1');
    });

    expect(result.current.filteredFaq).toHaveLength(1);
    expect(result.current.filteredFaq[0].question).toBe('質問1');
  });

  it('should handle FAQ expansion', () => {
    const { result } = renderHook(() =>
      useHelpSearch({ categories: mockCategories, faqItems: mockFaqItems })
    );

    expect(result.current.expandedFaq).toBeNull();

    act(() => {
      result.current.setExpandedFaq(0);
    });

    expect(result.current.expandedFaq).toBe(0);

    act(() => {
      result.current.setExpandedFaq(null);
    });

    expect(result.current.expandedFaq).toBeNull();
  });

  it('should return all items when search query is empty', () => {
    const { result } = renderHook(() =>
      useHelpSearch({ categories: mockCategories, faqItems: mockFaqItems })
    );

    act(() => {
      result.current.setSearchQuery('');
    });

    expect(result.current.filteredCategories).toEqual(mockCategories);
    expect(result.current.filteredFaq).toEqual(mockFaqItems);
  });

  it('should filter by description', () => {
    const { result } = renderHook(() =>
      useHelpSearch({ categories: mockCategories, faqItems: mockFaqItems })
    );

    act(() => {
      result.current.setSearchQuery('検索テスト');
    });

    expect(result.current.filteredCategories[0].items).toHaveLength(1);
    expect(result.current.filteredCategories[0].items[0].key).toBe('test-2');
  });

  it('should filter FAQ by answer', () => {
    const { result } = renderHook(() =>
      useHelpSearch({ categories: mockCategories, faqItems: mockFaqItems })
    );

    act(() => {
      result.current.setSearchQuery('回答1');
    });

    expect(result.current.filteredFaq).toHaveLength(1);
    expect(result.current.filteredFaq[0].answer).toBe('回答1');
  });
});
