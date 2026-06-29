import { useState } from 'react';
import { Popover } from 'antd';
import type { CitationMarkerGroup } from '@/utils/citationContent';
import CitationDetailCard from '@/components/chat/CitationDetailCard';
import './CitationMarker.css';

interface CitationMarkerProps {
    group: CitationMarkerGroup;
}

function formatMarkerLabel(indices: number[]): string {
    if (indices.length === 1) {
        return String(indices[0]);
    }

    return String(indices[0]);
}

const CitationMarker = ({ group }: CitationMarkerProps) => {
    const [pinned, setPinned] = useState(false);
    const [hoverOpen, setHoverOpen] = useState(false);
    const label = formatMarkerLabel(group.markerIndices);
    const ariaLabel =
        group.markerIndices.length > 1
            ? `引用 ${group.markerIndices.join('、')}，来自 ${group.citations[0]?.documentName ?? '知识库文档'}`
            : `引用 ${label}，来自 ${group.citations[0]?.documentName ?? '知识库文档'}`;

    return (
        <Popover
            content={<CitationDetailCard citations={group.citations} />}
            trigger={pinned ? 'click' : ['hover', 'click']}
            open={pinned ? true : hoverOpen}
            onOpenChange={(open) => {
                if (pinned) {
                    if (!open) {
                        setPinned(false);
                    }
                    return;
                }

                setHoverOpen(open);
            }}
            mouseEnterDelay={0.15}
            mouseLeaveDelay={0.05}
            overlayClassName="citation-marker-popover"
            placement="top"
        >
            <button
                type="button"
                className="citation-marker"
                aria-label={ariaLabel}
                onClick={(event) => {
                    event.preventDefault();
                    event.stopPropagation();
                    setPinned(true);
                    setHoverOpen(false);
                }}
            >
                {label}
            </button>
        </Popover>
    );
};

export default CitationMarker;
