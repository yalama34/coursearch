import { authApi } from '../services/authApi'

describe('authApi', () => {
    beforeEach(() => {
        vi.stubGlobal('fetch', vi.fn())
    })

    afterEach(() => {
        vi.unstubAllGlobals()
    })

    describe('register', () => {
        it('should register user successfully', async () => {
            const mockResponse = {
                token: 'jwt-token-123',
                user_id: 1,
                nickname: 'testuser',
            }

            vi.mocked(fetch).mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockResponse),
            } as Response)

            const result = await authApi.register({ nickname: 'testuser', password: 'password123' })

            expect(result).toEqual(mockResponse)
            expect(fetch).toHaveBeenCalledWith(
                expect.stringContaining('/register'),
                expect.objectContaining({ method: 'POST' })
            )
        })

        it('should throw error on 409 conflict', async () => {
            vi.mocked(fetch).mockResolvedValueOnce({
                ok: false,
                status: 409,
            } as Response)

            await expect(
                authApi.register({ nickname: 'taken', password: 'password123' })
            ).rejects.toThrow('Nickname already taken')
        })
    })

    describe('login', () => {
        it('should login user successfully', async () => {
            const mockResponse = {
                token: 'jwt-token-456',
                user_id: 1,
                nickname: 'testuser',
            }

            vi.mocked(fetch).mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockResponse),
            } as Response)

            const result = await authApi.login({ nickname: 'testuser', password: 'password123' })

            expect(result).toEqual(mockResponse)
        })

        it('should throw error on 401 unauthorized', async () => {
            vi.mocked(fetch).mockResolvedValueOnce({
                ok: false,
                status: 401,
            } as Response)

            await expect(
                authApi.login({ nickname: 'wrong', password: 'wrong' })
            ).rejects.toThrow('Wrong nickname or password')
        })
    })

    describe('logout', () => {
        it('should logout successfully', async () => {
            vi.mocked(fetch).mockResolvedValueOnce({
                ok: true,
            } as Response)

            await expect(authApi.logout('token-123')).resolves.not.toThrow()
        })

        it('should throw error on failure', async () => {
            vi.mocked(fetch).mockResolvedValueOnce({
                ok: false,
                status: 500,
            } as Response)

            await expect(authApi.logout('token-123')).rejects.toThrow('Logout failed')
        })
    })

    describe('getMe', () => {
        it('should get current user successfully', async () => {
            const mockResponse = { user_id: 1, nickname: 'testuser' }

            vi.mocked(fetch).mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockResponse),
            } as Response)

            const result = await authApi.getMe('token-123')

            expect(result).toEqual(mockResponse)
            expect(fetch).toHaveBeenCalledWith(
                expect.stringContaining('/me'),
                expect.objectContaining({
                    headers: expect.objectContaining({
                        'Authorization': 'Bearer token-123',
                    }),
                })
            )
        })

        it('should throw error on unauthorized', async () => {
            vi.mocked(fetch).mockResolvedValueOnce({
                ok: false,
                status: 401,
            } as Response)

            await expect(authApi.getMe('invalid-token')).rejects.toThrow('Not authorized')
        })
    })
})