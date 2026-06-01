import React from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useRecommendations } from '../../hooks/useRecommendations';
import './RecommendationsPage.css';
import { CourseCard } from '../course_card/CourseCard';
import { CourseCardSkeleton } from '../course_card_skeleton/course_card_skeleton.tsx';

const SKELETON_COUNT = 10;

interface RecommendationsPageProps {
    userId?: string | number;
}

export const RecommendationsPage: React.FC<RecommendationsPageProps> = ({ userId }) => {
    const { user } = useAuth();
    const effectiveUserId = userId ?? user?.user_id ?? '';
    const { recommendations, isLoading, isLoadingExplanations, error } = useRecommendations(effectiveUserId);

    if (isLoading) {
        return (
            <div className="recommendations-page">
                <h1 className="page-title">Рекомендованные курсы</h1>
                <div className="courses-grid">
                    {Array.from({ length: SKELETON_COUNT }).map((_, i) => (
                        <CourseCardSkeleton key={`skeleton-${i}`} />
                    ))}
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="recommendations-page">
                <div className="error-state">{error}</div>
            </div>
        );
    }

    return (
        <div className="recommendations-page">
            <h1 className="page-title">Рекомендованные курсы</h1>
            <div className="courses-grid">
                {recommendations.map((course, index) => (
                    <CourseCard
                        key={course.id}
                        course={course}
                        index={index}
                        isExplanationLoading={isLoadingExplanations}
                    />
                ))}
            </div>
        </div>
    );
};
