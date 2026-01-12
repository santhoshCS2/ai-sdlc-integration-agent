import React from 'react';

interface Step {
    id: string;
    name: string;
    description: string;
    status: 'idle' | 'running' | 'completed' | 'error';
    icon: string;
}

interface MultiAgentWorkflowProps {
    currentStepId: string;
    steps: Step[];
}

const MultiAgentWorkflow: React.FC<MultiAgentWorkflowProps> = ({ currentStepId, steps }) => {
    return (
        <div className="w-full max-w-4xl mx-auto my-12">
            <div className="relative">
                {/* Connection Line */}
                <div className="absolute top-10 left-0 right-0 h-0.5 bg-white/5 -z-10" />
                <div 
                    className="absolute top-10 left-0 h-0.5 bg-accent transition-all duration-1000 -z-10" 
                    style={{ 
                        width: `${(steps.findIndex(s => s.id === currentStepId) / (steps.length - 1)) * 100}%` 
                    }}
                />

                <div className="flex justify-between items-start gap-4">
                    {steps.map((step, index) => {
                        const isActive = step.id === currentStepId;
                        const isCompleted = steps.findIndex(s => s.id === currentStepId) > index;
                        
                        return (
                            <div key={step.id} className="flex flex-col items-center group cursor-help transition-all duration-500">
                                <div 
                                    className={`w-20 h-20 rounded-2xl flex items-center justify-center border-2 transition-all duration-500 ${
                                        isActive 
                                            ? 'bg-accent/20 border-accent shadow-[0_0_30px_rgba(var(--color-accent-rgb),0.3)] animate-float' 
                                            : isCompleted
                                                ? 'bg-emerald-500/10 border-emerald-500/50'
                                                : 'bg-white/5 border-white/10'
                                    }`}
                                >
                                    <span className={`text-2xl ${isActive ? 'scale-125' : ''} transition-transform`}>
                                        {step.icon}
                                    </span>
                                    
                                    {isActive && (
                                        <div className="absolute -inset-2 bg-accent/20 blur-xl rounded-full animate-pulse -z-10" />
                                    )}
                                </div>
                                
                                <div className="mt-4 text-center">
                                    <h4 className={`text-xs font-bold tracking-widest uppercase mb-1 ${
                                        isActive ? 'text-accent' : isCompleted ? 'text-emerald-500' : 'text-zinc-500'
                                    }`}>
                                        {step.name}
                                    </h4>
                                    <div className="flex items-center justify-center gap-1.5">
                                        <div className={`status-dot ${
                                            isActive ? 'status-active' : isCompleted ? 'bg-emerald-500' : 'status-idle'
                                        }`} />
                                        <span className="text-[10px] text-zinc-400 font-medium">
                                            {isActive ? 'Processing' : isCompleted ? 'Completed' : 'Queued'}
                                        </span>
                                    </div>
                                </div>
                                
                                {/* Tooltip */}
                                <div className="absolute top-full mt-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none z-50">
                                    <div className="bg-zinc-900 border border-white/10 p-3 rounded-xl shadow-2xl w-48 text-center">
                                        <p className="text-[10px] text-zinc-400 leading-relaxed">{step.description}</p>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};

export default MultiAgentWorkflow;
