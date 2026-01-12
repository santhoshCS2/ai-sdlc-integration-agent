const Footer = () => {
  return (
    <footer className="bg-[rgb(11,21,41)] border-t border-[rgb(17,85,120,0.1)] relative overflow-hidden">
      <div className="absolute inset-0 bg-grid-white/[0.01] pointer-events-none"></div>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
          <div className="md:col-span-2">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-8 h-8 rounded-xl bg-[rgb(17,85,120,0.15)] flex items-center justify-center border border-[rgb(17,85,120,0.2)] shadow-lg">
                <img
                  src="/logo.png"
                  alt="Coastal Seven"
                  className="w-5 h-5 object-contain"
                />
              </div>
              <span className="text-2xl font-black tracking-tight text-white">Coastal Seven</span>
            </div>
            <p className="text-zinc-500 max-w-sm text-sm leading-relaxed font-medium">
              Enterprise-grade autonomous SDLC platform.
              Orchestrating specialized agents to build the future of software.
            </p>
          </div>

          <div>
            <h4 className="text-[10px] font-bold text-white uppercase tracking-[0.3em] mb-6">Platform</h4>
            <ul className="space-y-4 text-xs font-semibold text-zinc-500">
              <li className="hover:text-accent transition-all cursor-pointer hover:translate-x-1">Project Management</li>
              <li className="hover:text-accent transition-all cursor-pointer hover:translate-x-1">Code Review</li>
              <li className="hover:text-accent transition-all cursor-pointer hover:translate-x-1">Deployments</li>
              <li className="hover:text-accent transition-all cursor-pointer hover:translate-x-1">Analytics</li>
            </ul>
          </div>

          <div>
            <h4 className="text-[10px] font-bold text-white uppercase tracking-[0.3em] mb-6">Company</h4>
            <ul className="space-y-4 text-xs font-semibold text-zinc-500">
              <li className="hover:text-accent transition-all cursor-pointer hover:translate-x-1">About Us</li>
              <li className="hover:text-accent transition-all cursor-pointer hover:translate-x-1">Careers</li>
              <li className="hover:text-accent transition-all cursor-pointer hover:translate-x-1">Blog</li>
              <li className="hover:text-accent transition-all cursor-pointer hover:translate-x-1">Contact</li>
            </ul>
          </div>
        </div>

        <div className="mt-16 pt-8 border-t border-[rgb(17,85,120,0.1)] flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-[10px] font-bold text-zinc-600 uppercase tracking-widest">
            © 2026 Coastal Seven Enterprise SDLC Platform. All rights reserved.
          </p>
          <div className="flex gap-8">
            <a href="#" className="text-[10px] font-bold text-zinc-600 hover:text-white transition-colors uppercase tracking-widest">Privacy</a>
            <a href="#" className="text-[10px] font-bold text-zinc-600 hover:text-white transition-colors uppercase tracking-widest">Terms</a>
            <a href="#" className="text-[10px] font-bold text-zinc-600 hover:text-white transition-colors uppercase tracking-widest">Security</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;