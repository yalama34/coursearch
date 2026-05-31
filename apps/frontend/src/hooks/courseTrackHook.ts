import { useEffect, useRef, useState, useCallback } from 'react';
import { actionsApi } from '../services/actionsApi';

export const useCourseTracking = (courseId: string | undefined) => {
    const [isLiked, setIsLiked] = useState(false);
    const lastSentTime = useRef(Date.now());
    const intervalRef = useRef<number | null>(null);

    const sendView = useCallback(async () => {
        if (!courseId) return;
        try { await actionsApi.sendAction({ course_id: courseId, action_type: 'view' }); }
        catch (e) { console.error('View error', e); }
    }, [courseId]);

    const handleLike = useCallback(async () => {
        if (!courseId) return;
        try {
            await actionsApi.sendAction({ course_id: courseId, action_type: 'like' });
            setIsLiked(prev => !prev);
        } catch (e) { console.error('Like error', e); }
    }, [courseId]);

    useEffect(() => {
        if (!courseId) return;

        sendView();

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
    }, [courseId, sendView]);

    return { isLiked, handleLike };
};