import type { Citation } from '@/types/chat';

const CITATION_MARKER_REGEX = /\[(\d+)\]/g;

export interface CitationMarkerGroup {
    markerIndices: number[];
    citations: Citation[];
    documentId: string;
}

export type MessageContentSegment =
    | { type: 'text'; value: string }
    | { type: 'citation'; group: CitationMarkerGroup };

function buildCitationMap(citations: Citation[]): Map<number, Citation> {
    const map = new Map<number, Citation>();
    for (const citation of citations) {
        map.set(citation.markerIndex, citation);
    }
    return map;
}

function createMarkerGroup(indices: number[], citationMap: Map<number, Citation>): CitationMarkerGroup | null {
    const citations = indices
        .map((index) => citationMap.get(index))
        .filter((item): item is Citation => Boolean(item));

    if (citations.length === 0) {
        return null;
    }

    return {
        markerIndices: indices,
        citations,
        documentId: citations[0].documentId,
    };
}

function mergeAdjacentCitationGroups(segments: MessageContentSegment[]): MessageContentSegment[] {
    const merged: MessageContentSegment[] = [];

    for (const segment of segments) {
        const previous = merged[merged.length - 1];

        if (
            segment.type === 'citation' &&
            previous?.type === 'citation' &&
            previous.group.documentId === segment.group.documentId
        ) {
            const combinedIndices = [...previous.group.markerIndices, ...segment.group.markerIndices];
            const combinedCitations = [...previous.group.citations, ...segment.group.citations];
            merged[merged.length - 1] = {
                type: 'citation',
                group: {
                    markerIndices: combinedIndices,
                    citations: combinedCitations,
                    documentId: previous.group.documentId,
                },
            };
            continue;
        }

        merged.push(segment);
    }

    return merged;
}

/**
 * Parse assistant content with [n] citation markers into render segments.
 * Adjacent markers referencing the same document are merged per product rules.
 */
export function parseMessageContentSegments(content: string, citations: Citation[]): MessageContentSegment[] {
    if (!content) {
        return [];
    }

    const citationMap = buildCitationMap(citations);
    const segments: MessageContentSegment[] = [];
    let lastIndex = 0;

    for (const match of content.matchAll(CITATION_MARKER_REGEX)) {
        const matchIndex = match.index ?? 0;
        const markerIndex = Number(match[1]);

        if (matchIndex > lastIndex) {
            segments.push({ type: 'text', value: content.slice(lastIndex, matchIndex) });
        }

        const group = createMarkerGroup([markerIndex], citationMap);
        if (group) {
            segments.push({ type: 'citation', group });
        }

        lastIndex = matchIndex + match[0].length;
    }

    if (lastIndex < content.length) {
        segments.push({ type: 'text', value: content.slice(lastIndex) });
    }

    if (segments.length === 0) {
        segments.push({ type: 'text', value: content });
    }

    return mergeAdjacentCitationGroups(segments);
}

/**
 * Append trailing citation markers when backend provides citations but no inline markers yet.
 */
export function appendTrailingCitationMarkers(content: string, citations: Citation[]): string {
    if (citations.length === 0 || /\[\d+\]/.test(content)) {
        return content;
    }

    const markers = citations
        .slice()
        .sort((left, right) => left.markerIndex - right.markerIndex)
        .map((citation) => `[${citation.markerIndex}]`)
        .join('');

    return `${content}${markers}`;
}

export function formatCitationBreadcrumb(citation: Citation): string {
    if (!citation.chapterPath) {
        return citation.documentName;
    }

    const chapter = citation.chapterPath.replace(/\s*\/\s*/g, ' > ');
    return `${citation.documentName} > ${chapter}`;
}

export function formatRelevanceLabel(citation: Citation): string {
    if (citation.relevanceScore !== undefined) {
        return `${Math.round(citation.relevanceScore * 100)}%`;
    }

    return String(citation.markerIndex);
}
