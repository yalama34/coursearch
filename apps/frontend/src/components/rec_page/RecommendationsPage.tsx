import React from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useProfile } from '../../hooks/profilehook';
import './RecommendationsPage.css';
import { CourseCard } from '../course_card/CourseCard';
import { CourseCardSkeleton } from '../course_card_skeleton/course_card_skeleton.tsx';

const SKELETON_COUNT = 10;

interface RecommendationsPageProps {
    userId?: string | number;
}

export const RecommendationsPage: React.FC<RecommendationsPageProps> = ({ userId }) => {
    const { user, isLoading: authLoading } = useAuth();
    const effectiveUserId = userId ?? user?.user_id ?? '';
    const { recommendations, isLoading, error } = useProfile(effectiveUserId);

    if (authLoading || isLoading) {
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
                    <CourseCard key={course.id} course={course} index={index} />
                ))}
            </div>
        </div>
    );
};
