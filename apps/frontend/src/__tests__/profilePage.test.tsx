import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { ProfilePage } from '../components/prof_page/ProfilePage'
import { useProfile } from '../hooks/profilehook'

vi.mock('../hooks/profilehook')
const mockedUseProfile = vi.mocked(useProfile)

describe('ProfilePage', () => {
    beforeEach(() => {
        vi.clearAllMocks()
    })

    it('shows loading state', () => {
        mockedUseProfile.mockReturnValue({
            profile: null,
            recommendations: [],
            isLoading: true,
            error: null,
        } as any)

        render(
            <BrowserRouter>
                <ProfilePage />
            </BrowserRouter>
        )

        expect(screen.getByText('Загрузка...')).toBeInTheDocument()
    })

    it('shows error state', () => {
        mockedUseProfile.mockReturnValue({
            profile: null,
            recommendations: [],
            isLoading: false,
            error: 'Failed to load',
        } as any)

        render(
            <BrowserRouter>
                <ProfilePage />
            </BrowserRouter>
        )

        expect(screen.getByText('Failed to load')).toBeInTheDocument()
    })

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
            recommendations: [],
            isLoading: false,
            error: null,
        } as any)

        render(
            <BrowserRouter>
                <ProfilePage />
            </BrowserRouter>
        )

        expect(screen.getByText('Test User')).toBeInTheDocument()
        expect(screen.getByText('User ID: 123')).toBeInTheDocument()
        expect(screen.getByText('React')).toBeInTheDocument()
        expect(screen.getByText('TypeScript')).toBeInTheDocument()
    })

    it('renders favorite courses section', () => {
        mockedUseProfile.mockReturnValue({
            profile: {
                userId: '1',
                name: 'User',
                interests: [],
                favoriteCourses: [
                    { id: '1', title: 'Favorite Course', description: 'Desc', tags: [] },
                ],
            },
            recommendations: [],
            isLoading: false,
            error: null,
        } as any)

        render(
            <BrowserRouter>
                <ProfilePage />
            </BrowserRouter>
        )

        expect(screen.getByText('Favorite Courses')).toBeInTheDocument()
        expect(screen.getByText('Favorite Course')).toBeInTheDocument()
    })
})