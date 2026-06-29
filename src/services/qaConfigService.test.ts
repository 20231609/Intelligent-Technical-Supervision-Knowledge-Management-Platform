import { describe, expect, it } from "vitest";
import {
  isManagerRole,
  maskApiKey,
  normalizeConfigPayload
} from "./qaConfigService";

describe("qaConfigService", () => {
  it("normalizes configuration before saving", () => {
    const result = normalizeConfigPayload({
      terminologyKnowledgeBaseId: " terms ",
      supervisionKnowledgeBaseId: " supervision ",
      topK: 3.8,
      similarityThreshold: 0.724,
      rerankThreshold: 0.653,
      llmApiUrl: " https://api.deepseek.com/v1/chat/completions ",
      llmApiKey: " sk-demo ",
      llmModelName: " deepseek-chat ",
      timeoutSeconds: 1200
    });

    expect(result).toEqual({
      terminologyKnowledgeBaseId: "terms",
      supervisionKnowledgeBaseId: "supervision",
      topK: 4,
      similarityThreshold: 0.72,
      rerankThreshold: 0.65,
      llmApiUrl: "https://api.deepseek.com/v1/chat/completions",
      llmApiKey: "sk-demo",
      llmModelName: "deepseek-chat",
      timeoutSeconds: 1200
    });
  });

  it("masks the api key while preserving the last characters", () => {
    expect(maskApiKey("sk-1234567890abcdef")).toBe("***************cdef");
  });

  it("allows only admin and super admin roles into management pages", () => {
    expect(isManagerRole("user")).toBe(false);
    expect(isManagerRole("admin")).toBe(true);
    expect(isManagerRole("super_admin")).toBe(true);
  });
});
