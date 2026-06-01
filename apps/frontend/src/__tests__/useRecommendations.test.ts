import { renderHook, waitFor } from '@testing-library/react';
import { useRecommendations } from '../hooks/useRecommendations';
import { getRecommendations, getRecommendationExplanations } from '../services/profileapi';

vi.mock('../services/profileapi', () => ({
    getRecommendations: vi.fn(),
    getRecommendationExplanations: vi.fn(),
}));

const mockedGetRecommendations = vi.mocked(getRecommendations);
const mockedGetExplanations = vi.mocked(getRecommendationExplanations);

const mockCourses = [
    {
        id: 1,
        title: 'Course 1',
        description: 'Desc',
        tags: [],
        author: '',
        imageUrl: '',
        recommendationExplanation: { text: '', confidence: 0.9 },
    },
    {
        id: 2,
        title: 'Course 2',
        description: 'Desc',
        tags: [],
        author: '',
        imageUrl: '',
        recommendationExplanation: { text: '', confidence: 0.8 },
    },
];

describe('useRecommendations', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('loads recommendations first, then merges explanations', async () => {
        mockedGetRecommendations.mockResolvedValueOnce({ recommendations: mockCourses });
        mockedGetExplanations.mockResolvedValueOnce({
            user_id: 1,
            explanations: [
                { course_id: 1, text: 'Explanation for course 1' },
                { course_id: 2, text: 'Explanation for course 2' },
            ],
        });

        const { result } = renderHook(() => useRecommendations('1'));

        await waitFor(() => expect(result.current.isLoading).toBe(false));
        expect(result.current.recommendations).toHaveLength(2);
        expect(result.current.recommendations[0].recommendationExplanation?.text).toBe('');

        await waitFor(() => expect(result.current.isLoadingExplanations).toBe(false));
        expect(result.current.recommendations[0].recommendationExplanation?.text).toBe('Explanation for course 1');
        expect(result.current.recommendations[1].recommendationExplanation?.text).toBe('Explanation for course 2');
        expect(result.current.recommendations[0].recommendationExplanation?.confidence).toBe(0.9);
    });

    it('keeps recommendations when explanations request fails', async () => {
        mockedGetRecommendations.mockResolvedValueOnce({ recommendations: mockCourses });
        mockedGetExplanations.mockRejectedValueOnce(new Error('Explanations failed'));
        const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

        const { result } = renderHook(() => useRecommendations('1'));

        await waitFor(() => expect(result.current.isLoading).toBe(false));
        await waitFor(() => expect(result.current.isLoadingExplanations).toBe(false));

        expect(result.current.recommendations).toHaveLength(2);
        expect(result.current.error).toBeNull();
        expect(consoleSpy).toHaveBeenCalled();

        consoleSpy.mockRestore();
    });
});
