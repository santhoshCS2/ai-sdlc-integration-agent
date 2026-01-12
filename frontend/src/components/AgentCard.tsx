import React from 'react';

export type AgentStatus = 'idle' | 'running' | 'completed' | 'stopped' | 'success' | 'error';

interface AgentCardProps {
    name: string;
    purpose: string;
    status: AgentStatus;
    icon: string;
    isActive: boolean;
    onContinue?: () => void;
    onDownload?: () => void;
    showContinue?: boolean;
    showDownload?: boolean;
    downloadUrl?: string;
    githubUrl?: string;
    summary?: string;
}

const AgentCard: React.FC<AgentCardProps> = ({
    name,
    purpose,
    status,
    icon,
    isActive,
    onContinue,
    onDownload,
    showContinue,
    showDownload,
    downloadUrl,
    githubUrl,
    summary
}) => {
    const statusColors = {
        idle: 'text-zinc-600 bg-zinc-900/50 border-zinc-900',
        running: 'text-accent bg-accent/10 border-accent animate-pulse',
        completed: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/50',
        success: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/50',
        stopped: 'text-amber-500 bg-amber-500/10 border-amber-500/50',
        error: 'text-red-500 bg-red-500/10 border-red-500/50',
    };

    const handleDownload = (e?: React.MouseEvent) => {
        if (e) e.stopPropagation();

        if (downloadUrl) {
            const fullUrl = downloadUrl.startsWith('http')
                ? downloadUrl
                : `http://localhost:8001${downloadUrl}`;
            window.open(fullUrl, '_blank');
        } else if (onDownload) {
            onDownload();
        }
    };

    const handleGitHubOpen = () => {
        if (githubUrl) {
            window.open(githubUrl, '_blank');
        }
    };

    return (
        <div
            onClick={() => status === 'success' && (downloadUrl || githubUrl) ? (downloadUrl ? handleDownload() : handleGitHubOpen()) : null}
            className={`relative overflow-hidden p-8 rounded-[2.5rem] border transition-all duration-700 h-full flex flex-col group/card ${isActive
                ? 'bg-gradient-to-br from-[rgba(17,85,120,0.15)] to-[rgba(17,27,51,0.4)] border-[rgb(17,85,120,0.5)] shadow-[0_30px_60px_-12px_rgba(0,0,0,0.5),0_0_40px_rgba(17,85,120,0.2)] -translate-y-3 scale-[1.02]'
                : 'bg-[rgb(17,27,51,0.4)] border-[rgb(17,85,120,0.1)] hover:border-[rgb(17,85,120,0.3)] hover:bg-[rgb(17,85,120,0.05)] hover:-translate-y-1'
                } ${status === 'success' ? 'cursor-pointer hover:shadow-[0_20px_40px_rgba(0,0,0,0.3)]' : ''}`}>
            <div className="flex justify-between items-start mb-6">
                <div className={`w-12 h-12 rounded-2xl flex items-center justify-center text-2xl border ${isActive ? 'bg-accent/20 border-accent/40 scale-110' : 'bg-white/5 border-white/10'
                    } transition-all duration-700`}>
                    {icon}
                </div>
                <div className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest border ${statusColors[status]}`}>
                    {status}
                </div>
            </div>

            <div className="flex-1">
                <h3 className={`text-lg font-bold mb-2 transition-colors ${isActive ? 'text-white' : 'text-zinc-300'}`}>
                    {name}
                </h3>
                <p className="text-xs text-zinc-500 leading-relaxed line-clamp-3 mb-3">
                    {purpose}
                </p>
                {summary && status === 'success' && (
                    <div className="p-3 bg-emerald-500/5 border border-emerald-500/20 rounded-xl">
                        <p className="text-xs text-emerald-400 font-medium">{summary}</p>
                    </div>
                )}
            </div>

            <div className="mt-6 flex flex-col gap-2">
                {(showDownload || downloadUrl) && status === 'success' && (
                    <button
                        onClick={handleDownload}
                        className="w-full py-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-[10px] font-bold uppercase tracking-widest text-white border border-white/10 transition-all flex items-center justify-center gap-2"
                    >
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1M8 12l4 4m0 0l4-4m-4 4V4" /></svg>
                        Download Report
                    </button>
                )}
                {githubUrl && status === 'success' && (
                    <button
                        onClick={handleGitHubOpen}
                        className="w-full py-2.5 rounded-xl bg-zinc-800/50 hover:bg-zinc-700/50 text-[10px] font-bold uppercase tracking-widest text-white border border-zinc-700/50 transition-all flex items-center justify-center gap-2"
                    >
                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" /></svg>
                        View on GitHub
                    </button>
                )}
                {showContinue && (
                    <button
                        onClick={onContinue}
                        className="w-full btn-primary py-2.5 rounded-xl text-[10px] font-bold uppercase tracking-widest flex items-center justify-center gap-2 group"
                    >
                        Continue Procedure
                        <svg className="w-3 h-3 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6" /></svg>
                    </button>
                )}
            </div>

            {isActive && (
                <div className="absolute bottom-0 left-0 right-0 h-1 bg-accent/20">
                    <div className="h-full bg-accent animate-[shimmer_2s_infinite_linear]" style={{ width: '30%' }}></div>
                </div>
            )}
        </div>
    );
};

export default AgentCard;
