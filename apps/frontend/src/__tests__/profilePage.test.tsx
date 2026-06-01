import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ProfilePage } from '../components/prof_page/ProfilePage';
import { useProfile } from '../hooks/profilehook';
import { useAuth } from '../hooks/useAuth';

vi.mock('../hooks/profilehook');
vi.mock('../hooks/useAuth');

const mockedUseProfile = vi.mocked(useProfile);
const mockedUseAuth = vi.mocked(useAuth);

describe('ProfilePage', () => {
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

    it('shows loading state', () => {
        mockedUseProfile.mockReturnValue({
            profile: null,
            isLoading: true,
            error: null,
            refetch: vi.fn(),
        } as any);

        render(
            <BrowserRouter>
                <ProfilePage />
            </BrowserRouter>,
        );

        expect(screen.getByText('Загрузка...')).toBeInTheDocument();
    });

    it('shows error state', () => {
        mockedUseProfile.mockReturnValue({
            profile: null,
            isLoading: false,
            error: 'Failed to load',
            refetch: vi.fn(),
        } as any);

        render(
            <BrowserRouter>
                <ProfilePage />
            </BrowserRouter>,
        );

        expect(screen.getByText('Failed to load')).toBeInTheDocument();
    });

    it('renders profile data', () => {
        mockedUseProfile.mockReturnValue({
            profile: {
                userId: '123',
                name: 'Test User',
                interests: [
                    { id: '1', label: 'React' },
                    { id: '2', label: 'TypeScript' },
                ],
                favoriteCourses: [],
            },
            isLoading: false,
            error: null,
            refetch: vi.fn(),
        } as any);

        render(
            <BrowserRouter>
                <ProfilePage />
            </BrowserRouter>,
        );

        expect(screen.getByText('Test User')).toBeInTheDocument();
        expect(screen.getByText('User ID: 123')).toBeInTheDocument();
        expect(screen.getByText('React')).toBeInTheDocument();
        expect(screen.getByText('TypeScript')).toBeInTheDocument();
    });

    it('renders favorite courses section', () => {
        mockedUseProfile.mockReturnValue({
            profile: {
                userId: '1',
                name: 'User',
                interests: [],
                favoriteCourses: [
                    {
                        id: '1',
                        title: 'Favorite Course',
                        description: 'Desc',
                        tags: [],
                        author: '',
                        imageUrl: '',
                    },
                ],
            },
            isLoading: false,
            error: null,
            refetch: vi.fn(),
        } as any);

        render(
            <BrowserRouter>
                <ProfilePage />
            </BrowserRouter>,
        );

        expect(screen.getByText('Favorite Courses')).toBeInTheDocument();
        expect(screen.getByText('Favorite Course')).toBeInTheDocument();
    });
});
