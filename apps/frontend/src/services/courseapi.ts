import { mockCourseDetails } from '../mock/mockData.ts';
import { Course } from '../types/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const mapCourseDetail = (data: Record<string, unknown>): Course => ({
    id: (data.id ?? data.course_id) as string | number,
    title: (data.title ?? data.name ?? '') as string,
    description: (data.description ?? '') as string,
    author: (data.author ?? '') as string,
    imageUrl: (data.imageUrl ?? '') as string,
    link: typeof data.link === 'string' && data.link.trim() ? data.link.trim() : undefined,
    tags: Array.isArray(data.tags)
        ? data.tags.map((tag: Record<string, unknown>) => ({
              id: (tag.id ?? tag.tag_id) as string | number,
              label: (tag.label ?? tag.name ?? '') as string,
          }))
        : [],
});

export const getCourseById = async (courseId: string): Promise<Course> => {
    if (import.meta.env.VITE_USE_MOCK === 'true') {
        await new Promise((resolve) => setTimeout(resolve, 500));
        return mockCourseDetails;
    }

    const res = await fetch(`${API_BASE_URL}/courses/${courseId}`);

    if (!res.ok) {
        if (res.status === 404) throw new Error('Course not found');
        throw new Error(`Failed to fetch course: ${res.status}`);
    }

    const data = await res.json();
    return mapCourseDetail(data);
};