import { useState, useRef, useEffect } from 'react';

interface SearchBarProps {
    onSearch?: (query: string, files: File[]) => void;
    isLoading?: boolean;
}

const SearchBar = ({ onSearch, isLoading }: SearchBarProps) => {
    const [searchQuery, setSearchQuery] = useState('');
    const [attachedFiles, setAttachedFiles] = useState<File[]>([]);
    const [isFocused, setIsFocused] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const searchInputRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        if (searchInputRef.current) {
            searchInputRef.current.focus();
        }
    }, []);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            const newFiles = Array.from(e.target.files);
            setAttachedFiles(prev => [...prev, ...newFiles]);
        }
    };

    const removeFile = (index: number) => {
        setAttachedFiles(prev => prev.filter((_, i) => i !== index));
    };

    const handleSubmit = () => {
        if ((searchQuery.trim() || attachedFiles.length > 0) && !isLoading && onSearch) {
            onSearch(searchQuery, attachedFiles);
            setSearchQuery('');
            setAttachedFiles([]);

            // Reset height after submit
            if (searchInputRef.current) {
                searchInputRef.current.style.height = 'auto';
            }
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    return (
        <div className="w-full max-w-4xl mx-auto px-4">
            <div className={`relative transition-all duration-500 rounded-[28px] overflow-hidden ${isFocused
                ? 'shadow-[0_0_50px_-12px_rgba(99,102,241,0.25)] ring-1 ring-accent/40 bg-zinc-900/40'
                : 'shadow-2xl bg-zinc-900/30'
                } border border-zinc-800/50 backdrop-blur-3xl`}>

                <div className="relative p-3">
                    {/* Attached Files display above input area */}
                    {attachedFiles.length > 0 && (
                        <div className="flex flex-wrap gap-2 px-4 py-3 border-b border-zinc-800/20 mb-2 animate-in fade-in slide-in-from-bottom-2 duration-300">
                            {attachedFiles.map((file, index) => (
                                <div key={index} className="flex items-center gap-2 bg-zinc-800/50 border border-zinc-700/30 rounded-xl pl-3 pr-1 py-1.5 text-[11px] text-zinc-300 group/item transition-all hover:border-accent/30">
                                    <svg className="w-3.5 h-3.5 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                                    </svg>
                                    <span className="truncate max-w-[120px] font-medium">{file.name}</span>
                                    <button
                                        onClick={() => removeFile(index)}
                                        className="w-5 h-5 rounded-lg hover:bg-red-500/20 hover:text-red-400 flex items-center justify-center transition-colors"
                                    >
                                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" /></svg>
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}

                    <div className="flex items-end gap-3 px-2">
                        {/* File Upload Button */}
                        <div className="mb-1.5">
                            <button
                                onClick={() => fileInputRef.current?.click()}
                                className="relative w-9 h-9 rounded-full flex items-center justify-center text-zinc-400 hover:text-white transition-all group/plus active:scale-90"
                                title="Attach files"
                            >
                                <div className="absolute inset-0 bg-white/5 opacity-0 group-hover/plus:opacity-100 rounded-full transition-opacity" />
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
                                </svg>
                            </button>
                            <input
                                type="file"
                                multiple
                                hidden
                                ref={fileInputRef}
                                onChange={handleFileChange}
                            />
                        </div>

                        {/* Text Area Input */}
                        <div className="flex-1 min-h-[44px] flex items-center">
                            <textarea
                                ref={searchInputRef}
                                rows={1}
                                value={searchQuery}
                                onFocus={() => setIsFocused(true)}
                                onBlur={() => setIsFocused(false)}
                                onKeyDown={handleKeyDown}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                onInput={(e) => {
                                    const target = e.target as HTMLTextAreaElement;
                                    target.style.height = 'auto';
                                    target.style.height = `${Math.min(target.scrollHeight, 180)}px`;
                                }}
                                placeholder="Message SDLC Orchestrator..."
                                className="w-full bg-transparent border-none focus:ring-0 text-white placeholder-zinc-500 py-2.5 px-0 resize-none overflow-y-auto leading-relaxed text-[15px] font-normal"
                                style={{ height: 'auto' }}
                            />
                        </div>

                        {/* Action Buttons Group */}
                        <div className="flex items-center gap-2 mb-1.5">
                            <button
                                onClick={handleSubmit}
                                disabled={(!searchQuery.trim() && attachedFiles.length === 0) || isLoading}
                                className={`w-9 h-9 rounded-full flex items-center justify-center transition-all duration-300 transform active:scale-90 ${(searchQuery.trim() || attachedFiles.length > 0) && !isLoading
                                    ? 'bg-white text-black hover:bg-zinc-200'
                                    : 'bg-zinc-800 text-zinc-500'
                                    }`}
                            >
                                {isLoading ? (
                                    <div className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                                ) : (
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M5 12h14M12 5l7 7-7 7" />
                                    </svg>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            {/* Small Footer Text */}
            <div className="mt-3 text-center text-[11px] text-zinc-500 font-normal tracking-wide">
                AgntiGravity Orchestrator can make mistakes. Check important info.
            </div>
        </div>
    );
};

export default SearchBar;
