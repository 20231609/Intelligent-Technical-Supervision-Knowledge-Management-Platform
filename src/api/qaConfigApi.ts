import type {
  KnowledgeBaseOption,
  QaConfig,
  RetrievalTestResult
} from "../types/qaConfig";
import request from "@/api/request";

export const getMockKnowledgeBaseList = (): KnowledgeBaseOption[] => [
  {
    id: "terms",
    name: "电力术语知识库",
    description: "覆盖设备、线路、调度等标准术语",
    documentCount: 328
  },
  {
    id: "supervision",
    name: "技术监督知识库",
    description: "覆盖缺陷判定、试验规程、监督规则",
    documentCount: 516
  },
  {
    id: "operation",
    name: "运行检修知识库",
    description: "覆盖运行规程、检修案例和处理建议",
    documentCount: 204
  }
];

export const getDefaultQaConfig = (): QaConfig => ({
  terminologyKnowledgeBaseId: "terms",
  supervisionKnowledgeBaseId: "supervision",
  topK: 6,
  similarityThreshold: 0.72,
  rerankThreshold: 0.65,
  llmApiUrl: "https://api.deepseek.com/v1/chat/completions",
  llmApiKey: "sk-demo-qa-management-key",
  llmModelName: "deepseek-chat",
  timeoutSeconds: 1200
});

export async function fetchQaConfig(): Promise<QaConfig> {
  const response = await request.get("/admin/qa-config");
  const data = response.data.data ?? {};
  return {
    terminologyKnowledgeBaseId: data.termKnowledgeBaseIds?.[0] ?? "terms",
    supervisionKnowledgeBaseId: data.technicalKnowledgeBaseIds?.[0] ?? "default",
    topK: data.topK ?? 6,
    similarityThreshold: data.similarityThreshold ?? 0.72,
    rerankThreshold: data.rerankThreshold ?? 0.65,
    llmApiUrl: data.llmApiUrl ?? "https://api.deepseek.com/v1/chat/completions",
    llmApiKey: data.llmApiKey ?? "",
    llmModelName: data.llmModelName ?? "deepseek-chat",
    timeoutSeconds: data.llmTimeoutSeconds ?? 30
  };
}

export async function saveQaConfig(config: QaConfig): Promise<QaConfig> {
  const response = await request.put("/admin/qa-config", {
    termKnowledgeBaseIds: [config.terminologyKnowledgeBaseId],
    technicalKnowledgeBaseIds: [config.supervisionKnowledgeBaseId],
    topK: config.topK,
    similarityThreshold: config.similarityThreshold,
    rerankThreshold: config.rerankThreshold,
    llmApiUrl: config.llmApiUrl,
    llmModelName: config.llmModelName,
    llmTimeoutSeconds: config.timeoutSeconds
  });
  const data = response.data.data ?? {};
  return {
    terminologyKnowledgeBaseId: data.termKnowledgeBaseIds?.[0] ?? config.terminologyKnowledgeBaseId,
    supervisionKnowledgeBaseId: data.technicalKnowledgeBaseIds?.[0] ?? config.supervisionKnowledgeBaseId,
    topK: data.topK ?? config.topK,
    similarityThreshold: data.similarityThreshold ?? config.similarityThreshold,
    rerankThreshold: data.rerankThreshold ?? config.rerankThreshold,
    llmApiUrl: data.llmApiUrl ?? config.llmApiUrl,
    llmApiKey: "",
    llmModelName: data.llmModelName ?? config.llmModelName,
    timeoutSeconds: data.llmTimeoutSeconds ?? config.timeoutSeconds
  };
}

export const runMockRetrievalTest = async (question: string): Promise<RetrievalTestResult[]> => {
  const response = await request.post("/search", {
    query: question.trim() || "变压器绕组温升异常如何判断",
    topK: 5
  });

  const rows = response.data.data?.results ?? [];
  return rows.map((item: any) => ({
    documentName: item.documentName,
    fragment: item.snippet,
    score: item.score,
    sourceType: item.knowledgeBaseId ?? "知识库"
  }));
};
