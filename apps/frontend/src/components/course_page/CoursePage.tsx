import React from 'react';
import { useParams } from 'react-router-dom';
import { useCourse } from '../../hooks/coursehook';
import './CoursePage.css';

export const CoursePage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const { course, isLoading, error } = useCourse(id);

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
                    <h1 className="course-title-course-page">{course.title}</h1>
                </div>

                <div className="course-author">{course.author || 'Нет Автора'}</div>
            </div>

            <p className="course-description-course-page">{course.description}</p>

            <div className="tags-section">
                <div className="tags-label">Тэги Курса</div>
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
