import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { updateInterests } from '../../services/profileapi';
import './interests_page.css';

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
    const { user, token, logout } = useAuth();

    const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set([])); 
    const [isSaving, setIsSaving] = useState(false);

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
        setIsSaving(true);
        try {
            const selectedTags = Array.from(selectedIds)
                .map(id => AVAILABLE_TAGS.find(t => t.id === id)?.label)
                .filter(Boolean) as string[];
            if (token) {
                await updateInterests(selectedTags, token);
            }
            if (location.state?.fromRegistration) {
                navigate('/', { replace: true });
            } else {
                navigate('/profile');
            }
        } catch (error) {
            console.error('Failed to save interests', error);
            alert('Не удалось сохранить интересы');
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <main className="interest-content">
            <div className="user-header">
                <h2 className="username">{user?.nickname || 'Имя пользователя'}</h2>
            </div>

            <h3 className="page-subtitle">Выберите свои навыки и интересы</h3>

            <div className="tags-container">
                {AVAILABLE_TAGS.map((tag) => {
                    const isSelected = selectedIds.has(tag.id);
                    return (
                        <button
                            key={tag.id}
                            className={`tag-pill ${isSelected ? 'selected' : 'unselected'}`}
                            onClick={() => toggleTag(tag.id)}
                        >
                            {isSelected && <span className="check-icon">✓</span>}
                            {tag.label}
                        </button>
                    );
                })}
            </div>

            <button
                className="btn-finish"
                onClick={handleFinish}
                disabled={isSaving}
            >
                {isSaving ? 'Сохранение...' : 'Закончить редактирование'}
            </button>
        </main>

    );
};