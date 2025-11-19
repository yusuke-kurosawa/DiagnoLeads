/**
 * Unit tests for HelpStepItem component
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { HelpStepItem } from '../HelpStepItem';
import type { HelpStep } from '../../../types/help';

describe('HelpStepItem', () => {
  const mockStep: HelpStep = {
    title: 'テストステップ',
    description: 'これはテストの説明です',
  };

  it('should render step number', () => {
    render(<HelpStepItem step={mockStep} index={0} />);
    expect(screen.getByLabelText('Step 1')).toBeInTheDocument();
    expect(screen.getByText('1')).toBeInTheDocument();
  });

  it('should render step title', () => {
    render(<HelpStepItem step={mockStep} index={0} />);
    expect(screen.getByText('テストステップ')).toBeInTheDocument();
  });

  it('should render step description', () => {
    render(<HelpStepItem step={mockStep} index={0} />);
    expect(screen.getByText('これはテストの説明です')).toBeInTheDocument();
  });

  it('should render image when provided', () => {
    const stepWithImage: HelpStep = {
      ...mockStep,
      image: 'https://example.com/image.png',
    };

    render(<HelpStepItem step={stepWithImage} index={0} />);
    const image = screen.getByRole('img');
    expect(image).toHaveAttribute('src', 'https://example.com/image.png');
    expect(image).toHaveAttribute('alt', 'テストステップ');
    expect(image).toHaveAttribute('loading', 'lazy');
  });

  it('should not render image when not provided', () => {
    render(<HelpStepItem step={mockStep} index={0} />);
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
  });

  it('should use correct index for step number', () => {
    render(<HelpStepItem step={mockStep} index={5} />);
    expect(screen.getByLabelText('Step 6')).toBeInTheDocument();
    expect(screen.getByText('6')).toBeInTheDocument();
  });

  it('should have proper accessibility attributes', () => {
    render(<HelpStepItem step={mockStep} index={0} />);
    const listItem = screen.getByRole('listitem');
    expect(listItem).toBeInTheDocument();
  });
});
