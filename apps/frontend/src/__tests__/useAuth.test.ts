import { renderHook, waitFor, act } from '@testing-library/react'
import { useAuth } from '../hooks/useAuth'
import { authApi } from '../services/authApi'

vi.mock('../services/authApi')
const mockedAuthApi = vi.mocked(authApi)

describe('useAuth', () => {
    beforeEach(() => {
        vi.clearAllMocks()
        localStorage.clear()
    })

    it('should initialize with no user', async () => {
        const { result } = renderHook(() => useAuth())

        await waitFor(() => expect(result.current.isLoading).toBe(false))

        expect(result.current.isAuthenticated).toBe(false)
        expect(result.current.user).toBeNull()
        expect(result.current.token).toBeNull()
    })

    it('should restore session from localStorage', async () => {
        localStorage.setItem('authToken', 'existing-token')
        mockedAuthApi.getMe.mockResolvedValueOnce({ user_id: 1, nickname: 'testuser' })

        const { result } = renderHook(() => useAuth())

        await waitFor(() => expect(result.current.isLoading).toBe(false))

        expect(result.current.isAuthenticated).toBe(true)
        expect(result.current.user?.nickname).toBe('testuser')
        expect(mockedAuthApi.getMe).toHaveBeenCalledWith('existing-token')
    })

    it('should login successfully', async () => {
        mockedAuthApi.login.mockResolvedValueOnce({
            token: 'new-token',
            user_id: 1,
            nickname: 'newuser',
        })

        const { result } = renderHook(() => useAuth())

        await act(async () => {
            const success = await result.current.login('newuser', 'password123')
            expect(success).toBe(true)
        })

        expect(result.current.isAuthenticated).toBe(true)
        expect(result.current.user?.nickname).toBe('newuser')
        expect(localStorage.getItem('authToken')).toBe('new-token')
    })

    it('should handle login failure', async () => {
        mockedAuthApi.login.mockRejectedValueOnce(new Error('Wrong credentials'))

        const { result } = renderHook(() => useAuth())

        await act(async () => {
            const success = await result.current.login('wrong', 'wrong')
            expect(success).toBe(false)
        })

        expect(result.current.error).toBe('Wrong credentials')
    })

    it('should register successfully', async () => {
        mockedAuthApi.register.mockResolvedValueOnce({
            token: 'reg-token',
            user_id: 2,
            nickname: 'reguser',
        })

        const { result } = renderHook(() => useAuth())

        await act(async () => {
            const success = await result.current.register('reguser', 'password123')
            expect(success).toBe(true)
        })

        expect(result.current.isAuthenticated).toBe(true)
        expect(result.current.user?.nickname).toBe('reguser')
    })

    it('should logout successfully', async () => {
        localStorage.setItem('authToken', 'token-to-logout')
        mockedAuthApi.getMe.mockResolvedValueOnce({ user_id: 1, nickname: 'testuser' })

        const { result } = renderHook(() => useAuth())
        await waitFor(() => expect(result.current.isLoading).toBe(false))

        mockedAuthApi.logout.mockResolvedValueOnce(undefined)

        await act(async () => {
            await result.current.logout()
        })

        expect(result.current.isAuthenticated).toBe(false)
        expect(localStorage.getItem('authToken')).toBeNull()
    })

    it('should handle invalid token on mount', async () => {
        localStorage.setItem('authToken', 'invalid-token')
        mockedAuthApi.getMe.mockRejectedValueOnce(new Error('Invalid token'))

        const { result } = renderHook(() => useAuth())

        await waitFor(() => expect(result.current.isLoading).toBe(false))

        expect(result.current.isAuthenticated).toBe(false)
        expect(localStorage.getItem('authToken')).toBeNull()
    })
})