import type { Citation } from '@/types/chat';
import CitationMarker from '@/components/chat/CitationMarker';
import {
    appendTrailingCitationMarkers,
    parseMessageContentSegments,
} from '@/utils/citationContent';

interface MessageContentWithCitationsProps {
    content: string;
    citations?: Citation[];
    isStreaming?: boolean;
}

const MessageContentWithCitations = ({
    content,
    citations = [],
    isStreaming = false,
}: MessageContentWithCitationsProps) => {
    if (!content && isStreaming) {
        return <span className="message-bubble__placeholder">正在生成...</span>;
    }

    const normalizedContent = isStreaming
        ? content
        : appendTrailingCitationMarkers(content, citations);
    const segments = parseMessageContentSegments(normalizedContent, citations);

    return (
        <span className="message-bubble__rich-content">
            {segments.map((segment, index) => {
                if (segment.type === 'text') {
                    return (
                        <span key={`text-${index}`} className="message-bubble__text">
                            {segment.value}
                        </span>
                    );
                }

                return <CitationMarker key={`cite-${segment.group.documentId}-${index}`} group={segment.group} />;
            })}
        </span>
    );
};

export default MessageContentWithCitations;
