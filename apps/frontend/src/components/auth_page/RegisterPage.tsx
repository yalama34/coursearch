import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import './AuthPages.css';

export const RegisterPage: React.FC = () => {
    const navigate = useNavigate();
    const { register, error, isLoading } = useAuth();
    const [nickname, setNickname] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (password !== confirmPassword) {
            alert('Пароли не совпадают!');
            return;
        }
        const success = await register(nickname, password);
        if (success) navigate('/');
    };

    return (
        <div className="auth-page">
            <div className="auth-form-container">
                <h1 className="auth-title">Регистрация</h1>

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

                    <input
                        type="password"
                        className="auth-input"
                        placeholder="Повторите пароль"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                    />

                    {error && <p className="error-text">{error}</p>}

                    <button type="submit" className="btn-submit" disabled={isLoading}>
                        {isLoading ? 'Регистрация...' : 'Войти'}
                    </button>
                </form>
            </div>
        </div>
    );
};