import { useEffect, useRef } from 'react';
import type { ChatMessage } from '@/types/chat';
import MessageBubble from '@/components/chat/MessageBubble';
import './MessageList.css';

interface MessageListProps {
    messages: ChatMessage[];
    onRetry?: (messageId: string) => void;
}

const SCROLL_THRESHOLD = 80;

const MessageList = ({ messages, onRetry }: MessageListProps) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const shouldAutoScrollRef = useRef(true);

    useEffect(() => {
        const container = containerRef.current;
        if (!container || !shouldAutoScrollRef.current) {
            return;
        }

        container.scrollTop = container.scrollHeight;
    }, [messages]);

    const handleScroll = () => {
        const container = containerRef.current;
        if (!container) {
            return;
        }

        const distanceToBottom = container.scrollHeight - container.scrollTop - container.clientHeight;
        shouldAutoScrollRef.current = distanceToBottom <= SCROLL_THRESHOLD;
    };

    return (
        <div ref={containerRef} className="message-list" onScroll={handleScroll}>
            {messages.map((message) => (
                <MessageBubble key={message.id} message={message} onRetry={onRetry} />
            ))}
        </div>
    );
};

export default MessageList;
