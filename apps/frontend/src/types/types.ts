export interface Tag {
    id: string | number;
    label: string;
}

export interface Course {
    id: string | number;
    title: string;
    description: string;
    tags: Tag[];
}

export interface ProfileResponse {
    user_id?: number;
    userId?: number;
    name: string;
    interests?: Tag[];
    favorite_courses?: Course[];
    favoriteCourses?: Course[];
}

export interface RecommendationResponse {
    recommendations: Course[];
}

export interface ProfileData {
    userId: string;
    name: string;
    interests: Tag[];
    favoriteCourses: Course[];
}

export interface RecommendationsData {
    recommendations: Course[];
}