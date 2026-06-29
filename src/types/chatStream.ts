/**
 * SSE event contract for POST /api/chat/stream
 * Align mock payloads with these shapes before backend integration.
 */

export type ChatStreamEventName = 'token' | 'thinking' | 'citation' | 'done' | 'error';

export interface ChatStreamRequest {
    sessionId: string;
    messageId: string;
    content: string;
    history: Array<{
        role: 'user' | 'assistant';
        content: string;
    }>;
}

export interface ChatStreamTokenPayload {
    messageId: string;
    sessionId: string;
    content: string;
}

export interface ChatStreamThinkingPayload {
    messageId: string;
    sessionId: string;
    stepId: string;
    label: string;
    status: 'running' | 'done' | 'failed';
    icon?: string;
    detail?: string;
}

export interface ChatStreamCitationPayload {
    messageId: string;
    sessionId: string;
    citation: {
        id: string;
        documentId: string;
        documentName: string;
        chapterPath?: string;
        snippet: string;
        relevanceScore?: number;
        chunkType?: string;
        markerIndex: number;
    };
}

export interface ChatStreamDonePayload {
    messageId: string;
    sessionId: string;
}

export interface ChatStreamErrorPayload {
    messageId: string;
    sessionId: string;
    message: string;
}

export type ChatStreamEventPayload =
    | ChatStreamTokenPayload
    | ChatStreamThinkingPayload
    | ChatStreamCitationPayload
    | ChatStreamDonePayload
    | ChatStreamErrorPayload;

export interface ChatStreamEvent {
    event: ChatStreamEventName;
    data: ChatStreamEventPayload;
}

export type ChatStreamEventHandler = (event: ChatStreamEvent) => void;

export interface ChatStreamOptions {
    signal?: AbortSignal;
    onEvent: ChatStreamEventHandler;
}
