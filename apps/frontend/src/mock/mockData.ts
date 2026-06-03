import { ProfileData, RecommendationResponse } from '../types/types';
import LogoImage from '../components/assets/coursearch_logo.png';

export const mockProfile: ProfileData = {
    userId: '12345',
    name: 'Имя пользователя',
    interests: [
        { id: '1', label: 'Frontend' },
        { id: '2', label: 'JavaScript' },
        { id: '3', label: 'TypeScript' },
        { id: '4', label: 'Python' },
        { id: '5', label: 'Data Science' },
        { id: '6', label: 'Backend' },
    ],
    favoriteCourses: [
        {
            id: '1',
            title: 'Introduction to React',
            description: 'Learn React fundamentals',
            tags: [
                { id: '1', label: 'Frontend' },
                { id: '2', label: 'JavaScript' },
            ],
            author: 'Me',
            imageUrl: '',
        },
        {
            id: '2',
            title: 'TypeScript Mastery',
            description: 'Master TypeScript',
            tags: [
                { id: '3', label: 'TypeScript' },
                { id: '2', label: 'JavaScript' },
            ],
            author: 'Me',
            imageUrl: '',
        },
        {
            id: '3',
            title: 'Python for Data Science',
            description: 'Data analysis with Python',
            tags: [
                { id: '4', label: 'Python' },
                { id: '5', label: 'Data Science' },
            ],
            author: 'Me',
            imageUrl: '',
        },
        {
            id: '4',
            title: 'FastAPI Backend',
            description: 'Build fast APIs',
            tags: [
                { id: '4', label: 'Python' },
                { id: '6', label: 'Backend' },
            ],
            author: 'Me',
            imageUrl: '',
        },
    ],
};

export const mockRecommendations: RecommendationResponse = {
    recommendations: [
        {
            id: '1',
            title: 'Advanced React Patterns',
            description: 'Learn advanced React techniques',
            tags: [
                { id: '1', label: 'Frontend' },
                { id: '2', label: 'JavaScript' },
            ],
            author: 'Me',
            imageUrl: '',
            recommendationExplanation: {
                text: 'Этот курс подходит вам, потому что вы интересуетесь React и JavaScript.',
                confidence: 0.87,
            },
        },
        {
            id: '2',
            title: 'Node.js Microservices',
            description: 'Build scalable microservices',
            tags: [
                { id: '6', label: 'Backend' },
                { id: '9', label: 'Node.js' },
            ],
            author: 'Me',
            imageUrl: '',
        },
        {
            id: '3',
            title: 'Machine Learning Basics',
            description: 'Introduction to ML',
            tags: [
                { id: '4', label: 'Python' },
                { id: '5', label: 'Data Science' },
            ],
            author: 'Me',
            imageUrl: '',
        },
        {
            id: '4',
            title: 'Docker & Kubernetes',
            description: 'Container orchestration',
            tags: [
                { id: '10', label: 'DevOps' },
                { id: '11', label: 'Docker' },
            ],
            author: 'Me',
            imageUrl: '',
        },
        {
            id: '5',
            title: 'GraphQL API Design',
            description: 'Modern API development',
            tags: [
                { id: '6', label: 'Backend' },
                { id: '12', label: 'GraphQL' },
            ],
            author: 'Me',
            imageUrl: '',
        },
        {
            id: '6',
            title: 'CSS Advanced Techniques',
            description: 'Master modern CSS',
            tags: [
                { id: '1', label: 'Frontend' },
                { id: '13', label: 'CSS' },
            ],
            author: 'Me',
            imageUrl: '',
        },
        {
            id: '7',
            title: 'Database Design',
            description: 'SQL and NoSQL databases',
            tags: [
                { id: '6', label: 'Backend' },
                { id: '14', label: 'Database' },
            ],
            author: 'Me',
            imageUrl: '',
        },
        {
            id: '8',
            title: 'AWS Cloud Fundamentals',
            description: 'Cloud computing basics',
            tags: [
                { id: '10', label: 'DevOps' },
                { id: '15', label: 'AWS' },
            ],
            author: 'Me',
            imageUrl: '',
        },
        {
            id: '9',
            title: 'React Native Mobile Dev',
            description: 'Build mobile apps',
            tags: [
                { id: '1', label: 'Frontend' },
                { id: '16', label: 'Mobile' },
            ],
            author: 'Me',
            imageUrl: '',
        },
        {
            id: '10',
            title: 'System Design',
            description: 'Architecture patterns',
            tags: [
                { id: '6', label: 'Backend' },
                { id: '17', label: 'Architecture' },
            ],
            author: 'Me',
            imageUrl: '',
        },
    ],
};

export const mockCourseDetails = {
    id: '1',
    title: 'Coursearch',
    description: 'ээээ типа проект бро',
    author: 'Прудников Ярик(любит сокращения)',
    imageUrl: LogoImage,
    tags: [
        { id: '1', label: 'TypeScript' },
        { id: '2', label: 'rEACT' },
        { id: '3', label: 'Python' },
    ],
};