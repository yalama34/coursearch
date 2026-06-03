export const ENDPOINTS = {
    RECOMMENDATIONS: '/recommendations',
    PROFILE: '/profile',
    COURSES: '/courses',
} as const;

export const STORAGE_KEYS = {
    AUTH_TOKEN: 'authToken',
    USER_ID: 'userId',
} as const;

export const DEFAULT_VALUES = {
    DESCRIPTION_PLACEHOLDER: 'Добавьте описание...',
    MAX_TAGS: 10,
} as const;

export const COLORS = {
    PRIMARY: '#B692E8',
    SECONDARY: '#A9DEF9',
    TAG_BG: '#FFF5BA',
    BACKGROUND: '#333',
    CARD_BACKGROUND: '#555',
} as const;