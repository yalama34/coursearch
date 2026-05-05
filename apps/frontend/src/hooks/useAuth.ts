import { useState, useEffect, useCallback } from 'react';
import { authApi } from '../services/authApi';
import { MeResponse } from '../types/types';

export const useAuth = () => {
    const [user, setUser] = useState<MeResponse | null>(null);
    const [token, setToken] = useState<string | null>(localStorage.getItem('authToken'));
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Verify token on mount
    useEffect(() => {
        const initAuth = async () => {
            if (token) {
                try {
                    const me = await authApi.getMe(token);
                    setUser(me);
                } catch (err) {
                    // Invalid token
                    localStorage.removeItem('authToken');
                    setToken(null);
                    setUser(null);
                }
            }
            setIsLoading(false);
        };
        initAuth();
    }, [token]);

    const login = useCallback(async (nickname: string, password: string) => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await authApi.login({ nickname, password });
            localStorage.setItem('authToken', response.token);
            setToken(response.token);
            setUser({ user_id: response.user_id, nickname: response.nickname });
            return true;
        } catch (err: any) {
            setError(err.message);
            return false;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const register = useCallback(async (nickname: string, password: string) => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await authApi.register({ nickname, password });
            localStorage.setItem('authToken', response.token);
            setToken(response.token);
            setUser({ user_id: response.user_id, nickname: response.nickname });
            return true;
        } catch (err: any) {
            setError(err.message);
            return false;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const logout = useCallback(async () => {
        if (token) {
            await authApi.logout(token);
        }
        localStorage.removeItem('authToken');
        setToken(null);
        setUser(null);
    }, [token]);

    return { user, token, isAuthenticated: !!user && !!token, isLoading, error, login, register, logout };
};