import React from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { Breadcrumbs } from './Breadcrumbs';
import { HelpDialog } from '../help/HelpDialog';
import { useHelpStore } from '../../store/helpStore';
import { getHelpContent } from '../../data/helpContent';

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const { isHelpOpen, currentHelpPage, closeHelp } = useHelpStore();
  const helpContent = currentHelpPage ? getHelpContent(currentHelpPage) : null;

  return (
    <div className="min-h-screen flex bg-gray-50">
      <Sidebar />

      <div className="flex-1 flex flex-col">
        <Header />
        <Breadcrumbs />

        <main className="flex-1 p-6">
          {children}
        </main>
      </div>

      {/* Global Help Dialog */}
      {helpContent && (
        <HelpDialog
          open={isHelpOpen}
          onClose={closeHelp}
          title={helpContent.title}
          description={helpContent.description}
          steps={helpContent.steps}
          sections={helpContent.sections}
          relatedLinks={helpContent.relatedLinks}
        />
      )}
    </div>
  );
}
