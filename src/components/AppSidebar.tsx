import {
  AppstoreOutlined,
  BookOutlined,
  FileTextOutlined,
  FolderOpenOutlined,
  MessageOutlined,
  SafetyCertificateOutlined,
  SettingOutlined,
  TeamOutlined,
  UserOutlined
} from "@ant-design/icons";
import { Layout, Menu, Typography } from "antd";
import { useLocation, useNavigate } from "react-router-dom";

import "./AppSidebar.css";

const { Sider } = Layout;
const { Text } = Typography;

const AppSidebar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const selectedKey = location.pathname.startsWith("/admin") ? "system-setting" : "chat";

  return (
    <Sider className="appSidebar" width={184}>
      <div className="appSidebarLogo">
        <AppstoreOutlined />
        <Text strong>智能问答</Text>
      </div>
      <Menu
        mode="inline"
        selectedKeys={[selectedKey]}
        defaultOpenKeys={["system", "rag"]}
        onClick={({ key }) => {
          if (key === "chat") {
            navigate("/chat");
          }
          if (key === "system-setting") {
            navigate("/admin/settings");
          }
        }}
        items={[
          {
            key: "chat",
            icon: <MessageOutlined />,
            label: "智能对话"
          },
          {
            key: "system",
            icon: <SettingOutlined />,
            label: "系统管理",
            children: [
              { key: "user", icon: <UserOutlined />, label: "用户管理" },
              { key: "role", icon: <TeamOutlined />, label: "角色管理" },
              {
                key: "permission",
                icon: <SafetyCertificateOutlined />,
                label: "权限管理"
              },
              { key: "report", icon: <FileTextOutlined />, label: "报告类别" },
              { key: "file", icon: <FolderOpenOutlined />, label: "文件管理" }
            ]
          },
          {
            key: "rag",
            icon: <BookOutlined />,
            label: "RAG 知识库",
            children: [
              { key: "knowledge-manage", label: "知识管理" },
              { key: "knowledge-experience", label: "知识体验" }
            ]
          },
          {
            key: "system-setting",
            icon: <SettingOutlined />,
            label: "系统设置"
          }
        ]}
      />
    </Sider>
  );
};

export default AppSidebar;
