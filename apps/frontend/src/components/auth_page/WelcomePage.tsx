import React from 'react';
import { useNavigate } from 'react-router-dom';
import './WelcomePage.css';
import LogoImage from '../assets/coursearch_logo.png'

export const WelcomePage: React.FC = () => {
    const navigate = useNavigate();

    return (
        <div className="auth-page">
            <div className="auth-content">
                <h1 className="auth-title">Добро Пожаловать на платформу</h1>

                <div className="logo-container">
                    <div className="logo">
                        <img
                            src={LogoImage}
                            alt="CourseArch Logo"
                            className="logo-img"
                        />
                    </div>
                </div>

                <div className="auth-buttons">
                    <button className="btn-auth" onClick={() => navigate('/login')}>
                        Вход
                    </button>
                    <button className="btn-auth" onClick={() => navigate('/register')}>
                        Регистрация
                    </button>
                </div>
            </div>
        </div>
    );
};