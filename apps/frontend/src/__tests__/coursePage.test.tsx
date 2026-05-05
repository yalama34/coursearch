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
})