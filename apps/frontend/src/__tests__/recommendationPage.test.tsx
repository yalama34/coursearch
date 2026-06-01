import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { RecommendationsPage } from '../components/rec_page/RecommendationsPage';
import { useProfile } from '../hooks/profilehook';
import { useAuth } from '../hooks/useAuth';

vi.mock('../hooks/profilehook');
vi.mock('../hooks/useAuth');

const mockedUseProfile = vi.mocked(useProfile);
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
        mockedUseProfile.mockReturnValue({
            recommendations: [],
            isLoading: true,
            error: null,
            refetch: vi.fn(),
        } as any);

        const { container } = render(
            <BrowserRouter>
                <RecommendationsPage />
            </BrowserRouter>,
        );

        expect(screen.getByText('Рекомендованные курсы')).toBeInTheDocument();
        expect(container.querySelector('.course-card-skeleton')).toBeInTheDocument();
    });

    it('shows error state', () => {
        mockedUseProfile.mockReturnValue({
            recommendations: [],
            isLoading: false,
            error: 'Failed to load',
            refetch: vi.fn(),
        } as any);

        render(
            <BrowserRouter>
                <RecommendationsPage />
            </BrowserRouter>,
        );

        expect(screen.getByText('Failed to load')).toBeInTheDocument();
    });

    it('renders recommendations grid', () => {
        mockedUseProfile.mockReturnValue({
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
            error: null,
            refetch: vi.fn(),
        } as any);

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
        mockedUseProfile.mockReturnValue({
            recommendations: [],
            isLoading: false,
            error: null,
            refetch: vi.fn(),
        } as any);

        render(
            <BrowserRouter>
                <RecommendationsPage />
            </BrowserRouter>,
        );

        expect(screen.getByText('Рекомендованные курсы')).toBeInTheDocument();
    });
});
