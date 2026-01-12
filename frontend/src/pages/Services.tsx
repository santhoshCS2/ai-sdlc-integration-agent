const Services = () => {
    const agents = [
        {
            title: 'UI/UX Designer',
            description: 'Analyzes PRDs to generate premium Figma design prompts and system blueprints.',
            icon: '🎨',
            color: 'from-pink-500 to-rose-500',
            link: 'https://ui-ux-txvv.onrender.com/'
        },
        {
            title: 'Cloud Architect',
            description: 'Designs scalable, cloud-native infrastructure and database schemas via GitArch.',
            icon: '🏗️',
            color: 'from-blue-500 to-indigo-500',
            link: 'https://gitarch-production.up.railway.app/'
        },
        {
            title: 'Impact Analyst',
            description: 'Analyzes scope, risks, and technical dependencies with detailed reports.',
            icon: '📊',
            color: 'from-indigo-500 to-purple-500'
        },
        {
            title: 'Coding Expert',
            description: 'Converts blueprints into clean, production-ready frontend and backend code.',
            icon: '💻',
            color: 'from-emerald-500 to-teal-500'
        },
        {
            title: 'QA Automation',
            description: 'Generates comprehensive test suites for maximum reliability and coverage.',
            icon: '🧪',
            color: 'from-amber-500 to-orange-500'
        },
        {
            title: 'Security Scanner',
            description: 'Performs deep vulnerability audits and dependency health checks.',
            icon: '🛡️',
            color: 'from-red-500 to-crimson-500'
        },
        {
            title: 'Code Reviewer',
            description: 'Provides expert feedback on codebase optimization and best practices.',
            icon: '🔍',
            color: 'from-zinc-500 to-slate-500'
        }
    ];

    return (
        <div className="min-h-screen bg-black text-white pt-32 pb-24 relative overflow-hidden">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-accent/5 rounded-full blur-[120px] pointer-events-none" />

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
                <div className="text-center mb-24 animate-in fade-in slide-in-from-bottom-4 duration-1000">
                    <div className="inline-block px-4 py-1.5 rounded-full bg-accent/10 border border-accent/20 mb-6">
                        <span className="text-xs font-bold text-accent uppercase tracking-[0.2em]">Agent Ecosystem</span>
                    </div>
                    <h2 className="text-5xl md:text-6xl font-black tracking-tight text-white mb-8">
                        Specialized Intelligence at <br />
                        <span className="text-accent">Every Stage.</span>
                    </h2>
                    <p className="max-w-2xl text-xl text-zinc-400 mx-auto font-medium">
                        Our multi-agent orchestration engine coordinates professional AI agents to handle the entire SDLC with precision.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {agents.map((agent, index) => (
                        <div
                            key={index}
                            className="agent-card group hover:-translate-y-2 animate-in fade-in slide-in-from-bottom-8 duration-700"
                            style={{ animationDelay: `${index * 100}ms` }}
                        >
                            <div className={`w-14 h-14 rounded-2xl flex items-center justify-center mb-8 text-2xl bg-gradient-to-br ${agent.color} shadow-lg ring-4 ring-white/5`}>
                                {agent.icon}
                            </div>
                            <h3 className="text-2xl font-bold text-white mb-4 group-hover:text-accent transition-colors">
                                {agent.title}
                            </h3>
                            <p className="text-zinc-400 leading-relaxed font-medium">
                                {agent.description}
                            </p>

                            <div className="mt-8 flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <span className="status-dot status-active" />
                                    <span className="text-[10px] uppercase tracking-widest font-bold text-zinc-500">Active & Ready</span>
                                </div>
                                {agent.link && (
                                    <a
                                        href={agent.link}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-[10px] uppercase tracking-widest font-bold text-accent hover:text-white transition-colors"
                                    >
                                        Launch Agent →
                                    </a>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Services;

