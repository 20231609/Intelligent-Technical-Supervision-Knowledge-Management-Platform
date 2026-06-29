import type {
    ChatStreamCitationPayload,
    ChatStreamEvent,
    ChatStreamOptions,
    ChatStreamRequest,
} from '@/types/chatStream';
import {
    buildDefaultMockAnswer,
    resolveMockScenario,
    type MockScenario,
} from '@/mocks/chatMockData';
import { buildMockThinkingSequence } from '@/mocks/thinkingStepsMock';

function wait(ms: number, signal?: AbortSignal): Promise<void> {
    return new Promise((resolve, reject) => {
        if (signal?.aborted) {
            reject(new DOMException('Aborted', 'AbortError'));
            return;
        }

        const timer = window.setTimeout(resolve, ms);
        signal?.addEventListener(
            'abort',
            () => {
                window.clearTimeout(timer);
                reject(new DOMException('Aborted', 'AbortError'));
            },
            { once: true },
        );
    });
}

function emit(event: ChatStreamEvent, onEvent: ChatStreamOptions['onEvent']): void {
    onEvent(event);
}

function resolveAnswer(content: string): { answer: string; scenario: MockScenario | null } {
    const scenario = resolveMockScenario(content);
    if (scenario) {
        return { answer: scenario.answer, scenario };
    }

    return { answer: buildDefaultMockAnswer(content), scenario: null };
}

/**
 * Mock implementation of POST /api/chat/stream SSE contract.
 * Replace with real EventSource/fetch stream when backend is ready.
 */
export async function mockStreamChatResponse(
    request: ChatStreamRequest,
    options: ChatStreamOptions,
): Promise<void> {
    const { sessionId, messageId, content } = request;
    const { signal, onEvent } = options;
    const { answer } = resolveAnswer(content);
    const thinkingSequence = buildMockThinkingSequence(content);

    for (const step of thinkingSequence) {
        await wait(step.status === 'running' ? 320 : 220, signal);
        emit(
            {
                event: 'thinking',
                data: {
                    messageId,
                    sessionId,
                    stepId: step.stepId,
                    label: step.label,
                    status: step.status,
                    icon: step.icon,
                    detail: step.detail,
                },
            },
            onEvent,
        );
    }

    await wait(160, signal);

    const citations = resolveMockScenario(content)?.citations ?? [
        {
            id: 'cite-mock-fallback-1',
            documentId: 'doc-mock-fallback-001',
            documentName: '技术监督知识库示例文档.pdf',
            chapterPath: '第三章 / 运行管理',
            snippet: '迎峰度夏期间应加强燃料库存监测与设备巡检，确保闭环检查项按期完成整改。',
            relevanceScore: 0.72,
            chunkType: 'paragraph',
        },
    ];

    for (let index = 0; index < citations.length; index += 1) {
        const citation = citations[index];
        const citationPayload: ChatStreamCitationPayload = {
            messageId,
            sessionId,
            citation: {
                ...citation,
                markerIndex: index + 1,
            },
        };
        emit({ event: 'citation', data: citationPayload }, onEvent);
        if (index < citations.length - 1) {
            await wait(80, signal);
        }
    }

    const chunkSize = 3;
    for (let index = 0; index < answer.length; index += chunkSize) {
        await wait(35, signal);
        emit(
            {
                event: 'token',
                data: {
                    messageId,
                    sessionId,
                    content: answer.slice(index, index + chunkSize),
                },
            },
            onEvent,
        );
    }

    emit(
        {
            event: 'done',
            data: { messageId, sessionId },
        },
        onEvent,
    );
}
