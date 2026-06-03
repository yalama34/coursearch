import { useState, useEffect, useCallback } from 'react';
import {
    getRecommendations,
    getRecommendationExplanations,
} from '../services/profileapi';
import { mockRecommendations } from '../mock/mockData';
import { Course, ExplanationItem } from '../types/types';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

interface UseRecommendationsResult {
    recommendations: Course[];
    isLoading: boolean;
    isRefreshing: boolean;
    isLoadingExplanations: boolean;
    error: string | null;
    refetch: () => void;
    refresh: () => void;
}

const mergeExplanations = (courses: Course[], explanations: ExplanationItem[]): Course[] => {
    const byId = new Map(explanations.map((item) => [item.course_id, item.text]));

    return courses.map((course) => {
        const text = byId.get(Number(course.id));
        if (!text) {
            return course;
        }

        return {
            ...course,
            recommendationExplanation: {
                text,
                confidence: course.recommendationExplanation?.confidence ?? null,
            },
        };
    });
};

export const useRecommendations = (
    userId: string | number,
    limit: number = 10,
): UseRecommendationsResult => {
    const [recommendations, setRecommendations] = useState<Course[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [isLoadingExplanations, setIsLoadingExplanations] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchExplanations = useCallback(async (
        uid: string | number,
        courses: Course[],
        force = false,
    ) => {
        const courseIds = courses.map((course) => course.id);
        if (courseIds.length === 0) {
            return;
        }

        setIsLoadingExplanations(true);
        try {
            const data = await getRecommendationExplanations(uid, courseIds, force);
            setRecommendations((prev) => mergeExplanations(prev, data.explanations));
        } catch (err) {
            console.error('Failed to load recommendation explanations:', err);
        } finally {
            setIsLoadingExplanations(false);
        }
    }, []);

    const fetchData = useCallback(async (force = false) => {
        if (!userId) {
            setIsLoading(false);
            return;
        }

        if (force) {
            setIsRefreshing(true);
        } else {
            setIsLoading(true);
        }
        setError(null);
        setRecommendations([]);

        try {
            if (USE_MOCK) {
                await new Promise((resolve) => setTimeout(resolve, 800));
                setRecommendations(mockRecommendations.recommendations);
                return;
            }

            const recsData = await getRecommendations(userId, limit, force);
            setRecommendations(recsData.recommendations);
            if (!force) {
                setIsLoading(false);
            }

            void fetchExplanations(userId, recsData.recommendations, force);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load recommendations');
        } finally {
            setIsLoading(false);
            setIsRefreshing(false);
        }
    }, [userId, limit, fetchExplanations]);

    useEffect(() => {
        void fetchData(false);
    }, [fetchData]);

    return {
        recommendations,
        isLoading,
        isRefreshing,
        isLoadingExplanations,
        error,
        refetch: () => {
            void fetchData(false);
        },
        refresh: () => {
            void fetchData(true);
        },
    };
};
