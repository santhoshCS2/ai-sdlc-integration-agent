import { Link, useLocation } from 'react-router-dom';
import { ROUTES } from '../constants/routes';

const Sidebar = () => {
    const location = useLocation();

    const menuItems = [
        { name: 'SDLC Pipeline', icon: '⚡', path: ROUTES.DASHBOARD },
        { name: 'Repositories', icon: '📁', path: `${ROUTES.DASHBOARD}/repos` },
        { name: 'Documentation', icon: '📄', path: `${ROUTES.DASHBOARD}/docs` },
        { name: 'Analytics', icon: '📊', path: `${ROUTES.DASHBOARD}/analytics` },
        { name: 'Settings', icon: '⚙️', path: `${ROUTES.DASHBOARD}/settings` },
    ];

    return (
        <aside className="fixed left-8 top-32 bottom-8 w-64 glass-panel border-[rgb(17,85,120,0.2)] bg-[rgb(17,27,51,0.6)] backdrop-blur-3xl z-50 flex flex-col p-6 animate-in slide-in-from-left-8 duration-1000">
            <div className="flex items-center gap-3 mb-10 px-2 group cursor-pointer">
                <div className="p-2 rounded-xl bg-accent/20 text-accent transition-all duration-300 group-hover:bg-accent group-hover:text-white shadow-[0_0_20px_rgba(17,85,120,0.3)]">
                    <img
                        src="/src/assets/logo.png"
                        alt="Logo"
                        className="w-5 h-5 object-contain"
                    />
                </div>
            </div>

            <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
                {menuItems.map((item) => (
                    <Link
                        key={item.path}
                        to={item.path}
                        className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${location.pathname === item.path
                            ? 'bg-accent/10 text-accent'
                            : 'text-zinc-500 hover:text-white hover:bg-white/5'
                            }`}
                    >
                        <span className="text-lg">{item.icon}</span>
                        {item.name}
                    </Link>
                ))}
            </nav>

            <div className="p-4 border-t border-white/5">
                <div className="bg-gradient-to-br from-zinc-900 to-black p-4 rounded-2xl border border-white/5">
                    <p className="text-[10px] font-bold text-accent uppercase tracking-widest mb-2">Cloud Usage</p>
                    <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                        <div className="w-2/3 h-full bg-accent"></div>
                    </div>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
