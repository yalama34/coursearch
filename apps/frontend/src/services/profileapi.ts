import { ProfileData, RecommendationsData } from '../types/types';


const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const mapProfile = (data: any): ProfileData => ({
    userId: (data.user_id ?? data.userId ?? '').toString(),
    name: data.name || 'User',
    interests: data.interests || [],
    favoriteCourses: data.favorite_courses || data.favoriteCourses || [],
});

export const getProfile = async (userId: string | number): Promise<ProfileData> => {
    const res = await fetch(`${API_BASE_URL}/profile/${userId}`);
    if (!res.ok) {
        if (res.status === 404) throw new Error('User not found');
        throw new Error(`Profile fetch failed: ${res.status}`);
    }
    const data = await res.json();
    return mapProfile(data);
};

export const getRecommendations = async (userId: string | number, limit: number = 10): Promise<RecommendationsData> => {
    const res = await fetch(`${API_BASE_URL}/recommendations?user_id=${userId}&limit=${limit}`);
    if (!res.ok) {
        if (res.status === 503) throw new Error('ML service unavailable');
        throw new Error(`Recommendations fetch failed: ${res.status}`);
    }
    const data = await res.json();
    return {
        recommendations: data.recommendations || [],
    };
};