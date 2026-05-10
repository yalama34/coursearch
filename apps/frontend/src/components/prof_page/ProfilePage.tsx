import React from 'react';
import {Link, useNavigate} from 'react-router-dom';
import { useProfile } from '../../hooks/profilehook';
import { Course } from '../../types/types';
import './ProfilePage.css';

const MiniCourseCard: React.FC<{ course: Course }> = ({ course }) => (
    <Link to={`/course/${course.id}`} className="course-card-link">
        <div className="course-card">
            <div className="course-image-placeholder">
                <div className="image-icon"></div>
            </div>

            <div className="course-content">
                <h3 className="course-title">{course.title}</h3>
                <p className="course-description">{course.description}</p>
                <div className="course-tags">
                    {course.tags?.map((tag) => (
                        <span key={tag.id} className="tag">{tag.label}</span>
                    ))}
                </div>
            </div>
        </div>
    </Link>
);

interface ProfilePageProps {
    userId?: string;
}

export const ProfilePage: React.FC<ProfilePageProps> = ({ userId }) => {
    const { profile, isLoading, error } = useProfile(userId || '');
    const navigate = useNavigate();

    if (isLoading) return <div className="profile-page"><div className="loading-state">Загрузка...</div></div>;
    if (error) return <div className="profile-page"><div className="error-state">{error}</div></div>;
    if (!profile) return <div className="profile-page"><div className="error-state">Profile not found</div></div>;

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
                </div>
            </div>

            <div className="interests-section">
                <h3 className="section-title">My Interests</h3>
                <div className="interests-container">
                    <div className="interests-tags">
                        {profile.interests.length === 0 ? (
                            <span className="no-interests-text">Нет интересов</span>
                        ) : (
                            profile.interests.map((tag) => (
                                <span key={tag.id} className="interest-tag">{tag.label}</span>
                            ))
                        )}
                    </div>
                    <button className="add-interest-btn" onClick={() => navigate('/setup-interests')}>+</button>
                </div>
            </div>

            <div className="favorites-section">
                <h3 className="section-title">Favorite Courses</h3>
                <div className="favorites-grid">
                    {profile.favoriteCourses.length === 0 ? (
                        <div className="no-interests-text">Нет избранных курсов</div>
                    ) : (
                        profile.favoriteCourses.map((course) => (
                            <MiniCourseCard key={course.id} course={course} />
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};