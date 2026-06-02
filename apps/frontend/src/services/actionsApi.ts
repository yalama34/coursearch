const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ActionPayload {
    course_id: string | number;
    action_type: 'view' | 'like' | 'click_link';
}

export interface EngagementPayload {
    course_id: string | number;
    value: number;
}

const getAuthHeaders = (): Record<string, string> => {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    const token = localStorage.getItem('authToken');

    if (token) {
        headers['X-Session-Token'] = token;
    }

    return headers;
};

export interface ActionResponse {
    status: 'ok' | 'liked' | 'already_liked';
}

export const actionsApi = {
    sendAction: async (payload: ActionPayload): Promise<ActionResponse | void> => {
        if (import.meta.env.VITE_USE_MOCK === 'true') {
            console.log('[MOCK] Action:', payload);
            return;
        }

        const res = await fetch(`${API_BASE_URL}/actions`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(payload),
        });
        if (!res.ok) throw new Error('Failed to send action');
        return res.json();
    },

    sendEngagement: async (payload: EngagementPayload) => {
        if (import.meta.env.VITE_USE_MOCK === 'true') {
            console.log('[MOCK] Engagement:', payload);
            return;
        }

        const res = await fetch(`${API_BASE_URL}/engagement`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(payload),
        });
        if (!res.ok) throw new Error('Failed to send engagement');
    },
};