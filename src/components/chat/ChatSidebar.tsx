import { DeleteOutlined, MessageOutlined, PlusOutlined } from "@ant-design/icons";
import { Button, Modal, Typography } from "antd";

import type { ChatSession } from "@/types/chat";

import "./ChatSidebar.css";

interface ChatSidebarProps {
  sessions: ChatSession[];
  activeSessionId: string | null;
  messageCountBySession: Record<string, number>;
  onCreateSession: () => void;
  onSwitchSession: (sessionId: string) => void;
  onDeleteSession: (sessionId: string) => void;
}

function getSessionSubtitle(hasMessages: boolean): string {
  return hasMessages ? "点击查看历史消息" : "暂无消息";
}

interface ChatSidebarItemProps {
  session: ChatSession;
  isActive: boolean;
  hasMessages: boolean;
  onSwitch: () => void;
  onDelete: () => void;
}

function ChatSidebarItem({
  session,
  isActive,
  hasMessages,
  onSwitch,
  onDelete
}: ChatSidebarItemProps) {
  const handleDelete = (event: React.MouseEvent) => {
    event.stopPropagation();
    Modal.confirm({
      title: "删除对话",
      content: "确定删除该对话吗？删除后无法恢复。",
      okText: "删除",
      okType: "danger",
      cancelText: "取消",
      onOk: onDelete
    });
  };

  return (
    <button
      type="button"
      className={`chat-sidebar__item ${isActive ? "chat-sidebar__item--active" : ""}`}
      onClick={onSwitch}
    >
      <div className="chat-sidebar__item-main">
        <Typography.Text className="chat-sidebar__item-title" ellipsis>
          {session.title}
        </Typography.Text>
        <Typography.Text type="secondary" className="chat-sidebar__item-subtitle">
          {getSessionSubtitle(hasMessages)}
        </Typography.Text>
      </div>
      <Button
        type="text"
        size="small"
        icon={<DeleteOutlined />}
        aria-label={`删除对话 ${session.title}`}
        className="chat-sidebar__delete"
        onClick={handleDelete}
      />
    </button>
  );
}

const ChatSidebar = ({
  sessions,
  activeSessionId,
  messageCountBySession,
  onCreateSession,
  onSwitchSession,
  onDeleteSession
}: ChatSidebarProps) => {
  return (
    <aside className="chat-sidebar">
      <div className="chat-sidebar__header">
        <Typography.Title level={5} className="chat-sidebar__title">
          <MessageOutlined /> 对话历史
        </Typography.Title>
        <Button type="primary" icon={<PlusOutlined />} block onClick={onCreateSession}>
          新建对话
        </Button>
      </div>

      <div className="chat-sidebar__list">
        {sessions.length === 0 ? (
          <Typography.Text type="secondary" className="chat-sidebar__empty">
            暂无对话，点击上方按钮开始
          </Typography.Text>
        ) : (
          sessions.map((session) => (
            <ChatSidebarItem
              key={session.id}
              session={session}
              isActive={session.id === activeSessionId}
              hasMessages={(messageCountBySession[session.id] ?? 0) > 0}
              onSwitch={() => onSwitchSession(session.id)}
              onDelete={() => onDeleteSession(session.id)}
            />
          ))
        )}
      </div>
    </aside>
  );
};

export default ChatSidebar;
