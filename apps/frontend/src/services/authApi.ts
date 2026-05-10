import { AuthPayload, AuthResponse, MeResponse } from '../types/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const authApi = {
    register: async (body: AuthPayload): Promise<AuthResponse> => {
        const res = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });

        if (!res.ok) {
            if (res.status === 409) throw new Error('Nickname already taken');
            throw new Error('Registration failed');
        }
        return res.json();
    },

    login: async (body: AuthPayload): Promise<AuthResponse> => {
        const res = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });

        if (!res.ok) {
            if (res.status === 401) throw new Error('Wrong nickname or password');
            throw new Error('Login failed');
        }
        return res.json();
    },

    logout: async (token: string): Promise<void> => {
        const res = await fetch(`${API_BASE_URL}/auth/logout`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Session-Token': token,
            },
        });

        if (!res.ok) throw new Error('Logout failed');
    },

    getMe: async (token: string): Promise<MeResponse> => {
        const res = await fetch(`${API_BASE_URL}/auth/me`, {
            method: 'GET',
            headers: {
                'X-Session-Token': token,
            },
        });

        if (!res.ok) throw new Error('Not authorized');
        return res.json();
    },
};