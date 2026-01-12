
import apiClient from '../client';
import { ENDPOINTS } from '../endpoints';

export interface SDLCResponse {
    status: 'success' | 'error';
    agent?: string;
    message?: string;
    output?: string;
    github_repo?: string;
    file_id?: string;
    download_url?: string;
    can_fix?: boolean;
    predicted_url?: string;
    // Add other fields as per API response
}

export const AgentService = {
    orchestrateSDLC: async (query: string, step: string | number, file?: File, githubUrl?: string, githubToken?: string, applyFix?: boolean): Promise<SDLCResponse> => {
        const formData = new FormData();
        formData.append('query', query);
        formData.append('step', step.toString());

        if (file) {
            formData.append('file', file);
        }
        if (githubUrl) {
            formData.append('github_url', githubUrl);
        }
        if (githubToken) {
            formData.append('github_token', githubToken);
        }
        if (applyFix) {
            formData.append('apply_fix', 'true');
        }

        const response = await apiClient.post<SDLCResponse>(ENDPOINTS.AGENTS.ORCHESTRATE, formData);
        return response.data;
    },

    getDownloadUrl: (agentType: string, fileId: string) => {
        // Return the full download URL using the provided file ID
        return ENDPOINTS.AGENTS.DOWNLOAD(agentType, fileId);
    }
};
