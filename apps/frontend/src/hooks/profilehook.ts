import { useState, useEffect, useCallback } from 'react';
import { getProfile } from '../services/profileapi';
import { mockProfile } from '../mock/mockData';
import { ProfileData } from '../types/types';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

interface UseProfileResult {
    profile: ProfileData | null;
    isLoading: boolean;
    error: string | null;
    refetch: () => void;
}

export const useProfile = (userId: string | number): UseProfileResult => {
    const [profile, setProfile] = useState<ProfileData | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchData = useCallback(async () => {
        if (!userId) {
            setIsLoading(false);
            return;
        }
        setIsLoading(true);
        setError(null);

        try {
            if (USE_MOCK) {
                await new Promise((resolve) => setTimeout(resolve, 800));
                setProfile(mockProfile);
            } else {
                const profileData = await getProfile(userId);
                setProfile(profileData);
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load data');
        } finally {
            setIsLoading(false);
        }
    }, [userId]);

    useEffect(() => {
        void fetchData();
    }, [fetchData]);

    return { profile, isLoading, error, refetch: fetchData };
};
