import React from 'react';
import { useParams } from 'react-router-dom';
import { useCourse } from '../../hooks/coursehook';
import './CoursePage.css';
import {useCourseTracking} from "../../hooks/courseTrackHook.ts";

export const CoursePage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const { course, isLoading, error } = useCourse(id);
    const { isLiked, handleLike } = useCourseTracking(id);

    if (isLoading) return <div className="course-page">Loading...</div>;
    if (error) return <div className="course-page" style={{color: 'red'}}>{error}</div>;
    if (!course) return <div className="course-page">Course not found</div>;

    return (
        <div className="course-page">
            <div className="course-top-section">
                <div className="course-left-content">
                    <div className="course-image-placeholder-course-page">
                        {course.imageUrl ? (
                            <img src={course.imageUrl} alt={course.title} className="course-image-course-page" />
                        ) : (
                            <div className="image-icon-large"></div>
                        )}
                    </div>
                    <div className="course-info-block">
                        <h1 className="course-title">{course.title}</h1>
                        <p className="course-description">{course.description}</p>

                        <button
                            className={`like-btn ${isLiked ? 'liked' : ''}`}
                            onClick={handleLike}
                            aria-label="Like course"
                        >
                            {isLiked ? '❤️ Liked' : '🤍 Like'}
                        </button>
                    </div>
                </div>

                <div className="course-author">{course.author || 'Нет Автора'}</div>
            </div>

            <p className="course-description-course-page">{course.description}</p>

            <div className="tags-section">
                <div className="tags-label">Теги Курса</div>
                <div className="tags-container">
                    <div className="tags-list">
                        {course.tags.map((tag) => (
                            <span key={tag.id} className="course-tag-course-page">{tag.label}</span>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};
