/**
 * Custom hook for help search and filtering
 */

import { useState, useMemo } from 'react';
import { HelpCategory, FAQItem } from '../types/help';
import { matchesSearchQuery } from '../utils/helpUtils';

interface UseHelpSearchProps {
  categories: HelpCategory[];
  faqItems: FAQItem[];
}

interface UseHelpSearchReturn {
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  filteredCategories: HelpCategory[];
  filteredFaq: FAQItem[];
  expandedFaq: number | null;
  setExpandedFaq: (index: number | null) => void;
}

/**
 * Hook to manage help search, filtering, and FAQ expansion
 */
export function useHelpSearch({
  categories,
  faqItems,
}: UseHelpSearchProps): UseHelpSearchReturn {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null);

  // Filter categories based on search query
  const filteredCategories = useMemo(() => {
    if (!searchQuery.trim()) return categories;

    return categories
      .map((category) => ({
        ...category,
        items: category.items.filter(
          (item) =>
            matchesSearchQuery(item.title, searchQuery) ||
            matchesSearchQuery(item.description, searchQuery)
        ),
      }))
      .filter((category) => category.items.length > 0);
  }, [categories, searchQuery]);

  // Filter FAQ items based on search query
  const filteredFaq = useMemo(() => {
    if (!searchQuery.trim()) return faqItems;

    return faqItems.filter(
      (item) =>
        matchesSearchQuery(item.question, searchQuery) ||
        matchesSearchQuery(item.answer, searchQuery)
    );
  }, [faqItems, searchQuery]);

  return {
    searchQuery,
    setSearchQuery,
    filteredCategories,
    filteredFaq,
    expandedFaq,
    setExpandedFaq,
  };
}
