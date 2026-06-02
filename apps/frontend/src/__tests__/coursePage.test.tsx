import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { CoursePage } from '../components/course_page/CoursePage'
import { useCourse } from '../hooks/coursehook'

vi.mock('../hooks/coursehook')
const mockedUseCourse = vi.mocked(useCourse)

describe('CoursePage', () => {
    beforeEach(() => {
        vi.clearAllMocks()
    })

    it('shows loading state', () => {
        mockedUseCourse.mockReturnValue({
            course: null,
            isLoading: true,
            error: null,
        })

        render(
            <BrowserRouter>
                <CoursePage />
            </BrowserRouter>
        )

        expect(screen.getByText('Loading...')).toBeInTheDocument()
    })

    it('shows error state', () => {
        mockedUseCourse.mockReturnValue({
            course: null,
            isLoading: false,
            error: 'Course not found',
        })

        render(
            <BrowserRouter>
                <CoursePage />
            </BrowserRouter>
        )

        expect(screen.getByText('Course not found')).toBeInTheDocument()
    })

    it('renders course data', () => {
        mockedUseCourse.mockReturnValue({
            course: {
                id: '1',
                title: 'Test Course',
                description: 'Test Description',
                author: 'Test Author',
                imageUrl: '',
                tags: [
                    { id: '1', label: 'React' },
                    { id: '2', label: 'TypeScript' },
                ],
            },
            isLoading: false,
            error: null,
        })

        render(
            <BrowserRouter>
                <CoursePage />
            </BrowserRouter>
        )

        expect(screen.getByText('Test Course')).toBeInTheDocument()
        expect(screen.getByText('Test Description')).toBeInTheDocument()
        expect(screen.getByText('Test Author')).toBeInTheDocument()
        expect(screen.getByText('React')).toBeInTheDocument()
        expect(screen.getByText('TypeScript')).toBeInTheDocument()
    })

    it('renders external link when course has link', () => {
        mockedUseCourse.mockReturnValue({
            course: {
                id: '1',
                title: 'Test Course',
                description: 'Test Description',
                author: 'Test Author',
                imageUrl: '',
                link: 'https://example.com/course',
                tags: [],
            },
            isLoading: false,
            error: null,
        })

        render(
            <BrowserRouter>
                <CoursePage />
            </BrowserRouter>
        )

        const link = screen.getByRole('link', { name: 'Перейти на курс' })
        expect(link).toHaveAttribute('href', 'https://example.com/course')
        expect(link).toHaveAttribute('target', '_blank')
    })

    it('does not render external link when course has no link', () => {
        mockedUseCourse.mockReturnValue({
            course: {
                id: '1',
                title: 'Test Course',
                description: 'Test Description',
                author: 'Test Author',
                imageUrl: '',
                tags: [],
            },
            isLoading: false,
            error: null,
        })

        render(
            <BrowserRouter>
                <CoursePage />
            </BrowserRouter>
        )

        expect(screen.queryByRole('link', { name: 'Перейти на курс' })).not.toBeInTheDocument()
    })
})