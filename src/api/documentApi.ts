import request from '@/api/request';

/**
 * GET /api/document/{documentId}/download
 * Download original knowledge-base document for citation tracing.
 */
export async function downloadDocument(documentId: string): Promise<Blob> {
    const response = await request.get<Blob>(`/document/${documentId}/download`, {
        responseType: 'blob',
    });

    return response.data;
}
