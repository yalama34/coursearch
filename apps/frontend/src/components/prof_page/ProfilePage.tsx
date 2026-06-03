import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useProfile } from '../../hooks/profilehook';
import './ProfilePage.css';
import { CourseCard } from '../course_card/CourseCard.tsx';

interface ProfilePageProps {
    userId?: string | number;
}

export const ProfilePage: React.FC<ProfilePageProps> = ({ userId }) => {
    const { user, isLoading: authLoading } = useAuth();
    const effectiveUserId = userId ?? user?.user_id ?? '';
    const { profile, isLoading, error } = useProfile(effectiveUserId);
    const navigate = useNavigate();

    if (authLoading || isLoading) {
        return (
            <div className="profile-page">
                <div className="loading-state">Загрузка...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="profile-page">
                <div className="error-state">Ошибка: {error}</div>
            </div>
        );
    }

    if (!profile) {
        return (
            <div className="profile-page">
                <div className="error-state">Профиль не найден</div>
            </div>
        );
    }

    return (
        <div className="profile-page">
            <div className="profile-header">
                <div className="profile-avatar-large">
                    <svg className="avatar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="12" cy="8" r="4" />
                        <path d="M6 20c0-3.3 2.7-6 6-6s6 2.7 6 6" />
                    </svg>
                </div>

                <div className="profile-info">
                    <div className="profile-name-row">
                        <h2 className="profile-name">{profile.name}</h2>
                    </div>
                    <p className="profile-label">User ID: {profile.userId}</p>

                    {profile.description && (
                        <p className="profile-description-display">
                            {profile.description}
                        </p>
                    )}
                    {!profile.description && (
                        <p className="profile-description-display empty">
                            Описание не добавлено
                        </p>
                    )}
                </div>
            </div>

            <div className="interests-section">
                <h3 className="section-title">My Interests</h3>
                <div className="interests-container">
                    <div className="interests-tags">
                        {profile.interests.map((tag, index) => (
                            <span
                                key={tag.id}
                                className="interest-tag"
                                style={{ animationDelay: `${index * 0.03}s` }}
                            >
                                {tag.label}
                            </span>
                        ))}
                    </div>
                    <button
                        className="add-interest-btn"
                        role="button"
                        onClick={() => navigate('/setup-interests')}
                    >
                        +
                    </button>
                </div>
            </div>

            <div className="favorites-section">
                <h3 className="section-title">Favorite Courses</h3>
                <div className="favorites-grid">
                    {profile.favoriteCourses.map((course, index) => (
                        <CourseCard
                            key={course.id}
                            course={course}
                            index={index}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
};
