import { useEffect, useRef, useState, useCallback } from 'react';
import { actionsApi } from '../services/actionsApi';

export const useCourseTracking = (
    courseId: string | undefined,
    initialLiked = false,
) => {
    const [isLiked, setIsLiked] = useState(initialLiked);
    const [isLiking, setIsLiking] = useState(false);
    const lastSentTime = useRef(Date.now());
    const intervalRef = useRef<number | null>(null);

    useEffect(() => {
        setIsLiked(initialLiked);
    }, [initialLiked, courseId]);

    const handleLike = useCallback(async () => {
        if (!courseId || isLiked || isLiking) return;

        setIsLiking(true);
        try {
            await actionsApi.sendAction({ course_id: courseId, action_type: 'like' });
            setIsLiked(true);
        } catch (e) {
            console.error('Like error', e);
        } finally {
            setIsLiking(false);
        }
    }, [courseId, isLiked, isLiking]);

    useEffect(() => {
        if (!courseId) return;

        const startTracking = () => {
            intervalRef.current = window.setInterval(() => {
                const now = Date.now();
                const delta = Math.round((now - lastSentTime.current) / 1000);
                if (delta > 0) {
                    actionsApi.sendEngagement({ course_id: courseId, value: delta }).catch(console.error);
                    lastSentTime.current = now;
                }
            }, 5000);
        };

        startTracking();

        const handleVisibility = () => {
            if (document.hidden) {
                if (intervalRef.current) clearInterval(intervalRef.current);
            } else {
                lastSentTime.current = Date.now();
                startTracking();
            }
        };
        document.addEventListener('visibilitychange', handleVisibility);

        return () => {
            document.removeEventListener('visibilitychange', handleVisibility);
            if (intervalRef.current) clearInterval(intervalRef.current);
            const finalDelta = Math.round((Date.now() - lastSentTime.current) / 1000);
            if (finalDelta > 0) {
                actionsApi.sendEngagement({ course_id: courseId, value: finalDelta }).catch(console.error);
            }
        };
    }, [courseId]);

    return { isLiked, isLiking, handleLike };
};
