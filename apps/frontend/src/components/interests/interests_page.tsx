import React, {useEffect, useState} from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import {updateDescription, updateInterests} from '../../services/profileapi';
import './interests_page.css';
import {useProfile} from "../../hooks/profilehook.ts";

const AVAILABLE_TAGS = [
    { id: '1', label: 'Frontend' },
    { id: '2', label: 'Backend' },
    { id: '3', label: 'JavaScript' },
    { id: '4', label: 'Python' },
    { id: '5', label: 'TypeScript' },
    { id: '6', label: 'React' },
    { id: '7', label: 'Data Science' },
    { id: '8', label: 'DevOps' },
    { id: '9', label: 'UI/UX' },
];

export const InterestSelectionPage: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { profile, isLoading } = useProfile('me');
    const { user, token } = useAuth();

    const [description, setDescription] = useState('');
    const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set([]));
    const [isSaving, setIsSaving] = useState(false);
    const [saveError, setSaveError] = useState<string | null>(null);

    useEffect(() => {
        if (profile?.description) {
            setDescription(profile.description);
        }
        if (profile?.interests) {
            setSelectedIds(new Set(profile.interests.map(i => i.id.toString())));
        }
    }, [profile]);

    const toggleTag = (id: string) => {
        const newSet = new Set(selectedIds);
        if (newSet.has(id)) {
            newSet.delete(id);
        } else {
            newSet.add(id);
        }
        setSelectedIds(newSet);
    };

    const handleFinish = async () => {
        if (!token) {
            setSaveError('Ошибка авторизации. Пожалуйста, войдите снова.');
            return;
        }

        setIsSaving(true);
        setSaveError(null);
        try {
            const trimmedDesc = description.trim();
            if (trimmedDesc !== profile?.description?.trim()) {
                await updateDescription(trimmedDesc, token);
            }

            const selectedTags = Array.from(selectedIds)
                .map(id => AVAILABLE_TAGS.find(t => t.id === id)?.label)
                .filter(Boolean) as string[];

            await updateInterests(selectedTags, token);

            if (location.state?.fromRegistration) {
                navigate('/', { replace: true });
            } else {
                navigate('/profile');
            }
        } catch (err) {
            console.error('Failed to save profile data', err);
            setSaveError('Не удалось сохранить изменения. Попробуйте снова.');
        } finally {
            setIsSaving(false);
        }
    };

    if (isLoading) {
        return <div className="loading-state">Загрузка данных профиля...</div>;
    }

    return (
        <main className="interest-content">
            <div className="user-header">
                <h2 className="username">{user?.nickname || profile?.name || 'Имя пользователя'}</h2>
            </div>

            <h3 className="page-subtitle">Настройка профиля</h3>

            <div className="description-section">
                <label htmlFor="user-description" className="section-label">О себе</label>
                <textarea
                    id="user-description"
                    className="description-input"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Расскажите немного о себе, вашем опыте и целях..."
                    rows={3}
                    maxLength={500}
                />
                <span className="char-count">{description.length}/500</span>
            </div>

            <h4 className="subsection-title">Выберите свои навыки и интересы</h4>

            <div className="tags-container">
                {AVAILABLE_TAGS.map((tag) => {
                    const isSelected = selectedIds.has(tag.id);
                    return (
                        <button
                            key={tag.id}
                            type="button"
                            className={`tag-pill ${isSelected ? 'selected' : 'unselected'}`}
                            onClick={() => toggleTag(tag.id)}
                        >
                            {isSelected && <span className="check-icon">✓</span>}
                            {tag.label}
                        </button>
                    );
                })}
            </div>

            {saveError && <p className="error-message">{saveError}</p>}

            <button
                type="button"
                className="btn-finish"
                onClick={handleFinish}
                disabled={isSaving}
            >
                {isSaving ? 'Сохранение...' : 'Закончить редактирование'}
            </button>
        </main>
    );
};