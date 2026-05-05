import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { RecommendationsPage } from '../components/rec_page/RecommendationsPage'
import { useProfile } from '../hooks/profilehook'

vi.mock('../hooks/profilehook')
const mockedUseProfile = vi.mocked(useProfile)

describe('RecommendationsPage', () => {
    beforeEach(() => {
        vi.clearAllMocks()
    })

    it('shows loading state', () => {
        mockedUseProfile.mockReturnValue({
            recommendations: [],
            isLoading: true,
            error: null,
        } as any)

        render(
            <BrowserRouter>
                <RecommendationsPage />
            </BrowserRouter>
        )

        expect(screen.getByText('Загрузка...')).toBeInTheDocument()
    })

    it('shows error state', () => {
        mockedUseProfile.mockReturnValue({
            recommendations: [],
            isLoading: false,
            error: 'Failed to load',
        } as any)

        render(
            <BrowserRouter>
                <RecommendationsPage />
            </BrowserRouter>
        )

        expect(screen.getByText('Failed to load')).toBeInTheDocument()
    })

    it('renders recommendations grid', () => {
        mockedUseProfile.mockReturnValue({
            recommendations: [
                {
                    id: '1',
                    title: 'Course 1',
                    description: 'Desc 1',
                    tags: [{ id: '1', label: 'Tag1' }],
                },
                {
                    id: '2',
                    title: 'Course 2',
                    description: 'Desc 2',
                    tags: [],
                },
            ],
            isLoading: false,
            error: null,
        } as any)

        render(
            <BrowserRouter>
                <RecommendationsPage />
            </BrowserRouter>
        )

        expect(screen.getByText('Course 1')).toBeInTheDocument()
        expect(screen.getByText('Course 2')).toBeInTheDocument()
        expect(screen.getByText('Tag1')).toBeInTheDocument()
    })

    it('has page title', () => {
        mockedUseProfile.mockReturnValue({
            recommendations: [],
            isLoading: false,
            error: null,
        } as any)

        render(
            <BrowserRouter>
                <RecommendationsPage />
            </BrowserRouter>
        )

        expect(screen.getByText('Рекомендованные курсы')).toBeInTheDocument()
    })
})