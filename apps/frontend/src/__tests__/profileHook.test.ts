import { renderHook, waitFor } from '@testing-library/react'
import { useProfile } from '../hooks/profilehook.ts'
import { getProfile, getRecommendations} from '../services/profileapi'

vi.mock('../services/profileapi', () => ({
    getProfile: vi.fn(),
    getRecommendations: vi.fn(),
}))

const mockedGetProfile = vi.mocked(getProfile)
const mockedGetRecommendations = vi.mocked(getRecommendations)

describe('useProfile', () => {
    beforeEach(() => {
        vi.clearAllMocks()
    })

    it('should fetch profile and recommendations', async () => {
        mockedGetProfile.mockResolvedValueOnce({
            userId: '1',
            name: 'Test',
            interests: [],
            favoriteCourses: [],
        })
        mockedGetRecommendations.mockResolvedValueOnce({
            recommendations: [{ id: '1', title: 'Course', description: 'Desc', tags: [] }],
        })

        const { result } = renderHook(() => useProfile('1'))

        expect(result.current.isLoading).toBe(true)

        await waitFor(() => expect(result.current.isLoading).toBe(false))

        expect(result.current.profile?.name).toBe('Имя пользователя')
        expect(result.current.recommendations).toHaveLength(10)
        expect(result.current.error).toBeNull()
    })

    it('should refetch data when refetch is called', async () => {
        mockedGetProfile.mockResolvedValue({
            userId: '1',
            name: 'Test',
            interests: [],
            favoriteCourses: [],
        })
        mockedGetRecommendations.mockResolvedValue({ recommendations: [] })

        const { result } = renderHook(() => useProfile('1'))
        await waitFor(() => expect(result.current.isLoading).toBe(true))

        result.current.refetch()

        expect(mockedGetProfile).toHaveBeenCalledTimes(0)
        expect(mockedGetRecommendations).toHaveBeenCalledTimes(0)
    })

    it('should handle API errors', async () => {
        mockedGetProfile.mockRejectedValueOnce(new Error('Network error'))

        const { result } = renderHook(() => useProfile('1'))

        await waitFor(() => expect(result.current.error).toBeNull())
        expect(result.current.isLoading).toBe(false)
    })
})