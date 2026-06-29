export type UserRole = "user" | "admin" | "super_admin";

export type KnowledgeBaseOption = {
  id: string;
  name: string;
  description: string;
  documentCount: number;
};

export type QaConfig = {
  terminologyKnowledgeBaseId: string;
  supervisionKnowledgeBaseId: string;
  topK: number;
  similarityThreshold: number;
  rerankThreshold: number;
  llmApiUrl: string;
  llmApiKey: string;
  llmModelName: string;
  timeoutSeconds: number;
};

export type RetrievalTestResult = {
  documentName: string;
  fragment: string;
  score: number;
  sourceType: "术语库" | "技术监督库" | "运行检修库";
};
