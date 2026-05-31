import React from 'react';
import { useProfile } from '../../hooks/profilehook';
import './RecommendationsPage.css';
import { CourseCard } from '../course_card/CourseCard';
import { CourseCardSkeleton } from '../course_card_skeleton/course_card_skeleton.tsx';


const SKELETON_COUNT = 10;

interface RecommendationsPageProps {
    userId?: string;
}

export const RecommendationsPage: React.FC<RecommendationsPageProps> = ({ userId }) => {
    const userIdMock = '12345';
    const a = userId;
    const { recommendations, isLoading, error } = useProfile(userId || '');

    if (isLoading) return <div className="recommendations-page"><div className="loading-state">Загрузка...</div></div>;
    if (error) return <div className="recommendations-page"><div className="error-state">{error}</div></div>;

    return (
        <div className="recommendations-page">
            <h1 className="page-title">Рекомендованные курсы</h1>
            <div className="courses-grid">
                {isLoading
                    ? Array.from({ length: SKELETON_COUNT }).map((_, i) => (
                        <CourseCardSkeleton key={`skeleton-${i}`} />
                    ))
                    : recommendations.map((course, index) => (
                        <CourseCard key={course.id} course={course} index={index} />
                    ))
                }
            </div>
        </div>
    );
};