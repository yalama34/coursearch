import React from 'react';
import { useProfile } from '../../hooks/profilehook';
import { Course } from '../../types/types';
import './RecommendationsPage.css';

const CourseCard: React.FC<{ course: Course }> = ({ course }) => (
    <div className="course-card">
        <div className="course-image-placeholder">
            <div className="image-icon"></div>
        </div>
        <div className="course-content">
            <h3 className="course-title">{course.title}</h3>
            <p className="course-description">{course.description}</p>
            <div className="course-tags">
                {course.tags.map((tag) => (
                    <span key={tag.id} className="tag">{tag.label}</span>
                ))}
            </div>
        </div>
    </div>
);

interface RecommendationsPageProps {
    userId?: string;
}

export const RecommendationsPage: React.FC<RecommendationsPageProps> = ({ userId = '12345' }) => {
    const { recommendations, isLoading, error } = useProfile(userId);

    if (isLoading) return <div className="recommendations-page"><div className="loading-state">Загрузка...</div></div>;
    if (error) return <div className="recommendations-page"><div className="error-state">{error}</div></div>;

    return (
        <div className="recommendations-page">
            <h1 className="page-title">Рекомендованные курсы</h1>
            <div className="courses-grid">
                {recommendations.length === 0 ? (
                    <span className="no-interests-text">Рекомендации отсутствуют</span>
                ) : (
                    recommendations.map((course) => (
                        <CourseCard key={course.id} course={course} />
                    ))
                )}
            </div>
        </div>
    );
};