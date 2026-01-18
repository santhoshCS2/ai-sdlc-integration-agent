import { useState, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import AgentCard, { AgentStatus } from '../components/AgentCard';
import PRDUploader from '../components/PRDUploader';
import ChatMessage from '../components/ChatMessage';
import PromptCard from '../components/PromptCard';
import MultiAgentWorkflow from '../components/MultiAgentWorkflow';
import { AgentService } from '../api/services/agentService';
import { AGENTS } from '../constants/agents';
import { EXTERNAL_LINKS } from '../constants/externalLinks';

const Dashboard = () => {
    const location = useLocation();
    const [processStarted, setProcessStarted] = useState(true);
    const [currentStepIndex, setCurrentStepIndex] = useState(0);
    const [agentStatuses, setAgentStatuses] = useState<Record<string, AgentStatus>>({
        ...Object.fromEntries(AGENTS.map(a => [a.id, 'idle'])),
        ui_ux: 'running'
    });
    const [isLoading, setIsLoading] = useState(false);
    const [githubRepoUrl, setGithubRepoUrl] = useState('');
    const [githubToken, setGithubToken] = useState('');
    const [messages, setMessages] = useState<any[]>([]);
    const [figmaPrompt, setFigmaPrompt] = useState<string | null>(null);
    const [uploadedFile, setUploadedFile] = useState<File | null>(null);
    const [prdText, setPrdText] = useState<string | null>(null);
    const [isAutoExecution] = useState(true);

    useEffect(() => {
        // Check if we have PRD text passed from Home page
        const state = location.state as { prdText?: string } | null;
        if (state?.prdText) {
            setPrdText(state.prdText);
            setUploadedFile(null);
            setMessages([{
                role: 'user',
                content: `📝 Initiated from Search: ${state.prdText.substring(0, 100)}...`,
                timestamp: new Date().toISOString()
            }]);

            // Auto-trigger analysis
            setTimeout(() => startUIUXAgent(state.prdText), 800);
        }
    }, [location.state]);

    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, currentStepIndex]);

    const handleStartProcess = () => {
        setProcessStarted(true);
        setCurrentStepIndex(0);
        setAgentStatuses(prev => ({ ...prev, [AGENTS[0].id]: 'running' }));
    };

    const handlePRDSubmit = (files: File[]) => {
        if (files && files.length > 0) {
            setUploadedFile(files[0]);
            setPrdText(null); // Clear text if file is uploaded
            setMessages(prev => [...prev, {
                role: 'user',
                content: `📤 Uploaded PRD: ${files[0].name}. Ready for analysis.`,
                timestamp: new Date().toISOString()
            }]);
        }
    };

    const handleTextSubmit = (text: string) => {
        if (text.trim()) {
            setPrdText(text);
            setUploadedFile(null); // Clear file if text is entered
            setMessages(prev => [...prev, {
                role: 'user',
                content: `📝 PRD Text Entered (${text.length} characters). Ready for analysis.`,
                timestamp: new Date().toISOString()
            }]);

            // Auto-trigger analysis for text submit
            setTimeout(() => startUIUXAgent(text), 500);
        }
    };

    const startUIUXAgent = async (directText?: string) => {
        const textToUse = directText?.trim() || prdText?.trim();
        const contentToProcess = textToUse || "Process this PRD for SDLC automation";

        // Prevent starting if no content and no file
        if (!uploadedFile && !textToUse) {
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: '⚠️ Please provide some requirements or upload a PRD file first.',
                timestamp: new Date().toISOString()
            }]);
            return;
        }

        setIsLoading(true);
        try {
            console.log("[Dashboard] Starting UI/UX Agent with:", contentToProcess.substring(0, 50));
            const result = await AgentService.orchestrateSDLC(
                contentToProcess,
                '1',
                uploadedFile || undefined,
                undefined,
                githubToken
            );

            if (result.status === 'success') {
                setAgentStatuses(prev => ({ ...prev, ui_ux: 'success' }));
                if (result.output) {
                    setFigmaPrompt(result.output);
                }

                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: `✅ ${result.agent}: ${result.message}`,
                    timestamp: new Date().toISOString(),
                    agentOutput: result.output,
                    githubUrl: result.github_repo,
                    agentType: 'ui_ux',
                    downloadUrl: result.file_id ? AgentService.getDownloadUrl('ui_ux', result.file_id) : undefined
                }]);
            } else {
                setAgentStatuses(prev => ({ ...prev, ui_ux: 'error' }));
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: `❌ UI/UX Analysis Failed: ${result.message || 'The agent could not process the requirements.'}`,
                    timestamp: new Date().toISOString()
                }]);
            }
        } catch (err) {
            console.error("[Dashboard] UI/UX Error:", err);
            setAgentStatuses(prev => ({ ...prev, ui_ux: 'error' }));
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `❌ Technical Error: Failed to connect to the UI/UX Agent.`,
                timestamp: new Date().toISOString()
            }]);
        } finally {
            setIsLoading(false);
        }
    };


    const advanceToNextStep = async (stepIndex?: number, forcedRepoUrl?: string) => {
        const nextIndex = stepIndex !== undefined ? stepIndex : currentStepIndex + 1;
        const repoToUse = forcedRepoUrl || githubRepoUrl;
        if (nextIndex < AGENTS.length) {
            setCurrentStepIndex(nextIndex);
            setAgentStatuses(prev => ({ ...prev, [AGENTS[nextIndex].id]: 'running' }));
            setIsLoading(true);

            try {
                // Get the latest agent output to pass as context to the next agent
                const prevMessage = [...messages].reverse().find(m => m.agentOutput || m.fileId);
                let query = prevMessage ? prevMessage.agentOutput : "";

                // For Security Scanning and Code Review, pass the file_id instead of raw text
                if (nextIndex + 1 >= 6 && prevMessage?.fileId) {
                    query = prevMessage.fileId;
                }

                console.log(`[Dashboard] Advancing to step ${nextIndex + 1} with context length: ${query?.length || 0}`);

                const result = await AgentService.orchestrateSDLC(
                    query,
                    (nextIndex + 1).toString(),
                    undefined,
                    repoToUse,
                    githubToken
                );

                if (result.status === 'success') {
                    setAgentStatuses(prev => ({ ...prev, [AGENTS[nextIndex].id]: 'success' }));

                    // Use download_url from backend response if available, otherwise construct it
                    const downloadUrl = result.download_url || (result.file_id ? AgentService.getDownloadUrl(AGENTS[nextIndex].id, result.file_id) : undefined);

                    setMessages(prev => [...prev, {
                        role: 'assistant',
                        content: `✅ ${result.agent}: ${result.message}`,
                        timestamp: new Date().toISOString(),
                        agentOutput: result.output,
                        githubUrl: result.github_repo,
                        agentType: AGENTS[nextIndex].id,
                        fileId: result.file_id || 'latest', // Keep fileId for use in next steps
                        downloadUrl: downloadUrl,
                        predictedUrl: result.predicted_url,
                        canFix: result.can_fix
                    }]);

                    if (isAutoExecution && nextIndex < AGENTS.length - 1) {
                        setTimeout(() => advanceToNextStep(nextIndex + 1, result.github_repo), 3000);
                    }
                } else {
                    setAgentStatuses(prev => ({ ...prev, [AGENTS[nextIndex].id]: 'error' }));
                    setMessages(prev => [...prev, {
                        role: 'assistant',
                        content: `❌ ${result.message}`,
                        timestamp: new Date().toISOString()
                    }]);
                }
            } catch (err) {
                setAgentStatuses(prev => ({ ...prev, [AGENTS[nextIndex].id]: 'error' }));
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: `❌ Failed to execute ${AGENTS[nextIndex].name}: ${err}`,
                    timestamp: new Date().toISOString()
                }]);
            } finally {
                setIsLoading(false);
            }
        }
    };


    const handleApplyFix = async (originalRepoUrl: string) => {
        setIsLoading(true);
        try {
            // Find the last message that had a security file ID or use the repo URL
            const prevMessage = [...messages].reverse().find(m => m.agentType === 'security');
            const context = prevMessage?.fileId || "";

            const result = await AgentService.orchestrateSDLC(
                context,
                '7',
                undefined,
                originalRepoUrl,
                githubToken,
                true // applyFix = true
            );

            if (result.status === 'success') {
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: result.output || result.message,
                    timestamp: new Date().toISOString(),
                    agentType: 'review',
                    githubUrl: result.github_repo
                }]);
                setAgentStatuses(prev => ({ ...prev, review: 'success' }));
            }
        } catch (err) {
            console.error("Fix apply failed:", err);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[rgb(17,27,51)] flex flex-col relative overflow-x-hidden">
            <main className="flex-1 w-full max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-12 pt-32 pb-12">
                {/* Global Header & Progress */}
                <div className="flex justify-between items-end mb-12">
                    <div>
                        <div className="inline-block px-3 py-1 rounded-full bg-accent/10 border border-accent/20 mb-4">
                            <span className="text-[10px] font-bold text-accent uppercase tracking-widest">Active Workspace</span>
                        </div>
                        <h1 className="text-4xl font-black text-white tracking-tight">SDLC Orchestration Portal</h1>
                    </div>
                    <div className="text-right">
                        {!processStarted ? (
                            <button
                                onClick={handleStartProcess}
                                className="btn-primary"
                            >
                                Initialize Workflow
                            </button>
                        ) : (
                            <div className="flex items-center gap-4">
                                <div className="text-right">
                                    <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest mb-1">Global Progress</p>
                                    <p className="text-xl font-black text-white">{Math.round(((currentStepIndex + 1) / AGENTS.length) * 100)}%</p>
                                </div>
                                <div className="w-48 h-2 bg-white/5 rounded-full overflow-hidden border border-white/5">
                                    <div
                                        className="h-full bg-accent transition-all duration-1000"
                                        style={{ width: `${((currentStepIndex + 1) / AGENTS.length) * 100}%` }}
                                    />
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Success Banner */}
                {agentStatuses['review'] === 'success' && (
                    <div className="mb-12 animate-in zoom-in duration-700">
                        <div className="bg-gradient-to-r from-emerald-500 to-teal-600 p-8 rounded-[2.5rem] flex items-center justify-between shadow-[0_20px_50px_rgba(16,185,129,0.2)]">
                            <div>
                                <h2 className="text-2xl font-black text-white mb-2">SDLC Workflow Completed Successfully</h2>
                                <p className="text-emerald-100 text-sm font-medium">All 7 specialized agents have completed their tasks. Your project is ready for development.</p>
                            </div>
                            <div className="flex gap-4">
                                <button onClick={() => window.location.reload()} className="px-6 py-3 bg-white/20 hover:bg-white/30 text-white rounded-xl text-xs font-bold transition-all backdrop-blur-md">
                                    New Project
                                </button>
                                <a
                                    href={githubRepoUrl}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className={`px-6 py-3 rounded-xl text-xs font-bold transition-all shadow-lg flex items-center gap-2 ${githubRepoUrl ? 'bg-white/10 text-white hover:bg-white/20' : 'bg-white/10 text-white/50 cursor-not-allowed'}`}
                                    onClick={(e) => !githubRepoUrl && e.preventDefault()}
                                >
                                    GitHub
                                </a>
                            </div>
                        </div>
                    </div>
                )}

                {/* Agent Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
                    {AGENTS.map((agent, index) => {
                        // Find the corresponding workflow result
                        const workflowResult = messages.find(m =>
                            m.content.includes(agent.name) && m.downloadUrl
                        );

                        return (
                            <AgentCard
                                key={agent.id}
                                name={agent.name}
                                purpose={agent.purpose}
                                icon={agent.icon}
                                status={agentStatuses[agent.id]}
                                isActive={currentStepIndex === index}
                                showContinue={
                                    currentStepIndex === index &&
                                    agentStatuses[agent.id] === 'success' &&
                                    index < AGENTS.length - 1 &&
                                    (index !== 0 || githubRepoUrl !== '') // Step 1 needs repo
                                }
                                onContinue={advanceToNextStep}
                                showDownload={!!workflowResult?.downloadUrl}
                                downloadUrl={workflowResult?.downloadUrl}
                                githubUrl={workflowResult?.githubUrl}
                                summary={workflowResult ? `Agent completed successfully` : undefined}
                            />
                        );
                    })}
                </div>

                {/* Visual Pipeline Status */}
                {processStarted && (
                    <div className="mb-16 animate-in fade-in zoom-in duration-1000">
                        <MultiAgentWorkflow
                            currentStepId={AGENTS[currentStepIndex]?.id}
                            steps={AGENTS.map(agent => ({
                                id: agent.id,
                                name: agent.name,
                                description: agent.purpose,
                                icon: agent.icon,
                                status: (agentStatuses[agent.id] === 'success' ? 'completed' :
                                    (agentStatuses[agent.id] === 'idle' ? 'idle' :
                                        (agentStatuses[agent.id] === 'error' ? 'error' : 'running'))) as any
                            }))}
                        />
                    </div>
                )}

                {/* Interactive Section */}
                {processStarted && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 animate-in fade-in slide-in-from-bottom-8 duration-1000">
                        <div className="lg:col-span-2 space-y-6">
                            <div className="glass-panel p-8 border-white/5 min-h-[400px] flex flex-col">
                                <div className="flex-1 space-y-6 mb-8 max-h-[500px] overflow-y-auto pr-4 scrollbar-thin scrollbar-thumb-white/10">
                                    {messages.length === 0 && currentStepIndex === 0 && (
                                        <div className="text-center py-20">
                                            <div className="w-16 h-16 bg-accent/10 rounded-2xl flex items-center justify-center mx-auto mb-6 border border-accent/20">
                                                <span className="text-2xl">📄</span>
                                            </div>
                                            <h3 className="text-xl font-bold text-white mb-2">Requirement Analysis</h3>
                                            <p className="text-sm text-zinc-500 max-w-sm mx-auto">
                                                Please upload your Product Requirement Document (PRD) to begin the architectural design sequence.
                                            </p>
                                        </div>
                                    )}
                                    {messages.map((m, i) => (
                                        <ChatMessage
                                            key={i}
                                            role={m.role}
                                            content={m.content}
                                            timestamp={m.timestamp}
                                            canFix={m.canFix}
                                            onApplyFix={() => handleApplyFix(m.githubUrl || githubRepoUrl)}
                                            downloadUrl={m.downloadUrl}
                                            agentType={m.agentType}
                                        />
                                    ))}
                                    {figmaPrompt && currentStepIndex === 0 && (
                                        <PromptCard
                                            title="Figma Design System Prompt"
                                            description="Copy this prompt to Figma AI or use our specialized UI/UX engine."
                                            prompt={figmaPrompt}
                                            onCopy={() => { }}
                                            externalLink={EXTERNAL_LINKS.UI_UX_TOOL}
                                            linkLabel="Launch UI/UX Engine"
                                        />
                                    )}
                                    {isLoading && (
                                        <div className="flex justify-start animate-pulse">
                                            <div className="bg-zinc-900 px-6 py-4 rounded-2xl flex gap-2">
                                                <div className="w-1.5 h-1.5 bg-accent rounded-full animate-bounce"></div>
                                                <div className="w-1.5 h-1.5 bg-accent rounded-full animate-bounce [animation-delay:0.2s]"></div>
                                                <div className="w-1.5 h-1.5 bg-accent rounded-full animate-bounce [animation-delay:0.4s]"></div>
                                            </div>
                                        </div>
                                    )}
                                    <div ref={messagesEndRef} />
                                </div>

                                <div className="pt-6 border-t border-white/5">
                                    {currentStepIndex === 0 && !figmaPrompt && (
                                        <div className="flex-1 overflow-y-auto space-y-6 pr-4">
                                            {/* GitHub Configuration (Before Start) */}
                                            <div className="p-6 rounded-[2rem] bg-zinc-900/50 border border-white/5 space-y-4">
                                                <div className="flex items-center justify-between">
                                                    <h3 className="text-xs font-bold text-white uppercase tracking-widest flex items-center gap-2">
                                                        <span className="w-2 h-2 bg-emerald-500 rounded-full"></span>
                                                        GitHub Integration (Optional)
                                                    </h3>
                                                    {githubToken && (
                                                        <span className="text-[10px] font-bold text-emerald-500 uppercase tracking-widest">Token Active</span>
                                                    )}
                                                </div>
                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                    <div className="space-y-2">
                                                        <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest ml-1">GitHub Personal Access Token</label>
                                                        <input
                                                            type="password"
                                                            placeholder="ghp_xxxxxxxxxxxx"
                                                            className="input-field py-3 text-xs"
                                                            value={githubToken}
                                                            onChange={(e) => setGithubToken(e.target.value)}
                                                        />
                                                    </div>
                                                    <div className="flex items-end pb-1">
                                                        <p className="text-[10px] text-zinc-500 leading-tight">
                                                            Providing a token allows the agents to automatically create a repository and push generated code/reports.
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>

                                            {!uploadedFile && !prdText ? (
                                                <PRDUploader
                                                    onUpload={(files) => handlePRDSubmit(files)}
                                                    onTextSubmit={(text) => handleTextSubmit(text)}
                                                    isLoading={isLoading}
                                                />
                                            ) : (
                                                <div className="p-6 rounded-[2rem] bg-accent/5 border border-accent/20 border-dashed flex flex-col items-center gap-6 animate-in zoom-in-95 duration-500">
                                                    <div className="flex items-center gap-4">
                                                        <div className="w-12 h-12 bg-accent rounded-2xl flex items-center justify-center text-xl shadow-lg">
                                                            {uploadedFile ? '📄' : '📝'}
                                                        </div>
                                                        <div>
                                                            <p className="text-sm font-bold text-white">
                                                                {uploadedFile ? uploadedFile.name : 'Text-based PRD'}
                                                            </p>
                                                            <p className="text-[10px] text-zinc-500 uppercase tracking-widest font-bold">
                                                                {uploadedFile ? 'PRD Document Loaded' : 'PRD Text Content Ready'}
                                                            </p>
                                                        </div>
                                                    </div>
                                                    <button
                                                        onClick={() => startUIUXAgent()}
                                                        disabled={isLoading}
                                                        className="btn-primary w-full py-4 text-lg flex items-center justify-center gap-3 transition-all hover:scale-[1.02] active:scale-[0.98]"
                                                    >
                                                        {isLoading ? (
                                                            <>
                                                                <div className="w-5 h-5 border-3 border-white/30 border-t-white rounded-full animate-spin" />
                                                                <span>Analyzing PRD...</span>
                                                            </>
                                                        ) : (
                                                            <>
                                                                <span>Generate Functional UI System</span>
                                                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                                                                </svg>
                                                            </>
                                                        )}
                                                    </button>
                                                    <button
                                                        onClick={() => {
                                                            setUploadedFile(null);
                                                            setPrdText(null);
                                                        }}
                                                        className="text-[10px] text-zinc-500 font-bold uppercase tracking-wider hover:text-white transition-colors"
                                                    >
                                                        Change Document
                                                    </button>
                                                </div>
                                            )}
                                        </div>
                                    )}
                                    {currentStepIndex === 0 && figmaPrompt && (
                                        <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                                            <div className="p-4 rounded-2xl bg-accent/5 border border-accent/20">
                                                <p className="text-[11px] font-bold text-accent uppercase tracking-widest mb-2">Stage 2: Architecture Planning</p>
                                                <p className="text-zinc-400 text-xs leading-relaxed">
                                                    Provide your GitHub Repository details to start the deep Architecture Analysis. If the repository is private, please provide a Personal Access Token.
                                                </p>
                                            </div>

                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                <div className="flex flex-col gap-2">
                                                    <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest ml-1">GitHub Repository URL</label>
                                                    <input
                                                        type="text"
                                                        placeholder="https://github.com/username/repo"
                                                        className="input-field"
                                                        value={githubRepoUrl}
                                                        onChange={(e) => setGithubRepoUrl(e.target.value)}
                                                    />
                                                </div>
                                                <div className="flex flex-col gap-2">
                                                    <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest ml-1">GitHub Token (Optional)</label>
                                                    <input
                                                        type="password"
                                                        placeholder="ghp_xxxxxxxxxxxx"
                                                        className="input-field"
                                                        value={githubToken}
                                                        onChange={(e) => setGithubToken(e.target.value)}
                                                    />
                                                </div>
                                            </div>

                                            <button
                                                onClick={() => advanceToNextStep(1)}
                                                disabled={!githubRepoUrl || isLoading}
                                                className="btn-primary w-full py-4 flex items-center justify-center gap-3 group"
                                            >
                                                {isLoading ? (
                                                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                                ) : (
                                                    <>
                                                        <span className="text-lg">Start Architecture Analysis</span>
                                                        <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                                                        </svg>
                                                    </>
                                                )}
                                            </button>
                                        </div>
                                    )}
                                    {currentStepIndex > 0 && agentStatuses[AGENTS[currentStepIndex].id] === 'success' && (
                                        <div className="p-4 rounded-2xl bg-emerald-500/5 border border-emerald-500/20 text-center">
                                            <p className="text-xs font-bold text-emerald-500 uppercase tracking-widest">Stage Complete</p>
                                            <p className="text-zinc-400 text-[10px] mt-1">Review the output above and click 'Continue' on the agent card.</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>

                        <div className="space-y-6">
                            <div className="glass-panel p-6 border-white/5">
                                <h4 className="text-sm font-bold text-white mb-6 flex items-center gap-2">
                                    <span className="w-1.5 h-1.5 bg-accent rounded-full"></span>
                                    User Manual
                                </h4>
                                <div className="space-y-4">
                                    {[
                                        "Open your browser",
                                        "Go to https://www.figma.com",
                                        "Login to your Figma account",
                                        "Create a new design file",
                                        "Open the Figma AI / prompt input",
                                        "Paste the generated prompt",
                                        "Generate the Figma design"
                                    ].map((step, i) => (
                                        <div key={i} className="flex gap-4 group">
                                            <div className="w-6 h-6 rounded-lg bg-zinc-900 border border-white/10 flex items-center justify-center text-[10px] font-bold text-zinc-500 shrink-0 group-hover:border-accent/40 group-hover:text-accent transition-all">
                                                {i + 1}
                                            </div>
                                            <p className="text-[11px] text-zinc-400 leading-relaxed pt-0.5">
                                                {step}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div className="agent-card p-6 border-emerald-500/20 bg-emerald-500/5">
                                <h4 className="text-xs font-bold text-emerald-500 mb-4 uppercase tracking-[0.2em]">System Status</h4>
                                <div className="space-y-3">
                                    <div className="flex justify-between items-center text-[10px]">
                                        <span className="text-zinc-500">Infrastructure</span>
                                        <span className="text-white font-bold font-mono">ONLINE</span>
                                    </div>
                                    <div className="flex justify-between items-center text-[10px]">
                                        <span className="text-zinc-500">AI Compute Pool</span>
                                        <span className="text-white font-bold font-mono">STABLE (0.4ms)</span>
                                    </div>
                                    <div className="flex justify-between items-center text-[10px]">
                                        <span className="text-zinc-500">Security Mesh</span>
                                        <span className="text-emerald-500 font-bold font-mono">ACTIVE</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
};

export default Dashboard;
