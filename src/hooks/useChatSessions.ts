import { useCallback, useEffect, useRef, useState } from 'react';
import type { ChatMessage, ChatSession } from '@/types/chat';
import {
    createEmptySession,
    deriveSessionTitle,
    loadActiveSessionId,
    loadMessages,
    loadSessions,
    removeMessages,
    saveActiveSessionId,
    saveMessages,
    saveSessions,
} from '@/utils/chatStorage';

function sortSessions(sessions: ChatSession[]): ChatSession[] {
    return [...sessions].sort((left, right) => right.updatedAt - left.updatedAt);
}

export function useChatSessions() {
    const [sessions, setSessions] = useState<ChatSession[]>(() => sortSessions(loadSessions()));
    const [activeSessionId, setActiveSessionId] = useState<string | null>(() => loadActiveSessionId());
    const [messagesBySession, setMessagesBySession] = useState<Record<string, ChatMessage[]>>(() => {
        const initialSessions = sortSessions(loadSessions());
        const map: Record<string, ChatMessage[]> = {};

        for (const session of initialSessions) {
            map[session.id] = loadMessages(session.id);
        }

        return map;
    });

    const initializedRef = useRef(false);

    useEffect(() => {
        if (initializedRef.current) {
            return;
        }

        initializedRef.current = true;

        if (sessions.length === 0) {
            const session = createEmptySession();
            setSessions([session]);
            setActiveSessionId(session.id);
            setMessagesBySession({ [session.id]: [] });
            saveSessions([session]);
            saveActiveSessionId(session.id);
            saveMessages(session.id, []);
            return;
        }

        if (!activeSessionId || !sessions.some((session) => session.id === activeSessionId)) {
            const fallbackId = sessions[0]?.id ?? null;
            setActiveSessionId(fallbackId);
            saveActiveSessionId(fallbackId);
        }
    }, [activeSessionId, sessions]);

    const activeMessages = activeSessionId ? (messagesBySession[activeSessionId] ?? []) : [];

    const persistSessions = useCallback((nextSessions: ChatSession[]) => {
        const sorted = sortSessions(nextSessions);
        setSessions(sorted);
        saveSessions(sorted);
    }, []);

    const persistMessages = useCallback((sessionId: string, messages: ChatMessage[]) => {
        setMessagesBySession((previous) => {
            const next = { ...previous, [sessionId]: messages };
            saveMessages(sessionId, messages);
            return next;
        });
    }, []);

    const createSession = useCallback(() => {
        const session = createEmptySession();
        persistSessions([session, ...sessions]);
        setActiveSessionId(session.id);
        saveActiveSessionId(session.id);
        persistMessages(session.id, []);
        return session.id;
    }, [persistMessages, persistSessions, sessions]);

    const switchSession = useCallback((sessionId: string) => {
        setActiveSessionId(sessionId);
        saveActiveSessionId(sessionId);

        setMessagesBySession((previous) => {
            if (previous[sessionId]) {
                return previous;
            }

            const loaded = loadMessages(sessionId);
            saveMessages(sessionId, loaded);
            return { ...previous, [sessionId]: loaded };
        });
    }, []);

    const deleteSession = useCallback(
        (sessionId: string) => {
            const remaining = sessions.filter((session) => session.id !== sessionId);
            removeMessages(sessionId);

            setMessagesBySession((previous) => {
                const next = { ...previous };
                delete next[sessionId];
                return next;
            });

            if (remaining.length === 0) {
                const session = createEmptySession();
                persistSessions([session]);
                setActiveSessionId(session.id);
                saveActiveSessionId(session.id);
                persistMessages(session.id, []);
                return;
            }

            persistSessions(remaining);

            if (activeSessionId === sessionId) {
                const nextActiveId = sortSessions(remaining)[0].id;
                setActiveSessionId(nextActiveId);
                saveActiveSessionId(nextActiveId);
            }
        },
        [activeSessionId, persistMessages, persistSessions, sessions],
    );

    const updateSessionMeta = useCallback(
        (sessionId: string, patch: Partial<Pick<ChatSession, 'title' | 'updatedAt'>>) => {
            const nextSessions = sessions.map((session) =>
                session.id === sessionId ? { ...session, ...patch } : session,
            );
            persistSessions(nextSessions);
        },
        [persistSessions, sessions],
    );

    const setSessionMessages = useCallback(
        (sessionId: string, updater: (messages: ChatMessage[]) => ChatMessage[]) => {
            setMessagesBySession((previous) => {
                const current = previous[sessionId] ?? [];
                const nextMessages = updater(current);
                saveMessages(sessionId, nextMessages);
                return { ...previous, [sessionId]: nextMessages };
            });
        },
        [],
    );

    const touchSession = useCallback(
        (sessionId: string, firstUserMessage?: string) => {
            const session = sessions.find((item) => item.id === sessionId);
            if (!session) {
                return;
            }

            const shouldUpdateTitle =
                session.title === '新对话' && firstUserMessage && firstUserMessage.trim().length > 0;

            updateSessionMeta(sessionId, {
                updatedAt: Date.now(),
                ...(shouldUpdateTitle ? { title: deriveSessionTitle(firstUserMessage) } : {}),
            });
        },
        [sessions, updateSessionMeta],
    );

    return {
        sessions,
        activeSessionId,
        activeMessages,
        createSession,
        switchSession,
        deleteSession,
        setSessionMessages,
        touchSession,
    };
}
