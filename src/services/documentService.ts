import { downloadDocument as downloadDocumentApi } from '@/api/documentApi';

const USE_MOCK_DOCUMENT = import.meta.env.VITE_USE_MOCK_STREAM !== 'false';

/**
 * Download source document by ID for citation tracing.
 */
export async function downloadSourceDocument(documentId: string, documentName: string): Promise<void> {
    if (USE_MOCK_DOCUMENT) {
        if (import.meta.env.DEV) {
            console.info('[mock] Download source document:', { documentId, documentName });
        }
        window.alert(`Mock 下载：${documentName}\n文档 ID：${documentId}`);
        return;
    }

    const blob = await downloadDocumentApi(documentId);
    const url = window.URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = documentName;
    anchor.click();
    window.URL.revokeObjectURL(url);
}
