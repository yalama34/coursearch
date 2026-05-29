import React from 'react';
import './course_card_skeleton.css';

export const CourseCardSkeleton: React.FC = () => {
    return (
        <div className="course-card-skeleton">
            <div className="skeleton-image skeleton-block"></div>

            <div className="skeleton-content">
                <div className="skeleton-title skeleton-block"></div>

                <div className="skeleton-description skeleton-block"></div>
                <div className="skeleton-description skeleton-block short"></div>

                <div className="skeleton-tags">
                    <div className="skeleton-tag skeleton-block"></div>
                    <div className="skeleton-tag skeleton-block"></div>
                </div>
            </div>
        </div>
    );
};