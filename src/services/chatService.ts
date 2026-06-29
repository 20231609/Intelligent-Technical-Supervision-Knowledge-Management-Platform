import { postChatStream } from '@/api/chatApi';
import type { ChatStreamOptions, ChatStreamRequest } from '@/types/chatStream';
import { mockStreamChatResponse } from '@/mocks/chatStreamMock';

const USE_MOCK_STREAM = import.meta.env.VITE_USE_MOCK_STREAM === 'true';

/**
 * Stream chat response.
 * - Mock mode: src/mocks/chatStreamMock.ts (default in development)
 * - Real API: POST /api/chat/stream via src/api/chatApi.ts
 */
export async function streamChatResponse(
    request: ChatStreamRequest,
    options: ChatStreamOptions,
): Promise<void> {
    if (USE_MOCK_STREAM) {
        return mockStreamChatResponse(request, options);
    }

    return postChatStream(request, options);
}
