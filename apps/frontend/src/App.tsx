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

// const isAuthenticated = localStorage.getItem('authToken') !== null;
const isAuthenticated = 1;

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
                        isAuthenticated ? (
                            <Layout>
                                <RecommendationsPage />
                            </Layout>
                        ) : (
                            <Navigate to="/welcome" />
                        )
                    }
                />

                <Route
                    path="/profile"
                    element={
                        isAuthenticated ? (
                            <Layout>
                                <ProfilePage />
                            </Layout>
                        ) : (
                            <Navigate to="/welcome" />
                        )
                    }
                />

                <Route
                    path="/course/:id"
                    element={
                        isAuthenticated ? (
                            <Layout>
                                <CoursePage />
                            </Layout>
                        ) : (
                            <Navigate to="/welcome" />
                        )
                    }
                />

                <Route
                    path="/setup-interests"
                    element={
                        isAuthenticated ? (
                            <Layout>
                                <InterestSelectionPage />
                            </Layout>
                        ) : (
                            <Navigate to="/welcome" />
                        )
                    }
                />
            </Routes>
        </BrowserRouter>
    );
};

export default App;