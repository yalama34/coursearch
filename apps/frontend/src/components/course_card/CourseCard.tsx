import React, { useRef } from 'react';
import { Link } from 'react-router-dom';
import { Course } from '../../types/types';
import { actionsApi } from '../../services/actionsApi';
import './CourseCard.css';

interface CourseCardProps {
    course: Course;
    index?: number;
    isExplanationLoading?: boolean;
}

export const CourseCard: React.FC<CourseCardProps> = ({
    course,
    index = 0,
    isExplanationLoading = false,
}) => {
    const cardRef = useRef<HTMLDivElement>(null);
    const explanation = course.recommendationExplanation;
    const showExplanation =
        isExplanationLoading ||
        Boolean(explanation?.text) ||
        explanation?.confidence != null;

    const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
        const card = cardRef.current;
        if (!card) return;

        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        card.style.setProperty('--mouse-x', `${x}px`);
        card.style.setProperty('--mouse-y', `${y}px`);
    };

    const title = course.title?.trim() || `Курс #${course.id}`;

    const handleCardClick = () => {
        actionsApi
            .sendAction({ course_id: course.id, action_type: 'view' })
            .catch((error) => console.error('Failed to send view action', error));
    };

    return (
        <Link
            to={`/course/${course.id}`}
            state={{ fromCard: true }}
            className="course-card-link"
            onClick={handleCardClick}
        >
            <div
                ref={cardRef}
                className="course-card"
                style={{ animationDelay: `${index * 0.05}s` }}
                onMouseMove={handleMouseMove}
                onMouseLeave={(e) => {
                    e.currentTarget.style.setProperty('--mouse-x', '0px');
                    e.currentTarget.style.setProperty('--mouse-y', '0px');
                }}
            >
                <div className="card-glow"></div>

                <div className="course-image-placeholder">
                    <div className="image-icon"></div>
                </div>

                <h3 className="course-title">{title}</h3>
                <p className="course-description" title={course.description || undefined}>
                    {course.description || '\u00A0'}
                </p>

                <div
                    className={`course-explanation${showExplanation ? '' : ' course-explanation--hidden'}`}
                    aria-hidden={!showExplanation}
                >
                    {explanation?.confidence != null && (
                        <span className="explanation-confidence">
                            {Math.round(explanation.confidence * 100)}%
                        </span>
                    )}
                    {isExplanationLoading && !explanation?.text ? (
                        <p className="explanation-loading">Генерируем объяснение...</p>
                    ) : (
                        explanation?.text && (
                            <p className="explanation-text" title={explanation.text}>
                                {explanation.text}
                            </p>
                        )
                    )}
                </div>

                <div className="course-tags">
                    {course.tags.slice(0, 3).map((tag) => (
                        <span key={tag.id} className="tag-pill" title={tag.label}>
                            {tag.label}
                        </span>
                    ))}
                    {course.tags.length > 3 && (
                        <span
                            className="tag-pill tag-pill-more"
                            title={course.tags.slice(3).map((tag) => tag.label).join(', ')}
                        >
                            +{course.tags.length - 3}
                        </span>
                    )}
                </div>
            </div>
        </Link>
    );
};
