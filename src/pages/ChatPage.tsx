import { useEffect, useMemo } from "react";
import { RobotOutlined } from "@ant-design/icons";
import { Layout, Typography } from "antd";

import AppSidebar from "@/components/AppSidebar";
import ChatComposer from "@/components/chat/ChatComposer";
import ChatSidebar from "@/components/chat/ChatSidebar";
import EmptyChatState from "@/components/chat/EmptyChatState";
import MessageList from "@/components/chat/MessageList";
import { useChatSessions } from "@/hooks/useChatSessions";
import { useChatStream } from "@/hooks/useChatStream";
import { loadMessages } from "@/utils/chatStorage";

import "./ChatPage.css";

const ChatPage = () => {
  const {
    sessions,
    activeSessionId,
    activeMessages,
    createSession,
    switchSession,
    deleteSession,
    setSessionMessages,
    touchSession
  } = useChatSessions();

  const { sendMessage, retryMessage, cancelStream, isStreaming } = useChatStream({
    sessionId: activeSessionId,
    messages: activeMessages,
    setSessionMessages,
    touchSession
  });

  useEffect(() => {
    return () => {
      cancelStream();
    };
  }, [cancelStream]);

  const handleSwitchSession = (sessionId: string) => {
    cancelStream();
    switchSession(sessionId);
  };

  const handleCreateSession = () => {
    cancelStream();
    createSession();
  };

  const messageCountBySession = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const session of sessions) {
      if (session.id === activeSessionId) {
        counts[session.id] = activeMessages.length;
      } else {
        counts[session.id] = loadMessages(session.id).length;
      }
    }
    return counts;
  }, [activeMessages.length, activeSessionId, sessions]);

  const showEmptyState = activeMessages.length === 0;

  return (
    <Layout className="chat-shell">
      <AppSidebar />
      <div className="chat-page">
        <aside className="chat-page__sidebar-wrap">
          <ChatSidebar
            sessions={sessions}
            activeSessionId={activeSessionId}
            messageCountBySession={messageCountBySession}
            onCreateSession={handleCreateSession}
            onSwitchSession={handleSwitchSession}
            onDeleteSession={deleteSession}
          />
        </aside>

        <main className="chat-page__main">
          <header className="chat-page__header">
            <div>
              <Typography.Title level={4} className="chat-page__title">
                <RobotOutlined /> AI 智能助手
              </Typography.Title>
              <Typography.Text type="secondary">
                面向电力技术监督场景，支持知识库检索、思考过程展示和引用溯源。
              </Typography.Text>
            </div>
          </header>

          <div className="chat-page__body">
            {showEmptyState ? (
              <EmptyChatState onSelectPrompt={sendMessage} />
            ) : (
              <MessageList messages={activeMessages} onRetry={retryMessage} />
            )}
          </div>

          <ChatComposer loading={isStreaming} onSend={sendMessage} />
        </main>
      </div>
    </Layout>
  );
};

export default ChatPage;
