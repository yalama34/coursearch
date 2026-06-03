import { useState, useEffect } from 'react';
import { getCourseById } from '../services/courseapi';
import { Course } from '../types/types';

export const useCourse = (courseId: string | undefined) => {
    const [course, setCourse] = useState<Course | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!courseId) return;

        const fetchCourse = async () => {
            setIsLoading(true);
            setError(null);
            try {
                const data = await getCourseById(courseId);
                setCourse(data);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load course');
            } finally {
                setIsLoading(false);
            }
        };

        fetchCourse();
    }, [courseId]);

    return { course, isLoading, error };
};