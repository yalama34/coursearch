import React from 'react';
import {useNavigate} from 'react-router-dom';
import './Header.css';
import LogoImage from '../assets/coursearch_logo.png';
import { motion } from "framer-motion";

interface HeaderProps {
    activeTab: 'recommendations' | 'profile';
    onTabChange: (tab: 'recommendations' | 'profile') => void;
    onSearch?: (query: string) => void;
}

interface NavItem {
    id: 'recommendations' | 'courses' | 'profile';
    label: string;
    disabled?: boolean;
}

const NAV_ITEMS: NavItem[] = [
    { id: 'recommendations', label: 'Рекомендации' },
    { id: 'courses', label: 'Курсы', disabled: true },
];

export const Header: React.FC<HeaderProps> = ({ activeTab, onTabChange, onSearch }) => {
    const navigate = useNavigate();
    const [searchQuery, setSearchQuery] = React.useState('');

    const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        setSearchQuery(value);
        onSearch?.(value);
    };

    return (
        <header className="header">
            <div className="header-left">
                <div className="logo" onClick={() => navigate('/')}>
                    <img
                        src={LogoImage}
                        alt={LogoImage}
                        className="logo-img-header"
                        onError={(e) => {
                            (e.target as HTMLImageElement).style.display = 'none';
                            e.currentTarget.parentElement!.innerHTML = '<span>Course</span><span class="logo-accent">arch</span>';
                        }}
                    />
                </div>

                <nav className="nav-container">
                    {NAV_ITEMS.map((item) => (
                        <button
                            key={item.id}
                            className={`nav-button ${activeTab === item.id ? 'active' : ''} ${item.disabled ? 'disabled' : ''}`}
                            onClick={() => !item.disabled && onTabChange(item.id as 'recommendations' | 'profile')}
                            disabled={item.disabled}
                        >
                            {item.label}
                            {activeTab === item.id && (
                                <motion.div
                                    layoutId="activeTabIndicator"
                                    className="active-indicator"
                                    transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                                />
                            )}
                        </button>
                    ))}
                </nav>
            </div>

            <div className="header-right">
                <div className="search-container">
                    <input
                        type="text"
                        className="search-input"
                        placeholder="Поиск Курса"
                        value={searchQuery}
                        onChange={handleSearchChange}
                    />
                    <span className="search-icon"></span>
                </div>
                <div
                    className="user-avatar"
                    onClick={() => onTabChange('profile')}
                    role="button"
                    tabIndex={0}
                />
            </div>
        </header>
    );
};