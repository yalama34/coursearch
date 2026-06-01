export interface Tag {
    id: string | number;
    label: string;
}

/** Объяснение из ML-пайплайна (текст + опционально скор уверенности) */
export interface RecommendationExplanation {
    text: string;
    confidence?: number | null;
}

export interface Course {
    id: string | number;
    title: string;
    author: string;
    description: string;
    tags: Tag[];
    recommendationExplanation?: RecommendationExplanation;
    imageUrl: string;
}

export interface ProfileResponse {
    user_id?: number;
    userId?: number;
    name: string;
    interests?: Tag[];
    description?: string;
    favorite_courses?: Course[];
    favoriteCourses?: Course[];
}

export interface RecommendationResponse {
    recommendations: Course[];
}

export interface ProfileData {
    userId: string;
    name: string;
    description?: string;
    interests: Tag[];
    favoriteCourses: Course[];
}

export interface RecommendationsData {
    recommendations: Course[];
}

export interface AuthPayload {
    nickname: string;
    password: string;
}

export interface AuthResponse {
    token: string;
    user_id: number;
    nickname: string;
}

export interface MeResponse {
    user_id: number;
    nickname: string;
}