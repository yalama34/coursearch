import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import './AuthPages.css';

export const LoginPage: React.FC = () => {
    const navigate = useNavigate();
    const { login, error, isLoading } = useAuth();
    const [nickname, setNickname] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const success = await login(nickname, password);
        if (success) navigate('/');
    };

    return (
        <div className="auth-page">
            <div className="auth-form-container">
                <h1 className="auth-title">Вход</h1>

                <form className="auth-form" onSubmit={handleSubmit}>
                    <input
                        type="text"
                        className="auth-input"
                        placeholder="Nickname"
                        value={nickname}
                        onChange={(e) => setNickname(e.target.value)}
                        required
                    />

                    <input
                        type="password"
                        className="auth-input"
                        placeholder="Пароль"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />

                    {error && <p className="error-text">{error}</p>}

                    <button type="submit" className="btn-submit" disabled={isLoading}>
                        {isLoading ? 'Вход...' : 'Войти'}
                    </button>
                </form>
            </div>
        </div>
    );
};