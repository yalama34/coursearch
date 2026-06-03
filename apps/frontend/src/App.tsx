import React from 'react';
import {BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation} from 'react-router-dom';
import { Header } from './components/header/Header';
import { RecommendationsPage } from './components/rec_page/RecommendationsPage';
import { ProfilePage } from './components//prof_page/ProfilePage';
import { CoursePage } from './components/course_page/CoursePage';
import { WelcomePage } from './components/auth_page/WelcomePage';
import { LoginPage } from './components/auth_page/LoginPage';
import { RegisterPage } from './components/auth_page/RegisterPage';
import { InterestSelectionPage } from './components/interests/interests_page';

import './App.css';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const isAuthenticated = localStorage.getItem('authToken') !== null;

    if (!isAuthenticated) {
        return <Navigate to="/welcome" replace />;
    }

    return <Layout>{children}</Layout>;
};

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const location = useLocation();
    const navigate = useNavigate();

    const getActiveTab = () => {
        if (location.pathname.startsWith('/profile')) return 'profile';
        return 'recommendations';
    };

    const handleTabChange = (tab: string) => {
        if (tab === 'profile') navigate('/profile');
        else navigate('/');
    };

    return (
        <div className="app-container">
            <Header
                activeTab={getActiveTab()}
                onTabChange={handleTabChange}
            />
            {children}
        </div>
    );
};

const App: React.FC = () => {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/welcome" element={<WelcomePage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />

                <Route
                    path="/"
                    element={
                        <ProtectedRoute>
                            <RecommendationsPage />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/profile"
                    element={
                        <ProtectedRoute>
                            <ProfilePage />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/course/:id"
                    element={
                        <ProtectedRoute>
                            <CoursePage />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/setup-interests"
                    element={
                        <ProtectedRoute>
                            <InterestSelectionPage />
                        </ProtectedRoute>
                    }
                />
            </Routes>
        </BrowserRouter>
    );
};

export default App;