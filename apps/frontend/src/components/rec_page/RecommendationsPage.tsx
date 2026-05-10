import React from 'react';
import { Link } from 'react-router-dom';
import { useProfile } from '../../hooks/profilehook';
import { Course } from '../../types/types';
import './RecommendationsPage.css';

function formatConfidence(value: number): string {
    if (value >= 0 && value <= 1) {
        return `${Math.round(value * 100)}%`;
    }
    return value.toFixed(2);
}

const CourseCard: React.FC<{ course: Course }> = ({ course }) => {
    const reason = course.recommendationExplanation?.text?.trim();
    const conf = course.recommendationExplanation?.confidence;

    return (
        <Link to={`/course/${course.id}`} className="course-card-link">
            <div className="course-card">
                <div className="course-image-placeholder">
                    <div className="image-icon"></div>
                </div>

                <div className="course-content">
                    <h3 className="course-title">{course.title}</h3>
                    {course.description ? (
                        <p className="course-description">{course.description}</p>
                    ) : null}
                    {reason ? (
                        <p className="course-recommendation-reason">
                            <span className="course-recommendation-label">Почему рекомендовано: </span>
                            <span className="course-recommendation-text">{reason}</span>
                            {typeof conf === 'number' && !Number.isNaN(conf) ? (
                                <span className="course-confidence"> ({formatConfidence(conf)})</span>
                            ) : null}
                        </p>
                    ) : null}
                    <div className="course-tags">
                        {course.tags.map((tag) => (
                            <span key={tag.id} className="tag">{tag.label}</span>
                        ))}
                    </div>
                </div>
            </div>
        </Link>
    );
};

interface RecommendationsPageProps {
    userId?: string;
}

export const RecommendationsPage: React.FC<RecommendationsPageProps> = ({ userId }) => {
    const { recommendations, isLoading, error } = useProfile(userId || '');

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