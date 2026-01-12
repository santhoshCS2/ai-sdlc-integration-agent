import React, { useState, useRef, useEffect } from 'react';
import { SEARCH_SUGGESTIONS } from '../constants/options';

interface HomeSearchBarProps {
  onSearch?: (query: string, files: File[]) => void;
  isLoading?: boolean;
}

const HomeSearchBar: React.FC<HomeSearchBarProps> = ({ onSearch, isLoading = false }) => {
  const [query, setQuery] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea like GPT
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [query]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(prev => [...prev, ...Array.from(e.target.files!)]);
    }
  };

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (onSearch && (query.trim() || files.length > 0)) {
      onSearch(query, files);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="w-full max-w-3xl mx-auto px-4">
      <form onSubmit={handleSubmit} className="relative transition-all duration-500">
        <div className="relative flex flex-col bg-[rgb(17,27,51,0.8)] border border-[rgb(17,85,120,0.3)] backdrop-blur-3xl rounded-[26px] shadow-[0_20px_60px_rgba(0,0,0,0.5)] focus-within:border-[rgb(17,85,120,0.5)] focus-within:shadow-[0_20px_60px_rgba(17,85,120,0.2)] transition-all duration-300 overflow-hidden">

          {/* Textarea Area */}
          <div className="flex items-end px-3 py-3 gap-2">
            {/* Attachments Section (Left) */}
            <div className="flex items-center pb-1">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="w-10 h-10 flex items-center justify-center text-zinc-400 hover:text-white hover:bg-white/5 rounded-full transition-all"
                title="Attach files"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
                </svg>
              </button>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                className="hidden"
                onChange={handleFileChange}
              />
            </div>

            {/* Input Area */}
            <textarea
              ref={textareaRef}
              rows={1}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message Coastal Seven..."
              className="flex-1 bg-transparent border-none text-white px-2 py-3 focus:outline-none focus:ring-0 placeholder-zinc-500 text-[16px] leading-relaxed resize-none overflow-y-auto max-h-[200px]"
            />

            {/* Action Buttons (Right) */}
            <div className="flex items-center pb-1">
              <button
                type="submit"
                disabled={isLoading || (!query.trim() && files.length === 0)}
                className={`w-10 h-10 flex items-center justify-center rounded-full transition-all ${isLoading || (!query.trim() && files.length === 0)
                  ? 'bg-zinc-800 text-zinc-500 opacity-50'
                  : 'bg-white text-black hover:bg-zinc-200 shadow-lg'
                  }`}
              >
                {isLoading ? (
                  <div className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin"></div>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M5 10l7-7m0 0l7 7m-7-7v18" />
                  </svg>
                )}
              </button>
            </div>
          </div>

          {/* Files Display (Bottom) */}
          {files.length > 0 && (
            <div className="px-5 pb-4 flex flex-wrap gap-2 animate-in fade-in duration-300">
              {files.map((file, index) => (
                <div
                  key={index}
                  className="group flex items-center gap-2 bg-[#1A1A1A] border border-white/5 pl-3 pr-2 py-1.5 rounded-xl text-xs font-medium text-zinc-300"
                >
                  <span className="max-w-[120px] truncate">{file.name}</span>
                  <button
                    type="button"
                    onClick={() => removeFile(index)}
                    className="text-zinc-500 hover:text-white transition-colors"
                  >
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* GPT Style Quick Suggestions (Optional but feels GPT) */}
        <div className="mt-8 flex flex-wrap justify-center gap-3 animate-in fade-in slide-in-from-bottom-2 duration-1000">
          {SEARCH_SUGGESTIONS.map((tag) => (
            <button
              key={tag}
              type="button"
              onClick={() => setQuery(tag)}
              className="px-4 py-2 rounded-full bg-[rgb(17,85,120,0.1)] border border-[rgb(17,85,120,0.2)] text-[10px] font-bold text-zinc-400 hover:text-white hover:bg-[rgb(17,85,120,0.2)] hover:border-[rgb(17,85,120,0.4)] transition-all uppercase tracking-widest"
            >
              {tag}
            </button>
          ))}
        </div>
      </form>
    </div>
  );
};

export default HomeSearchBar;