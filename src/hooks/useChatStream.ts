import { useCallback, useRef, useState } from 'react';
import type { ChatMessage, Citation, ThinkingStep } from '@/types/chat';
import type { ChatStreamEvent } from '@/types/chatStream';
import { streamChatResponse } from '@/services/chatService';

interface UseChatStreamParams {
    sessionId: string | null;
    messages: ChatMessage[];
    setSessionMessages: (
        sessionId: string,
        updater: (messages: ChatMessage[]) => ChatMessage[],
    ) => void;
    touchSession: (sessionId: string, firstUserMessage?: string) => void;
}

function updateAssistantMessage(
    messages: ChatMessage[],
    assistantMessageId: string,
    patch: Partial<ChatMessage>,
): ChatMessage[] {
    return messages.map((message) =>
        message.id === assistantMessageId ? { ...message, ...patch } : message,
    );
}

function applyStreamEvent(messages: ChatMessage[], event: ChatStreamEvent): ChatMessage[] {
    const { event: eventName, data } = event;
    const messageId = 'messageId' in data ? data.messageId : '';

    if (!messageId) {
        return messages;
    }

    if (eventName === 'token' && 'content' in data) {
        return updateAssistantMessage(messages, messageId, {
            content: (messages.find((item) => item.id === messageId)?.content ?? '') + data.content,
            status: 'streaming',
        });
    }

    if (eventName === 'thinking' && 'stepId' in data) {
        return messages.map((message) => {
            if (message.id !== messageId) {
                return message;
            }

            const existing = message.thinkingSteps ?? [];
            const nextStep: ThinkingStep = {
                id: data.stepId,
                label: data.label,
                status: data.status,
                icon: data.icon,
                detail: data.detail,
            };

            const index = existing.findIndex((step) => step.id === data.stepId);
            const thinkingSteps =
                index >= 0
                    ? existing.map((step, stepIndex) => (stepIndex === index ? nextStep : step))
                    : [...existing, nextStep];

            return { ...message, thinkingSteps, status: 'streaming' };
        });
    }

    if (eventName === 'citation' && 'citation' in data) {
        return messages.map((message) => {
            if (message.id !== messageId) {
                return message;
            }

            const citation: Citation = data.citation;
            const citations = [...(message.citations ?? [])];
            const index = citations.findIndex((item) => item.id === citation.id);
            if (index >= 0) {
                citations[index] = citation;
            } else {
                citations.push(citation);
            }

            return { ...message, citations };
        });
    }

    if (eventName === 'done') {
        return updateAssistantMessage(messages, messageId, { status: 'done' });
    }

    if (eventName === 'error' && 'message' in data) {
        return updateAssistantMessage(messages, messageId, {
            status: 'failed',
            errorMessage: data.message,
        });
    }

    return messages;
}

export function useChatStream({
    sessionId,
    messages,
    setSessionMessages,
    touchSession,
}: UseChatStreamParams) {
    const abortControllerRef = useRef<AbortController | null>(null);
    const [isStreaming, setIsStreaming] = useState(false);

    const cancelStream = useCallback(() => {
        abortControllerRef.current?.abort();
        abortControllerRef.current = null;
        setIsStreaming(false);
    }, []);

    const runStream = useCallback(
        async (userContent: string, existingAssistantId?: string) => {
            if (!sessionId || isStreaming) {
                return;
            }

            const userMessageId = crypto.randomUUID();
            const assistantMessageId = existingAssistantId ?? crypto.randomUUID();
            const now = Date.now();

            if (!existingAssistantId) {
                const userMessage: ChatMessage = {
                    id: userMessageId,
                    sessionId,
                    role: 'user',
                    content: userContent,
                    status: 'done',
                    createdAt: now,
                };

                const assistantPlaceholder: ChatMessage = {
                    id: assistantMessageId,
                    sessionId,
                    role: 'assistant',
                    content: '',
                    status: 'streaming',
                    createdAt: now + 1,
                    thinkingSteps: [],
                    citations: [],
                };

                setSessionMessages(sessionId, (previous) => [...previous, userMessage, assistantPlaceholder]);
                touchSession(sessionId, userContent);
            } else {
                setSessionMessages(sessionId, (previous) =>
                    previous.map((message) =>
                        message.id === assistantMessageId
                            ? {
                                  ...message,
                                  content: '',
                                  status: 'streaming',
                                  errorMessage: undefined,
                                  thinkingSteps: [],
                                  citations: [],
                              }
                            : message,
                    ),
                );
            }

            const history = messages
                .filter((message) => message.status === 'done')
                .map((message) => ({
                    role: message.role,
                    content: message.content,
                }));

            if (!existingAssistantId) {
                history.push({ role: 'user' as const, content: userContent });
            }

            const controller = new AbortController();
            abortControllerRef.current = controller;
            setIsStreaming(true);

            try {
                await streamChatResponse(
                    {
                        sessionId,
                        messageId: assistantMessageId,
                        content: userContent,
                        history,
                    },
                    {
                        signal: controller.signal,
                        onEvent: (event) => {
                            setSessionMessages(sessionId, (previous) => applyStreamEvent(previous, event));
                        },
                    },
                );
            } catch (error) {
                if (error instanceof DOMException && error.name === 'AbortError') {
                    setSessionMessages(sessionId, (previous) =>
                        updateAssistantMessage(previous, assistantMessageId, { status: 'done' }),
                    );
                    return;
                }

                const errorMessage = error instanceof Error ? error.message : '生成失败，请稍后重试';
                setSessionMessages(sessionId, (previous) =>
                    updateAssistantMessage(previous, assistantMessageId, {
                        status: 'failed',
                        errorMessage,
                    }),
                );
            } finally {
                setIsStreaming(false);
                abortControllerRef.current = null;
            }
        },
        [isStreaming, messages, sessionId, setSessionMessages, touchSession],
    );

    const sendMessage = useCallback(
        (content: string) => {
            const trimmed = content.trim();
            if (!trimmed) {
                return;
            }

            void runStream(trimmed);
        },
        [runStream],
    );

    const retryMessage = useCallback(
        (assistantMessageId: string) => {
            if (!sessionId) {
                return;
            }

            const assistantIndex = messages.findIndex((message) => message.id === assistantMessageId);
            if (assistantIndex <= 0) {
                return;
            }

            const userMessage = messages[assistantIndex - 1];
            if (userMessage.role !== 'user') {
                return;
            }

            void runStream(userMessage.content, assistantMessageId);
        },
        [messages, runStream, sessionId],
    );

    return {
        sendMessage,
        retryMessage,
        cancelStream,
        isStreaming,
    };
}
