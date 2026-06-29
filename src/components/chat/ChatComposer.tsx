import { useState } from "react";
import { SendOutlined } from "@ant-design/icons";
import { Button, Input, Typography } from "antd";

import "./ChatComposer.css";

const { TextArea } = Input;

interface ChatComposerProps {
  disabled?: boolean;
  loading?: boolean;
  onSend: (content: string) => void;
}

const ChatComposer = ({ disabled = false, loading = false, onSend }: ChatComposerProps) => {
  const [draft, setDraft] = useState("");

  const handleSend = () => {
    const trimmed = draft.trim();
    if (!trimmed || disabled || loading) {
      return;
    }

    onSend(trimmed);
    setDraft("");
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-composer">
      <div className="chat-composer__input-wrap">
        <TextArea
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入你的问题...（Shift+Enter 换行，Enter 发送）"
          autoSize={{ minRows: 1, maxRows: 6 }}
          disabled={disabled || loading}
          className="chat-composer__textarea"
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSend}
          disabled={!draft.trim() || disabled || loading}
          loading={loading}
          className="chat-composer__send"
        >
          发送
        </Button>
      </div>
      <Typography.Text type="secondary" className="chat-composer__hint">
        Enter 发送，Shift + Enter 换行
      </Typography.Text>
    </div>
  );
};

export default ChatComposer;
