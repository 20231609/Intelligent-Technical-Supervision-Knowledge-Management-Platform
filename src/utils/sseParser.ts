/**
 * Parse Server-Sent Events text chunks from fetch streaming responses.
 */

export interface ParsedSseEvent {
    event: string;
    data: string;
}

export function parseSseBuffer(buffer: string): { events: ParsedSseEvent[]; rest: string } {
    const events: ParsedSseEvent[] = [];
    const blocks = buffer.split('\n\n');

    if (blocks.length === 0) {
        return { events, rest: buffer };
    }

    const rest = blocks.pop() ?? '';
    for (const block of blocks) {
        const lines = block.split('\n').filter(Boolean);
        let eventName = 'message';
        const dataLines: string[] = [];

        for (const line of lines) {
            if (line.startsWith('event:')) {
                eventName = line.slice(6).trim();
                continue;
            }

            if (line.startsWith('data:')) {
                dataLines.push(line.slice(5).trim());
            }
        }

        if (dataLines.length > 0) {
            events.push({ event: eventName, data: dataLines.join('\n') });
        }
    }

    return { events, rest };
}
