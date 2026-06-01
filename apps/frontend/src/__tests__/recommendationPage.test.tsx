import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { RecommendationsPage } from '../components/rec_page/RecommendationsPage';
import { useRecommendations } from '../hooks/useRecommendations';
import { useAuth } from '../hooks/useAuth';

vi.mock('../hooks/useRecommendations');
vi.mock('../hooks/useAuth');

const mockedUseRecommendations = vi.mocked(useRecommendations);
const mockedUseAuth = vi.mocked(useAuth);

describe('RecommendationsPage', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        mockedUseAuth.mockReturnValue({
            user: { user_id: 1, nickname: 'test' },
            token: 'token',
            isAuthenticated: true,
            isLoading: false,
            error: null,
            login: vi.fn(),
            register: vi.fn(),
            logout: vi.fn(),
        });
    });

    it('shows skeleton grid while loading', () => {
        mockedUseRecommendations.mockReturnValue({
            recommendations: [],
            isLoading: true,
            isLoadingExplanations: false,
            error: null,
            refetch: vi.fn(),
        });

        const { container } = render(
            <BrowserRouter>
                <RecommendationsPage />
            </BrowserRouter>,
        );

        expect(screen.getByText('Рекомендованные курсы')).toBeInTheDocument();
        expect(container.querySelectorAll('.course-card-skeleton, [class*="skeleton"]').length).toBeGreaterThan(0);
    });

    it('shows error state', () => {
        mockedUseRecommendations.mockReturnValue({
            recommendations: [],
            isLoading: false,
            isLoadingExplanations: false,
            error: 'Failed to load',
            refetch: vi.fn(),
        });

        render(
            <BrowserRouter>
                <RecommendationsPage />
            </BrowserRouter>,
        );

        expect(screen.getByText('Failed to load')).toBeInTheDocument();
    });

    it('renders recommendations grid', () => {
        mockedUseRecommendations.mockReturnValue({
            recommendations: [
                {
                    id: '1',
                    title: 'Course 1',
                    description: 'Desc 1',
                    tags: [{ id: '1', label: 'Tag1' }],
                    author: '',
                    imageUrl: '',
                },
                {
                    id: '2',
                    title: 'Course 2',
                    description: 'Desc 2',
                    tags: [],
                    author: '',
                    imageUrl: '',
                },
            ],
            isLoading: false,
            isLoadingExplanations: false,
            error: null,
            refetch: vi.fn(),
        });

        render(
            <BrowserRouter>
                <RecommendationsPage />
            </BrowserRouter>,
        );

        expect(screen.getByText('Course 1')).toBeInTheDocument();
        expect(screen.getByText('Course 2')).toBeInTheDocument();
        expect(screen.getByText('Tag1')).toBeInTheDocument();
    });

    it('has page title', () => {
        mockedUseRecommendations.mockReturnValue({
            recommendations: [],
            isLoading: false,
            isLoadingExplanations: false,
            error: null,
            refetch: vi.fn(),
        });

        render(
            <BrowserRouter>
                <RecommendationsPage />
            </BrowserRouter>,
        );

        expect(screen.getByText('Рекомендованные курсы')).toBeInTheDocument();
    });
});
