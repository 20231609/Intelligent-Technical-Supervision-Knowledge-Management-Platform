import type { QaConfig, UserRole } from "../types/qaConfig";

const DECIMAL_PLACES = 2;

export const normalizeConfigPayload = (config: QaConfig): QaConfig => ({
  terminologyKnowledgeBaseId: config.terminologyKnowledgeBaseId.trim(),
  supervisionKnowledgeBaseId: config.supervisionKnowledgeBaseId.trim(),
  topK: Math.round(config.topK),
  similarityThreshold: Number(config.similarityThreshold.toFixed(DECIMAL_PLACES)),
  rerankThreshold: Number(config.rerankThreshold.toFixed(DECIMAL_PLACES)),
  llmApiUrl: config.llmApiUrl.trim(),
  llmApiKey: config.llmApiKey.trim(),
  llmModelName: config.llmModelName.trim(),
  timeoutSeconds: Math.round(config.timeoutSeconds)
});

export const maskApiKey = (apiKey: string): string => {
  const normalizedApiKey = apiKey.trim();

  if (normalizedApiKey.length <= 4) {
    return "*".repeat(normalizedApiKey.length);
  }

  return `${"*".repeat(normalizedApiKey.length - 4)}${normalizedApiKey.slice(-4)}`;
};

export const isManagerRole = (role: UserRole): boolean => {
  return role === "admin" || role === "super_admin";
};
