import type { ChatStreamThinkingPayload } from "@/types/chatStream";

export type MockThinkingStepTemplate = Omit<ChatStreamThinkingPayload, "messageId" | "sessionId">;

function trimQuestion(content: string, maxLength = 28): string {
  const trimmed = content.trim();
  if (trimmed.length <= maxLength) {
    return trimmed;
  }

  return `${trimmed.slice(0, maxLength)}...`;
}

export function buildMockThinkingSequence(userContent: string): MockThinkingStepTemplate[] {
  const question = trimQuestion(userContent);

  return [
    { stepId: "intent-analyze", icon: "1", label: "正在分析问题意图...", status: "running" },
    { stepId: "intent-route", icon: "2", label: "识别为：知识问答", status: "done" },
    { stepId: "term-recall-start", icon: "3", label: "正在检索术语库...", status: "running" },
    { stepId: "term-recall-done", icon: "4", label: "术语召回完成，找到 3 个可用标签", status: "done" },
    { stepId: "rewrite-start", icon: "5", label: "正在改写问题并匹配术语...", status: "running" },
    { stepId: "rewrite-done", icon: "6", label: `改写完成：${question}`, status: "done" },
    { stepId: "kb-recall-start", icon: "7", label: "正在检索技术监督知识库...", status: "running" },
    { stepId: "kb-recall-done", icon: "8", label: "技术监督知识库召回完成", status: "done" },
    { stepId: "generate-start", icon: "9", label: "正在生成回答...", status: "running" },
    { stepId: "generate-done", icon: "10", label: "回答生成完成", status: "done" }
  ];
}
