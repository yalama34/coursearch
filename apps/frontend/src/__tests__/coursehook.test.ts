import { renderHook, waitFor } from '@testing-library/react'
import { useCourse } from '../hooks/coursehook.ts'
import * as courseApi from '../services/courseapi.ts'

vi.mock('../services/courseapi.ts')
const mockedCourseApi = vi.mocked(courseApi)

describe('useCourse', () => {
    beforeEach(() => {
        vi.clearAllMocks()
    })

    it('should fetch course successfully', async () => {
        mockedCourseApi.getCourseById.mockResolvedValueOnce({
            id: '123',
            title: 'Test Course',
            description: 'Test Desc',
            author: 'Author',
            tags: [],
        })

        const { result } = renderHook(() => useCourse('123'))

        expect(result.current.isLoading).toBe(true)

        await waitFor(() => expect(result.current.isLoading).toBe(false))

        expect(result.current.course?.title).toBe('Test Course')
        expect(result.current.error).toBeNull()
    })

    it('should handle course not found', async () => {
        mockedCourseApi.getCourseById.mockRejectedValueOnce(new Error('Course not found'))

        const { result } = renderHook(() => useCourse('999'))

        await waitFor(() => expect(result.current.error).toBe('Course not found'))
    })

    it('should not fetch if no courseId', () => {
        renderHook(() => useCourse(undefined))

        expect(mockedCourseApi.getCourseById).not.toHaveBeenCalled()
    })
})