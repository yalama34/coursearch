import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { LoginPage } from '../components/auth_page/LoginPage'
import { useAuth } from '../hooks/useAuth'

vi.mock('../hooks/useAuth')
const mockedUseAuth = vi.mocked(useAuth)

describe('LoginPage', () => {
    const mockLogin = vi.fn()

    beforeEach(() => {
        mockedUseAuth.mockReturnValue({
            login: mockLogin,
            error: null,
            isLoading: false,
        } as any)
    })

    it('renders login form', () => {
        render(
            <BrowserRouter>
                <LoginPage />
            </BrowserRouter>
        )

        expect(screen.getByText('Вход')).toBeInTheDocument()
        expect(screen.getByPlaceholderText('Nickname')).toBeInTheDocument()
        expect(screen.getByPlaceholderText('Пароль')).toBeInTheDocument()
        expect(screen.getByText('Войти')).toBeInTheDocument()
    })

    it('calls login on form submit', async () => {
        mockLogin.mockResolvedValue(true)

        render(
            <BrowserRouter>
                <LoginPage />
            </BrowserRouter>
        )

        fireEvent.change(screen.getByPlaceholderText('Nickname'), {
            target: { value: 'testuser' },
        })
        fireEvent.change(screen.getByPlaceholderText('Пароль'), {
            target: { value: 'password123' },
        })
        fireEvent.click(screen.getByText('Войти'))

        await waitFor(() => {
            expect(mockLogin).toHaveBeenCalledWith('testuser', 'password123')
        })
    })

    it('shows error message', () => {
        mockedUseAuth.mockReturnValue({
            login: mockLogin,
            error: 'Wrong credentials',
            isLoading: false,
        } as any)

        render(
            <BrowserRouter>
                <LoginPage />
            </BrowserRouter>
        )

        expect(screen.getByText('Wrong credentials')).toBeInTheDocument()
    })

    it('disables button while loading', () => {
        mockedUseAuth.mockReturnValue({
            login: mockLogin,
            error: null,
            isLoading: true,
        } as any)

        render(
            <BrowserRouter>
                <LoginPage />
            </BrowserRouter>
        )

        expect(screen.getByText('Вход...')).toBeDisabled()
    })
})