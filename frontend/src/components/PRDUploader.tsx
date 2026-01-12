import { useState, useRef } from 'react';

interface PRDUploaderProps {
    onUpload: (files: File[]) => void;
    onTextSubmit?: (text: string) => void;
    isLoading: boolean;
}

const PRDUploader = ({ onUpload, onTextSubmit, isLoading }: PRDUploaderProps) => {
    const [attachedFiles, setAttachedFiles] = useState<File[]>([]);
    const [prdText, setPrdText] = useState('');
    const [activeTab, setActiveTab] = useState<'upload' | 'text'>('upload');
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            const newFiles = Array.from(e.target.files);
            setAttachedFiles(prev => [...prev, ...newFiles]);
        }
    };

    const removeFile = (index: number) => {
        setAttachedFiles(prev => prev.filter((_, i) => i !== index));
    };

    const handleFileUpload = () => {
        if (attachedFiles.length > 0 && !isLoading) {
            onUpload(attachedFiles);
            setAttachedFiles([]);
        }
    };

    const handleTextSubmit = () => {
        if (prdText.trim() && !isLoading && onTextSubmit) {
            onTextSubmit(prdText);
            setPrdText('');
        }
    };

    return (
        <div className="w-full max-w-4xl mx-auto px-4">
            <div className="flex gap-2 mb-6">
                <button
                    onClick={() => setActiveTab('upload')}
                    className={`px-6 py-2 rounded-xl text-xs font-bold uppercase tracking-widest transition-all ${activeTab === 'upload' ? 'bg-accent text-white shadow-lg' : 'bg-white/5 text-zinc-500 hover:text-white'}`}
                >
                    Upload File
                </button>
                <button
                    onClick={() => setActiveTab('text')}
                    className={`px-6 py-2 rounded-xl text-xs font-bold uppercase tracking-widest transition-all ${activeTab === 'text' ? 'bg-accent text-white shadow-lg' : 'bg-white/5 text-zinc-500 hover:text-white'}`}
                >
                    Enter Text
                </button>
            </div>

            <div className="relative p-8 bg-zinc-900/30 border-2 border-dashed border-zinc-800/50 rounded-[2rem] backdrop-blur-3xl transition-all hover:border-accent/30 group">
                {activeTab === 'upload' ? (
                    <>
                        <input
                            type="file"
                            multiple
                            hidden
                            ref={fileInputRef}
                            onChange={handleFileChange}
                            accept=".pdf,.docx,.txt"
                        />

                        <div className="flex flex-col items-center justify-center gap-6">
                            {attachedFiles.length === 0 ? (
                                <div
                                    className="flex flex-col items-center cursor-pointer"
                                    onClick={() => fileInputRef.current?.click()}
                                >
                                    <div className="w-16 h-16 rounded-2xl bg-accent/10 flex items-center justify-center text-accent mb-4 group-hover:scale-110 transition-transform">
                                        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                                        </svg>
                                    </div>
                                    <h3 className="text-xl font-bold text-white mb-2">Upload your PRD</h3>
                                    <p className="text-zinc-500 text-sm">PDF, DOCX or TXT files supported</p>
                                </div>
                            ) : (
                                <div className="w-full space-y-4">
                                    <div className="flex flex-wrap gap-3 justify-center">
                                        {attachedFiles.map((file, index) => (
                                            <div key={index} className="flex items-center gap-2 bg-accent/10 border border-accent/20 rounded-xl px-4 py-2 text-sm text-accent animate-in zoom-in duration-300">
                                                <span className="font-bold">{file.name}</span>
                                                <button onClick={() => removeFile(index)} className="hover:text-red-400">
                                                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" /></svg>
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                    <div className="flex justify-center pt-4">
                                        <button
                                            onClick={handleFileUpload}
                                            disabled={isLoading}
                                            className="btn-primary px-12 py-4 text-lg animate-in fade-in slide-in-from-bottom-4 duration-500"
                                        >
                                            {isLoading ? (
                                                <div className="flex items-center gap-3">
                                                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                                    <span>Processing...</span>
                                                </div>
                                            ) : (
                                                "Analyze PRD & Start SDLC"
                                            )}
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                    </>
                ) : (
                    <div className="flex flex-col gap-6">
                        <textarea
                            value={prdText}
                            onChange={(e) => setPrdText(e.target.value)}
                            placeholder="Enter your detailed Project Requirements (PRD) here..."
                            className="w-full h-64 bg-black/40 border border-white/10 rounded-2xl p-6 text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-accent/50 transition-all resize-none"
                        />
                        <div className="flex justify-center">
                            <button
                                onClick={handleTextSubmit}
                                disabled={isLoading || !prdText.trim()}
                                className="btn-primary px-12 py-4 text-lg animate-in fade-in slide-in-from-bottom-4 duration-500 disabled:opacity-50"
                            >
                                {isLoading ? (
                                    <div className="flex items-center gap-3">
                                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                        <span>Analyzing PRD...</span>
                                    </div>
                                ) : (
                                    "Analyze Text & Start SDLC"
                                )}
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default PRDUploader;
