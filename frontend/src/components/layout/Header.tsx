import { useAuthStore } from '../../store/authStore';
import { useNavigate } from 'react-router-dom';
import { LogOutIcon, UserIcon } from 'lucide-react';

export function Header() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left: Page title will be here (from context) */}
        <div>
          {/* This can be filled by page-specific content */}
        </div>

        {/* Right: User menu */}
        <div className="flex items-center gap-4">
          {user && (
            <>
              <div className="flex items-center gap-2 text-sm">
                <UserIcon className="w-4 h-4 text-gray-500" />
                <span className="text-gray-700">{user.name || user.email}</span>
              </div>
              <button
                onClick={handleLogout}
                className="
                  flex items-center gap-2 px-3 py-2 
                  text-sm text-gray-700 
                  hover:bg-gray-100 rounded-lg
                  transition-colors duration-200
                "
                title="ログアウト"
              >
                <LogOutIcon className="w-4 h-4" />
                <span>ログアウト</span>
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
