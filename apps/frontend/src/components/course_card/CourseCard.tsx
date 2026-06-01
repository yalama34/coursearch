import React, { useRef } from 'react';
import { Link } from 'react-router-dom';
import { Course } from '../../types/types';
import './CourseCard.css';

interface CourseCardProps {
    course: Course;
    index?: number;
}

export const CourseCard: React.FC<CourseCardProps> = ({ course, index = 0 }) => {
    const cardRef = useRef<HTMLDivElement>(null);

    const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
        const card = cardRef.current;
        if (!card) return;

        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        card.style.setProperty('--mouse-x', `${x}px`);
        card.style.setProperty('--mouse-y', `${y}px`);
    };

    return (
        <Link to={`/course/${course.id}`} className="course-card-link">
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

                <div className="course-content">
                    <h3 className="course-title">{course.title}</h3>
                    <p className="course-description">{course.description}</p>
                    <div className="course-tags">
                        {course.tags.map((tag) => (
                            <span key={tag.id} className="tag-pill" title={tag.label}>
                                {tag.label}
                            </span>
                        ))}
                    </div>
                </div>
            </div>
        </Link>
    );
};