import type { ChatSession, ChatMessage } from '@/types/chat';

const STORAGE_VERSION = 'v1';
const KEYS = {
    sessions: `chat_${STORAGE_VERSION}_sessions`,
    activeSessionId: `chat_${STORAGE_VERSION}_active_session`,
    messagesPrefix: `chat_${STORAGE_VERSION}_messages_`,
} as const;

const MAX_TITLE_LENGTH = 30;

function safeParse<T>(raw: string | null, fallback: T): T {
    if (!raw) {
        return fallback;
    }

    try {
        return JSON.parse(raw) as T;
    } catch {
        return fallback;
    }
}

export function deriveSessionTitle(firstUserMessage: string): string {
    const trimmed = firstUserMessage.trim();
    if (!trimmed) {
        return '新对话';
    }

    if (trimmed.length <= MAX_TITLE_LENGTH) {
        return trimmed;
    }

    return `${trimmed.slice(0, MAX_TITLE_LENGTH)}...`;
}

export function loadSessions(): ChatSession[] {
    return safeParse<ChatSession[]>(localStorage.getItem(KEYS.sessions), []);
}

export function saveSessions(sessions: ChatSession[]): void {
    localStorage.setItem(KEYS.sessions, JSON.stringify(sessions));
}

export function loadActiveSessionId(): string | null {
    return localStorage.getItem(KEYS.activeSessionId);
}

export function saveActiveSessionId(sessionId: string | null): void {
    if (sessionId) {
        localStorage.setItem(KEYS.activeSessionId, sessionId);
        return;
    }

    localStorage.removeItem(KEYS.activeSessionId);
}

export function loadMessages(sessionId: string): ChatMessage[] {
    return safeParse<ChatMessage[]>(
        localStorage.getItem(`${KEYS.messagesPrefix}${sessionId}`),
        [],
    );
}

export function saveMessages(sessionId: string, messages: ChatMessage[]): void {
    localStorage.setItem(`${KEYS.messagesPrefix}${sessionId}`, JSON.stringify(messages));
}

export function removeMessages(sessionId: string): void {
    localStorage.removeItem(`${KEYS.messagesPrefix}${sessionId}`);
}

export function createEmptySession(): ChatSession {
    const now = Date.now();
    return {
        id: crypto.randomUUID(),
        title: '新对话',
        createdAt: now,
        updatedAt: now,
    };
}
