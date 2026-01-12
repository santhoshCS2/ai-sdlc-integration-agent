import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const Header = () => {
  const location = useLocation();

  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navLinks = [
    { name: 'Home', path: '/' },
    { name: 'Services', path: '/services' },
    { name: 'Dashboard', path: '/dashboard', private: true },
  ];

  return (
    <header className="fixed top-0 left-0 right-0 z-[100] transition-all duration-300">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 mt-4">
        <div className="relative glass-panel border-[rgb(17,85,120,0.2)] bg-[rgb(17,27,51,0.4)] backdrop-blur-2xl rounded-2xl p-1 shadow-2xl overflow-hidden">
          <div className="flex h-12 items-center justify-between px-4">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <Link to="/" className="flex items-center gap-2.5 outline-none group">
                <div className="relative">
                  <div className="absolute -inset-1 bg-accent/30 rounded-full blur opacity-0 group-hover:opacity-100 transition duration-500"></div>
                  <img
                    src="/logo.png"
                    alt="Coastal Seven"
                    className="relative w-8 h-8 object-contain transition-all duration-300 group-hover:scale-110"
                  />
                </div>
                <span className="text-lg font-bold tracking-tight text-white group-hover:text-accent transition-colors">
                  Coastal Seven
                </span>
              </Link>
            </div>

            {/* Navigation */}
            <nav className="hidden md:flex items-center gap-1">
              {navLinks.map((link) => {
                if (link.private && !user) return null;
                const isActive = location.pathname === link.path;
                return (
                  <Link
                    key={link.path}
                    to={link.path}
                    className={`px-4 py-1.5 text-sm font-medium rounded-xl transition-all duration-300 ${isActive
                      ? 'bg-accent/10 text-accent border border-accent/20'
                      : 'text-zinc-400 hover:text-white hover:bg-zinc-800/50 border border-transparent'
                      }`}
                  >
                    {link.name}
                  </Link>
                );
              })}
            </nav>

            {/* Auth Actions */}
            <div className="flex items-center gap-3">
              {user ? (
                <div className="flex items-center gap-4 animate-fade-in">
                  <div className="hidden sm:flex flex-col items-end mr-2">
                    <span className="text-xs font-semibold text-white leading-none mb-0.5">
                      {user.first_name}
                    </span>
                    <span className="text-[10px] text-zinc-500 font-mono">
                      pro_account
                    </span>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="p-2 text-zinc-500 hover:text-red-400 hover:bg-red-500/10 rounded-xl transition-all duration-300 group/logout"
                    title="Sign Out"
                  >
                    <svg className="w-5 h-5 group-hover:translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                  </button>
                </div>
              ) : (
                <div className="flex items-center gap-2 animate-fade-in">
                  <Link to="/login" className="px-4 py-1.5 text-sm font-medium text-zinc-400 hover:text-white transition-colors">
                    Sign In
                  </Link>
                  <Link to="/register" className="btn-primary text-xs px-4 py-1.5 rounded-xl shadow-none">
                    Get Started
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;