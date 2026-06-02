import { renderHook, act, waitFor } from '@testing-library/react';
import { useCourseTracking } from '../hooks/courseTrackHook';
import { actionsApi } from '../services/actionsApi';

vi.mock('../services/actionsApi', () => ({
    actionsApi: {
        sendAction: vi.fn(),
        sendEngagement: vi.fn(),
    },
}));

const mockedSendAction = vi.mocked(actionsApi.sendAction);
const mockedSendEngagement = vi.mocked(actionsApi.sendEngagement);

describe('useCourseTracking', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        mockedSendAction.mockResolvedValue({ status: 'liked' });
        mockedSendEngagement.mockResolvedValue(undefined);
    });

    it('initializes liked state from initialLiked prop', () => {
        const { result } = renderHook(() => useCourseTracking('1', true));
        expect(result.current.isLiked).toBe(true);
    });

    it('sends like once and blocks repeat clicks', async () => {
        const { result } = renderHook(() => useCourseTracking('42', false));

        await act(async () => {
            await result.current.handleLike();
        });

        expect(mockedSendAction).toHaveBeenCalledWith({
            course_id: '42',
            action_type: 'like',
        });
        expect(result.current.isLiked).toBe(true);

        mockedSendAction.mockClear();

        await act(async () => {
            await result.current.handleLike();
        });

        expect(mockedSendAction).not.toHaveBeenCalled();
    });

    it('does not send like when already liked initially', async () => {
        const { result } = renderHook(() => useCourseTracking('42', true));

        await act(async () => {
            await result.current.handleLike();
        });

        expect(mockedSendAction).not.toHaveBeenCalledWith(
            expect.objectContaining({ action_type: 'like' }),
        );
    });

    it('sends view on mount', async () => {
        renderHook(() => useCourseTracking('7', false));

        await waitFor(() => {
            expect(mockedSendAction).toHaveBeenCalledWith({
                course_id: '7',
                action_type: 'view',
            });
        });
    });
});
