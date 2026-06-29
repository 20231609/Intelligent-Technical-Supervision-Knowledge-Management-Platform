import {
  ApiOutlined,
  BookOutlined,
  DatabaseOutlined,
  FileSearchOutlined,
  NodeIndexOutlined,
  RobotOutlined,
  SettingOutlined
} from "@ant-design/icons";
import { Tabs } from "antd";

type ManagementTabsProps = {
  activeKey: string;
  onChange: (activeKey: string) => void;
};

const ManagementTabs = ({ activeKey, onChange }: ManagementTabsProps) => {
  return (
    <Tabs
      activeKey={activeKey}
      className="managementTabs"
      onChange={onChange}
      items={[
        { key: "llm", label: "大模型配置", icon: <RobotOutlined /> },
        { key: "embedding", label: "嵌入模型", icon: <DatabaseOutlined /> },
        { key: "rerank", label: "重排序模型", icon: <NodeIndexOutlined /> },
        { key: "parser", label: "文档解析器", icon: <FileSearchOutlined /> },
        { key: "material", label: "材料解析", icon: <BookOutlined /> },
        { key: "qa", label: "知识问答", icon: <ApiOutlined /> },
        { key: "digital", label: "数字人设置", icon: <SettingOutlined /> }
      ]}
    />
  );
};

export default ManagementTabs;
