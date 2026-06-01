import { renderHook, waitFor } from '@testing-library/react';
import { useProfile } from '../hooks/profilehook.ts';
import { getProfile } from '../services/profileapi';

vi.mock('../services/profileapi', () => ({
    getProfile: vi.fn(),
}));

const mockedGetProfile = vi.mocked(getProfile);

describe('useProfile', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('should fetch profile', async () => {
        mockedGetProfile.mockResolvedValueOnce({
            userId: '1',
            name: 'Test',
            interests: [],
            favoriteCourses: [],
        });

        const { result } = renderHook(() => useProfile('1'));

        expect(result.current.isLoading).toBe(true);

        await waitFor(() => expect(result.current.isLoading).toBe(false));

        expect(result.current.profile?.name).toBe('Test');
        expect(result.current.error).toBeNull();
    });

    it('should refetch data when refetch is called', async () => {
        mockedGetProfile.mockResolvedValue({
            userId: '1',
            name: 'Test',
            interests: [],
            favoriteCourses: [],
        });

        const { result } = renderHook(() => useProfile('1'));
        await waitFor(() => expect(result.current.isLoading).toBe(false));

        result.current.refetch();

        await waitFor(() => expect(mockedGetProfile).toHaveBeenCalledTimes(2));
    });

    it('should handle API errors', async () => {
        mockedGetProfile.mockRejectedValueOnce(new Error('Network error'));

        const { result } = renderHook(() => useProfile('1'));

        await waitFor(() => expect(result.current.error).toBe('Network error'));
        expect(result.current.isLoading).toBe(false);
    });
});
