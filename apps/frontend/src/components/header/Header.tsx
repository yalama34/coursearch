import React from 'react';
import './Header.css';
import LogoImage from '../assets/coursearch_logo.png'

interface HeaderProps {
    activeTab: 'recommendations' | 'profile';
    onTabChange: (tab: 'recommendations' | 'profile') => void;
    onSearch?: (query: string) => void;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, onTabChange, onSearch }) => {
    const [searchQuery, setSearchQuery] = React.useState('');

    const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        setSearchQuery(value);
        onSearch?.(value);
    };

    return (
        <header className="header">
            <div className="header-left">
                {/* UPDATED: Logo Image Section */}
                <div className="logo" onClick={() => onTabChange('recommendations')}>
                    <img
                        src={LogoImage}
                        alt="CourseArch Logo"
                        className="logo-img"
                    />
                </div>
        <nav className="nav-buttons">
    <button
        className={`nav-button ${activeTab === 'recommendations' ? 'active' : ''}`}
    onClick={() => onTabChange('recommendations')}
>
    Рекомендации
    </button>
    <button
    className="nav-button"
    disabled={true}
    onClick={() => {}}
>
    Курсы
    </button>
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
    <div className="user-avatar" onClick={() => onTabChange('profile')}>
    {/* Avatar placeholder */}
    </div>
    </div>
    </header>
);
};