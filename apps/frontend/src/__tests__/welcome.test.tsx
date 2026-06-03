import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { WelcomePage } from '../components/auth_page/WelcomePage'

describe('WelcomePage', () => {
    it('renders welcome title', () => {
        render(
            <BrowserRouter>
                <WelcomePage />
            </BrowserRouter>
        )

        expect(screen.getByText('Добро Пожаловать на платформу')).toBeInTheDocument()
    })

    it('has navigation buttons', () => {
        render(
            <BrowserRouter>
                <WelcomePage />
            </BrowserRouter>
        )

        expect(screen.getByText('Вход')).toBeInTheDocument()
        expect(screen.getByText('Регистрация')).toBeInTheDocument()
    })

    it('navigates to login on button click', () => {
        render(
            <BrowserRouter>
                <WelcomePage />
            </BrowserRouter>
        )

        fireEvent.click(screen.getByText('Вход'))
    })
})