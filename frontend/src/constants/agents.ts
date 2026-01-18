
export interface AgentDefinition {
    id: string;
    name: string;
    purpose: string;
    icon: string;
}

export const AGENTS: AgentDefinition[] = [
    { id: 'ui_ux', name: 'UI/UX Agent', purpose: 'Analyzes PRDs to generate Figma-ready UI/UX prompts and design instructions.', icon: '🎨' },
    { id: 'architecture', name: 'Architecture Agent', purpose: 'Designs scalable system architecture and generates comprehensive design PDFs.', icon: '🏗️' },
    { id: 'impact', name: 'Impact Analysis Agent', purpose: 'Analyzes scope, risks, dependencies, and effort with detailed impact reports.', icon: '📊' },
    { id: 'coding', name: 'Coding Agent', purpose: 'Generates production-ready backend code with clean architecture and proper structure.', icon: '💻' },
    { id: 'testing', name: 'Testing Agent', purpose: 'Generates and executes unit tests to ensure code quality and reliability.', icon: '🧪' },
    { id: 'scanning', name: 'Security Scanning Agent', purpose: 'Performs vulnerability and dependency scans to ensure system security.', icon: '🛡️' },
    { id: 'review', name: 'Code Review Agent', purpose: 'Reviews the full codebase for improvements, best practices, and optimizations.', icon: '🔍' },
];
