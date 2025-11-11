import React from 'react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t border-gray-200 px-6 py-3">
      <div className="flex items-center justify-between text-sm text-gray-500">
        <div>
          © 2025 DiagnoLeads. All rights reserved.
        </div>
        <div className="flex items-center space-x-4">
          <a href="#" className="hover:text-gray-700 transition-colors">
            ヘルプ
          </a>
          <a href="#" className="hover:text-gray-700 transition-colors">
            プライバシー
          </a>
          <a href="#" className="hover:text-gray-700 transition-colors">
            利用規約
          </a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
