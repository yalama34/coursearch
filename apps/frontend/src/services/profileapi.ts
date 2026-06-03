import {
    ExplanationsResponse,
    ProfileData,
    RecommendationsData,
} from '../types/types';
import { getCourseById } from './courseapi';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const mapProfile = (data: any): ProfileData => {
    const rawCourses = data.liked_courses || data.favorite_courses || data.favoriteCourses || [];
    const favoriteCourses = rawCourses.map((c: any) => ({
        id: c.course_id || c.id,
        title: c.name || c.title || `Курс #${c.course_id || c.id}`,
        description: c.description || '',
        tags: c.tags || [],
    }));

    return {
        userId: (data.user_id ?? data.userId ?? '').toString(),
        name: data.nickname || data.name || 'User',
        description: data.description ?? undefined,
        interests: data.tags ? data.tags.map((tag: string, i: number) => ({ id: i, label: tag })) : (data.interests || []),
        favoriteCourses: favoriteCourses,
    };
};

export const getProfile = async (userId: string | number): Promise<ProfileData> => {
    const res = await fetch(`${API_BASE_URL}/profile/${userId}`);
    if (!res.ok) {
        if (res.status === 404) throw new Error('User not found');
        throw new Error(`Profile fetch failed: ${res.status}`);
    }
    const data = await res.json();
    return mapProfile(data);
};

export const updateInterests = async (interests: string[], token: string): Promise<void> => {
    const res = await fetch(`${API_BASE_URL}/profile/tags`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Session-Token': token,
        },
        body: JSON.stringify({ tags: interests }),
    });
    if (!res.ok) throw new Error('Failed to update interests');
};

export const getRecommendations = async (
    userId: string | number,
    limit: number = 10,
    force: boolean = false,
): Promise<RecommendationsData> => {
    const forceParam = force ? '&force=true' : '';
    const res = await fetch(`${API_BASE_URL}/recommendations?user_id=${userId}&limit=${limit}${forceParam}`);
    if (!res.ok) {
        if (res.status === 503) throw new Error('ML service unavailable');
        throw new Error(`Recommendations fetch failed: ${res.status}`);
    }
    const data = await res.json();

    const items = data.items || data.recommendations || [];

    const mappedRecommendations = await Promise.all(
        items.map(async (item: any) => {
            const courseId = item.item_id || item.id;
            const explanation = item.explanation
                ? {
                      text: '',
                      confidence: item.explanation.confidence ?? null,
                  }
                : undefined;

            try {
                const courseDetails = await getCourseById(courseId.toString());
                return {
                    id: courseId,
                    title: courseDetails.title || courseDetails.name || `Курс #${courseId}`,
                    description: courseDetails.description || '',
                    tags: courseDetails.tags || [],
                    author: courseDetails.author || '',
                    imageUrl: courseDetails.imageUrl || '',
                    recommendationExplanation: explanation,
                };
            } catch {
                return {
                    id: courseId,
                    title: `Курс #${courseId}`,
                    description: '',
                    tags: [],
                    author: '',
                    imageUrl: '',
                    recommendationExplanation: explanation,
                };
            }
        })
    );

    return {
        recommendations: mappedRecommendations,
    };
};

export const getRecommendationExplanations = async (
    userId: string | number,
    courseIds: Array<string | number>,
    force: boolean = false,
): Promise<ExplanationsResponse> => {
    if (courseIds.length === 0) {
        return { user_id: Number(userId), explanations: [] };
    }

    const ids = courseIds.join(',');
    const forceParam = force ? '&force=true' : '';
    const res = await fetch(
        `${API_BASE_URL}/recommendations/explanations?user_id=${userId}&course_ids=${ids}${forceParam}`,
    );
    if (!res.ok) {
        if (res.status === 503) throw new Error('ML service unavailable');
        throw new Error(`Explanations fetch failed: ${res.status}`);
    }
    return res.json();
};


export const updateDescription = async (description: string, token: string): Promise<void> => {
    const res = await fetch(`${API_BASE_URL}/profile/description`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Session-Token': token,
        },
        body: JSON.stringify({ description }),
    });

    if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to update description');
    }
};