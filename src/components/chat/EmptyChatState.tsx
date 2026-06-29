import { CommentOutlined } from "@ant-design/icons";
import { Typography } from "antd";

import "./EmptyChatState.css";

export const QUICK_START_PROMPTS = [
  "介绍一下你能做什么",
  "帮我生成一份煤仓库存分析报告",
  "变压器绕组温升异常如何判断",
  "脱硫系统启动的基本条件有哪些",
  "请总结当前知识库中的关键流程",
  "如何排查常见配置问题"
] as const;

interface EmptyChatStateProps {
  onSelectPrompt: (prompt: string) => void;
}

const EmptyChatState = ({ onSelectPrompt }: EmptyChatStateProps) => {
  return (
    <div className="empty-chat-state">
      <div className="empty-chat-state__hero">
        <div className="empty-chat-state__icon" aria-hidden>
          <CommentOutlined />
        </div>
        <Typography.Title level={4} className="empty-chat-state__title">
          智能助手已就绪
        </Typography.Title>
        <Typography.Text type="secondary" className="empty-chat-state__description">
          你可以提问、检索知识库，或让系统辅助分析技术监督数据。
        </Typography.Text>
      </div>

      <div className="empty-chat-state__prompts">
        <Typography.Text className="empty-chat-state__prompts-label">快速开始：</Typography.Text>
        <div className="empty-chat-state__prompt-list">
          {QUICK_START_PROMPTS.map((prompt) => (
            <button
              key={prompt}
              type="button"
              className="empty-chat-state__prompt"
              onClick={() => onSelectPrompt(prompt)}
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default EmptyChatState;
