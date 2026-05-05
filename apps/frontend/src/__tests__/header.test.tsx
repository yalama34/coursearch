import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { Header } from '../components/header/Header'

const renderHeader = (props = {}) =>
    render(
        <BrowserRouter>
            <Header activeTab="recommendations" onTabChange={vi.fn()} {...props} />
        </BrowserRouter>
    )

describe('Header', () => {
    it('renders navigation', () => {
        renderHeader()
        expect(screen.getByText('Рекомендации')).toBeInTheDocument()
        expect(screen.getByText('Курсы')).toBeInTheDocument()
    })

    it('renders search input', () => {
        renderHeader()

        const searchInput = screen.getByPlaceholderText('Поиск Курса')
        expect(searchInput).toBeInTheDocument()
    })

    it('calls onTabChange when clicking nav buttons', () => {
        const onTabChange = vi.fn()
        render(
            <BrowserRouter>
                <Header activeTab="recommendations" onTabChange={onTabChange} />
            </BrowserRouter>
        )

        fireEvent.click(screen.getByText('Рекомендации'))
        expect(onTabChange).toHaveBeenCalledWith('recommendations')
    })

    it('disables Courses button', () => {
        renderHeader()

        const coursesBtn = screen.getByText('Курсы')
        expect(coursesBtn).toBeDisabled()
    })

    it('shows active state on current tab', () => {
        const { container } = render(
            <BrowserRouter>
                <Header activeTab="recommendations" onTabChange={vi.fn()} />
            </BrowserRouter>
        )

        const activeBtn = container.querySelector('.nav-button.active')
        expect(activeBtn).toHaveTextContent('Рекомендации')
    })
})