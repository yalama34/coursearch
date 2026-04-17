import React, { useState } from 'react';
import { Header } from './components/header/Header';
import { RecommendationsPage } from './components/rec_page/RecommendationsPage';
import { ProfilePage } from './components/prof_page/ProfilePage';
import './App.css';

const App: React.FC = () => {
    const [activeTab, setActiveTab] = useState<'recommendations' | 'profile'>('recommendations');
    const [searchQuery, setSearchQuery] = useState('');

    const handleSearch = (query: string) => {
        setSearchQuery(query);
        // Implement search logic here
    };

    return (
        <div className="app-container">
            <Header
                activeTab={activeTab}
                onTabChange={setActiveTab}
                onSearch={handleSearch}
            />

            {activeTab === 'recommendations' && (
                <RecommendationsPage />
            )}

            {activeTab === 'profile' && (
                <ProfilePage />
            )}
        </div>
    );
};

export default App;