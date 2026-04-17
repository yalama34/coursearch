// src/features/profile/hooks/useProfile.ts

import { useState, useEffect, useCallback } from 'react';
import { getProfile, getRecommendations } from '../services/profileapi';
import { mockProfile, mockRecommendations } from '../mock/mockData';
import { ProfileData, Course } from '../types/types';

// Read from environment variable
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

interface UseProfileResult {
    profile: ProfileData | null;
    recommendations: Course[];
    isLoading: boolean;
    error: string | null;
    refetch: () => void;
}

export const useProfile = (userId: string | number): UseProfileResult => {
    const [profile, setProfile] = useState<ProfileData | null>(null);
    const [recommendations, setRecommendations] = useState<Course[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchData = useCallback(async () => {
        setIsLoading(true);
        setError(null);

        try {
            if (USE_MOCK) {
                await new Promise(resolve => setTimeout(resolve, 800));

                // Use mock data
                setProfile(mockProfile);
                setRecommendations(mockRecommendations.recommendations);
            } else {
                const [profileData, recsData] = await Promise.all([
                    getProfile(userId),
                    getRecommendations(userId, 10),
                ]);
                setProfile(profileData);
                setRecommendations(recsData.recommendations);
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load data');
        } finally {
            setIsLoading(false);
        }
    }, [userId]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    return { profile, recommendations, isLoading, error, refetch: fetchData };
};

