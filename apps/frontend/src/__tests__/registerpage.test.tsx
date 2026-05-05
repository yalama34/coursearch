import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { RegisterPage } from '../components/auth_page/RegisterPage'
import { useAuth } from '../hooks/useAuth'

vi.mock('../hooks/useAuth')
const mockedUseAuth = vi.mocked(useAuth)

describe('RegisterPage', () => {
    const mockRegister = vi.fn()

    beforeEach(() => {
        mockedUseAuth.mockReturnValue({
            register: mockRegister,
            error: null,
            isLoading: false,
        } as any)
    })

    it('renders registration form', () => {
        render(
            <BrowserRouter>
                <RegisterPage />
            </BrowserRouter>
        )

        expect(screen.getByText('Регистрация')).toBeInTheDocument()
        expect(screen.getAllByPlaceholderText('Nickname')).toHaveLength(1)
        expect(screen.getByPlaceholderText('Пароль')).toBeInTheDocument()
        expect(screen.getByPlaceholderText('Повторите пароль')).toBeInTheDocument()
    })

    it('validates password match', async () => {
        window.alert = vi.fn()

        render(
            <BrowserRouter>
                <RegisterPage />
            </BrowserRouter>
        )

        fireEvent.change(screen.getByPlaceholderText('Nickname'), {
            target: { value: 'newuser' },
        })
        fireEvent.change(screen.getByPlaceholderText('Пароль'), {
            target: { value: 'password123' },
        })
        fireEvent.change(screen.getByPlaceholderText('Повторите пароль'), {
            target: { value: 'different' },
        })
        fireEvent.click(screen.getByText('Войти'))

        await waitFor(() => {
            expect(window.alert).toHaveBeenCalledWith('Пароли не совпадают!')
        })
    })

    it('calls register on valid form submit', async () => {
        mockRegister.mockResolvedValue(true)

        render(
            <BrowserRouter>
                <RegisterPage />
            </BrowserRouter>
        )

        fireEvent.change(screen.getByPlaceholderText('Nickname'), {
            target: { value: 'newuser' },
        })
        fireEvent.change(screen.getByPlaceholderText('Пароль'), {
            target: { value: 'password123' },
        })
        fireEvent.change(screen.getByPlaceholderText('Повторите пароль'), {
            target: { value: 'password123' },
        })
        fireEvent.click(screen.getByText('Войти'))

        await waitFor(() => {
            expect(mockRegister).toHaveBeenCalledWith('newuser', 'password123')
        })
    })
})