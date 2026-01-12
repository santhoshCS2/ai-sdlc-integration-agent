import React, { useState } from 'react';

interface PromptCardProps {
    title: string;
    description: string;
    prompt: string;
    onCopy: () => void;
    externalLink?: string;
    linkLabel?: string;
}

const PromptCard: React.FC<PromptCardProps> = ({ title, description, prompt, onCopy, externalLink, linkLabel }) => {
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText(prompt);
        setCopied(true);
        onCopy();
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="agent-card w-full max-w-3xl mx-auto my-8 animate-in slide-in-from-bottom duration-700">
            <div className="flex justify-between items-start mb-6">
                <div>
                    <h3 className="text-xl font-bold text-white mb-2">{title}</h3>
                    <p className="text-sm text-zinc-400">{description}</p>
                </div>
                <div className="flex flex-col items-end gap-2">
                    <div className="bg-accent/10 px-3 py-1 rounded-full border border-accent/20">
                        <span className="text-[10px] font-bold text-accent uppercase tracking-wider">Action Required</span>
                    </div>
                    {externalLink && (
                        <a
                            href={externalLink}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-[10px] font-bold text-white uppercase tracking-wider hover:text-accent transition-colors flex items-center gap-1"
                        >
                            {linkLabel || 'Open Agent View'}
                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" /></svg>
                        </a>
                    )}
                </div>
            </div>

            <div className="relative group">
                <div className="absolute -inset-0.5 bg-gradient-to-r from-accent to-purple-600 rounded-xl blur opacity-10 group-hover:opacity-20 transition duration-1000"></div>
                <div className="relative bg-black/40 border border-white/5 rounded-xl p-6 font-mono text-sm text-zinc-300 leading-relaxed whitespace-pre-wrap max-h-60 overflow-y-auto">
                    {prompt}
                </div>
                <div className="absolute top-4 right-4 flex gap-2">
                    <button
                        onClick={handleCopy}
                        className={`px-4 py-2 rounded-lg font-bold text-xs transition-all duration-300 ${copied
                                ? 'bg-emerald-500 text-white'
                                : 'bg-white/10 hover:bg-white/20 text-white backdrop-blur-md'
                            }`}
                    >
                        {copied ? '✓ Copied' : 'Copy Prompt'}
                    </button>
                </div>
            </div>

            <div className="mt-8 flex items-center gap-4 text-xs text-zinc-500">
                <span className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-accent"></span>
                    Ready for Figma
                </span>
                <span className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-zinc-700"></span>
                    Next: GitHub Repository Link
                </span>
            </div>
        </div>
    );
};

export default PromptCard;
