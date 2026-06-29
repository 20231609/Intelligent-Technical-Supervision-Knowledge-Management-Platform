import { useEffect, useState } from "react";
import { ReloadOutlined, UserOutlined } from "@ant-design/icons";
import { Button, Typography } from "antd";

import MessageContentWithCitations from "@/components/chat/MessageContentWithCitations";
import ThinkingSteps from "@/components/chat/ThinkingSteps";
import type { ChatMessage } from "@/types/chat";

import "./MessageBubble.css";

interface MessageBubbleProps {
  message: ChatMessage;
  onRetry?: (messageId: string) => void;
}

const MessageBubble = ({ message, onRetry }: MessageBubbleProps) => {
  const isUser = message.role === "user";
  const [thinkingExpanded, setThinkingExpanded] = useState(message.status === "streaming");

  useEffect(() => {
    if (message.status === "done") {
      setThinkingExpanded(false);
    }

    if (message.status === "streaming") {
      setThinkingExpanded(true);
    }
  }, [message.status]);

  return (
    <div
      className={`message-bubble-row ${
        isUser ? "message-bubble-row--user" : "message-bubble-row--assistant"
      }`}
    >
      {!isUser ? (
        <div className="message-bubble__avatar message-bubble__avatar--assistant" aria-hidden>
          AI
        </div>
      ) : null}

      <div className={`message-bubble ${isUser ? "message-bubble--user" : "message-bubble--assistant"}`}>
        {!isUser && message.thinkingSteps && message.thinkingSteps.length > 0 ? (
          <ThinkingSteps
            steps={message.thinkingSteps}
            expanded={thinkingExpanded}
            onToggle={() => setThinkingExpanded((previous) => !previous)}
            isStreaming={message.status === "streaming"}
          />
        ) : null}

        <div className="message-bubble__content">
          <MessageContentWithCitations
            content={message.content}
            citations={message.citations}
            isStreaming={message.status === "streaming"}
          />
        </div>

        {message.status === "failed" ? (
          <div className="message-bubble__error">
            <Typography.Text type="danger">{message.errorMessage ?? "生成失败"}</Typography.Text>
            {onRetry ? (
              <Button size="small" icon={<ReloadOutlined />} onClick={() => onRetry(message.id)}>
                重试
              </Button>
            ) : null}
          </div>
        ) : null}
      </div>

      {isUser ? (
        <div className="message-bubble__avatar message-bubble__avatar--user" aria-hidden>
          <UserOutlined />
        </div>
      ) : null}
    </div>
  );
};

export default MessageBubble;
