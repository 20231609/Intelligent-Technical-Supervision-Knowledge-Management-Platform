import type { ChatStreamEvent, ChatStreamEventName, ChatStreamOptions, ChatStreamRequest } from '@/types/chatStream';
import { ensureAuthToken } from '@/api/auth';
import { parseSseBuffer } from '@/utils/sseParser';

const CHAT_STREAM_URL = '/api/chat/stream';

const STREAM_EVENT_NAMES: ChatStreamEventName[] = ['token', 'thinking', 'citation', 'done', 'error'];

function isStreamEventName(value: string): value is ChatStreamEventName {
    return STREAM_EVENT_NAMES.includes(value as ChatStreamEventName);
}

async function buildAuthHeaders(): Promise<Record<string, string>> {
    const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        Accept: 'text/event-stream',
    };

    const token = await ensureAuthToken();
    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    return headers;
}

/**
 * POST /api/chat/stream
 * Raw SSE request. Business orchestration stays in services/chatService.ts.
 */
export async function postChatStream(
    body: ChatStreamRequest,
    options: ChatStreamOptions,
): Promise<void> {
    const response = await fetch(CHAT_STREAM_URL, {
        method: 'POST',
        headers: await buildAuthHeaders(),
        body: JSON.stringify(body),
        signal: options.signal,
    });

    if (!response.ok) {
        throw new Error(`聊天流式请求失败（HTTP ${response.status}）`);
    }

    if (!response.body) {
        throw new Error('聊天流式响应为空');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
        const { done, value } = await reader.read();
        if (done) {
            break;
        }

        buffer += decoder.decode(value, { stream: true });
        const parsed = parseSseBuffer(buffer);
        buffer = parsed.rest;

        for (const item of parsed.events) {
            if (!isStreamEventName(item.event)) {
                continue;
            }

            let payload: ChatStreamEvent['data'];
            try {
                payload = JSON.parse(item.data) as ChatStreamEvent['data'];
            } catch {
                continue;
            }

            options.onEvent({
                event: item.event,
                data: payload,
            });
        }
    }
}
