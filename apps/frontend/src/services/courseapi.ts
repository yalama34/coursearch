import {mockCourseDetails} from "../mock/mockData.ts";


const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const getCourseById = async (courseId: string) => {
    if (import.meta.env.VITE_USE_MOCK === 'true') {
        await new Promise(resolve => setTimeout(resolve, 500));
        return mockCourseDetails;
    }

    const res = await fetch(`${API_BASE_URL}/courses/${courseId}`);

    if (!res.ok) {
        if (res.status === 404) throw new Error('Course not found');
        throw new Error(`Failed to fetch course: ${res.status}`);
    }

    return res.json();
};