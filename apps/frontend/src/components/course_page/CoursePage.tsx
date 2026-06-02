import React, { useEffect } from 'react';
import { useParams, useLocation } from 'react-router-dom';
import { useCourse } from '../../hooks/coursehook';
import { useAuth } from '../../hooks/useAuth';
import { useProfile } from '../../hooks/profilehook';
import './CoursePage.css';
import { useCourseTracking } from '../../hooks/courseTrackHook.ts';
import { actionsApi } from '../../services/actionsApi';

export const CoursePage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const location = useLocation();
    const { course, isLoading, error } = useCourse(id);
    const { user } = useAuth();
    const { profile } = useProfile(user?.user_id ?? '');
    const initialLiked = profile?.favoriteCourses.some(
        (c) => String(c.id) === id,
    ) ?? false;
    const { isLiked, isLiking, handleLike } = useCourseTracking(id, initialLiked);

    useEffect(() => {
        if (!id) return;

        const fromCard = (location.state as { fromCard?: boolean } | null)?.fromCard;
        if (fromCard) return;

        actionsApi
            .sendAction({ course_id: id, action_type: 'view' })
            .catch((err) => console.error('Failed to send view action', err));
    }, [id, location.state]);

    const handleExternalLinkClick = () => {
        if (!id) return;

        actionsApi
            .sendAction({ course_id: id, action_type: 'click_link' })
            .catch((err) => console.error('Failed to send click_link action', err));
    };

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
                            disabled={isLiked || isLiking}
                            aria-label="Like course"
                        >
                            {isLiking ? '...' : isLiked ? '❤️ Liked' : '🤍 Like'}
                        </button>
                    </div>
                </div>

                <div className="course-author">{course.author || 'Нет Автора'}</div>
            </div>

            <p className="course-description-course-page">{course.description}</p>

            {course.link && (
                <a
                    href={course.link}
                    className="course-external-link"
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={handleExternalLinkClick}
                >
                    Перейти на курс
                </a>
            )}

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
