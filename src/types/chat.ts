export type MessageRole = 'user' | 'assistant';

export type MessageStatus = 'pending' | 'streaming' | 'done' | 'failed';

export type ThinkingStepStatus = 'running' | 'done' | 'failed';

export interface ChatSession {
    id: string;
    title: string;
    createdAt: number;
    updatedAt: number;
}

export interface ThinkingStep {
    id: string;
    label: string;
    status: ThinkingStepStatus;
    icon?: string;
    detail?: string;
}

export interface Citation {
    id: string;
    documentId: string;
    documentName: string;
    chapterPath?: string;
    snippet: string;
    relevanceScore?: number;
    chunkType?: string;
    markerIndex: number;
}

export interface ChatMessage {
    id: string;
    sessionId: string;
    role: MessageRole;
    content: string;
    status: MessageStatus;
    createdAt: number;
    thinkingSteps?: ThinkingStep[];
    citations?: Citation[];
    errorMessage?: string;
}

export type { ApiResponse } from '@/types/api';
