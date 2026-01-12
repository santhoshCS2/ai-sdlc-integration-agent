
export const ENDPOINTS = {
    AUTH: {
        LOGIN: '/auth/login',
        REGISTER: '/auth/register',
        ME: '/auth/me', // Corrected from utils/api.ts which had /auth/me
    },
    AGENTS: {
        LIST: '/agents/',
        CHAT: '/agents/chat',
        STATUS: '/agents/status',
        ORCHESTRATE: '/agents/orchestrate-sdlc',
        DOWNLOAD_LATEST: (agentId: string) => `/agents/download/${agentId}/latest`,
        DOWNLOAD: (agentType: string, fileId: string) => `/agents/download/${agentType}/${fileId}`
    }
} as const;
