import {
  CheckCircleOutlined,
  CloudSyncOutlined,
  EyeInvisibleOutlined,
  ReloadOutlined,
  SaveOutlined,
  SearchOutlined
} from "@ant-design/icons";
import {
  Alert,
  Button,
  Card,
  Col,
  Divider,
  Form,
  Input,
  InputNumber,
  Layout,
  List,
  Progress,
  Row,
  Select,
  Slider,
  Space,
  Tag,
  Typography,
  message
} from "antd";
import { useEffect, useMemo, useState } from "react";

import {
  fetchQaConfig,
  getDefaultQaConfig,
  getMockKnowledgeBaseList,
  runMockRetrievalTest,
  saveQaConfig
} from "@/api/qaConfigApi";
import AppSidebar from "@/components/AppSidebar";
import ManagementTabs from "@/components/ManagementTabs";
import StatusMetric from "@/components/StatusMetric";
import {
  isManagerRole,
  maskApiKey,
  normalizeConfigPayload
} from "@/services/qaConfigService";
import type { QaConfig, RetrievalTestResult, UserRole } from "@/types/qaConfig";

import "./AdminManagementPage.css";

const { Content } = Layout;
const { Text, Title } = Typography;

const currentUserRole: UserRole = "admin";

const AdminManagementPage = () => {
  const [form] = Form.useForm<QaConfig>();
  const [activeTabKey, setActiveTabKey] = useState("llm");
  const [isSaving, setIsSaving] = useState(false);
  const [retrievalQuestion, setRetrievalQuestion] = useState(
    "变压器绕组温升异常如何判断"
  );
  const [retrievalResults, setRetrievalResults] = useState<RetrievalTestResult[]>([]);
  const [isRetrieving, setIsRetrieving] = useState(false);

  const defaultConfig = useMemo(() => getDefaultQaConfig(), []);
  const knowledgeBaseList = useMemo(() => getMockKnowledgeBaseList(), []);
  const canManage = isManagerRole(currentUserRole);

  const knowledgeBaseOptions = knowledgeBaseList.map((item) => ({
    label: `${item.name}（${item.documentCount} 篇）`,
    value: item.id
  }));

  useEffect(() => {
    void fetchQaConfig()
      .then((config) => {
        form.setFieldsValue(config);
      })
      .catch(() => {
        form.setFieldsValue(defaultConfig);
      });
    void handleRunRetrievalTest();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSaveConfig = async () => {
    const values = await form.validateFields();
    const payload = normalizeConfigPayload(values);

    setIsSaving(true);
    try {
      const saved = await saveQaConfig(payload);
      form.setFieldsValue(saved);
      setIsSaving(false);
      message.success("配置已保存");
    } catch (error) {
      setIsSaving(false);
      message.error(error instanceof Error ? error.message : "配置保存失败");
    }
  };

  const handleRunRetrievalTest = async () => {
    setIsRetrieving(true);
    try {
      setRetrievalResults(await runMockRetrievalTest(retrievalQuestion));
    } catch (error) {
      message.error(error instanceof Error ? error.message : "检索失败");
    } finally {
      setIsRetrieving(false);
    }
  };

  return (
    <Layout className="adminPage">
      <AppSidebar />
      <Layout>
        <Content className="adminContent">
          <div className="pageHeader">
            <div>
              <Text type="secondary">系统设置 / 智能问答</Text>
              <Title level={2}>管理功能</Title>
            </div>
            <Space>
              <Tag color="blue">管理员可访问</Tag>
              <Tag color="cyan">运行时生效</Tag>
            </Space>
          </div>

          {!canManage ? (
            <Alert
              message="当前账号无管理权限"
              description="管理功能仅限管理员和超级管理员角色访问。"
              showIcon
              type="warning"
            />
          ) : null}

          <Row gutter={[16, 16]} className="metricRow">
            <Col xs={24} md={8}>
              <StatusMetric label="知识问答总次数" value="12,486" trend="近 30 天 +18%" />
            </Col>
            <Col xs={24} md={8}>
              <StatusMetric label="平均检索相关度" value="0.87" trend="较上周 +0.04" />
            </Col>
            <Col xs={24} md={8}>
              <StatusMetric label="配置项健康度" value="96%" trend="核心项已配置" />
            </Col>
          </Row>

          <Card
            className="managementCard"
            title={<ManagementTabs activeKey={activeTabKey} onChange={setActiveTabKey} />}
          >
            <Form
              disabled={!canManage}
              form={form}
              initialValues={defaultConfig}
              layout="vertical"
              requiredMark={false}
            >
              <section className="panelSection">
                <div className="sectionHeading">
                  <CloudSyncOutlined />
                  <div>
                    <Title level={4}>大模型配置</Title>
                    <Text type="secondary">
                      配置统一的 LLM 客户端，支持 OpenAI 兼容 chat-completions 接口。
                    </Text>
                  </div>
                </div>

                <Form.Item
                  label="API URL"
                  name="llmApiUrl"
                  rules={[{ required: true, message: "请输入模型 API 地址" }]}
                >
                  <Input placeholder="https://api.deepseek.com/v1/chat/completions" />
                </Form.Item>

                <Form.Item
                  label="API Key"
                  name="llmApiKey"
                  rules={[{ required: true, message: "请输入模型密钥" }]}
                >
                  <Input.Password iconRender={() => <EyeInvisibleOutlined />} />
                </Form.Item>

                <Text className="hintText" type="secondary">
                  留空表示不修改，当前已配置：{maskApiKey(defaultConfig.llmApiKey)}
                </Text>

                <Row gutter={16}>
                  <Col xs={24} lg={12}>
                    <Form.Item
                      label="模型名称"
                      name="llmModelName"
                      rules={[{ required: true, message: "请输入模型名称" }]}
                    >
                      <Input placeholder="deepseek-chat" />
                    </Form.Item>
                  </Col>
                  <Col xs={24} lg={12}>
                    <Form.Item
                      label="超时时间（秒）"
                      name="timeoutSeconds"
                      rules={[{ required: true, message: "请输入超时时间" }]}
                    >
                      <InputNumber min={30} max={3600} step={30} />
                    </Form.Item>
                  </Col>
                </Row>
              </section>

              <Divider />

              <section className="panelSection">
                <div className="sectionHeading">
                  <SearchOutlined />
                  <div>
                    <Title level={4}>知识问答配置</Title>
                    <Text type="secondary">
                      选择检索知识库，并调整 Top K、相似度阈值和重排序阈值。
                    </Text>
                  </div>
                </div>

                <Row gutter={16}>
                  <Col xs={24} lg={12}>
                    <Form.Item
                      label="术语知识库"
                      name="terminologyKnowledgeBaseId"
                      rules={[{ required: true, message: "请选择术语知识库" }]}
                    >
                      <Select options={knowledgeBaseOptions} />
                    </Form.Item>
                  </Col>
                  <Col xs={24} lg={12}>
                    <Form.Item
                      label="技术监督知识库"
                      name="supervisionKnowledgeBaseId"
                      rules={[{ required: true, message: "请选择技术监督知识库" }]}
                    >
                      <Select options={knowledgeBaseOptions} />
                    </Form.Item>
                  </Col>
                </Row>

                <Row gutter={16}>
                  <Col xs={24} lg={8}>
                    <Form.Item label="Top K" name="topK">
                      <InputNumber min={1} max={20} />
                    </Form.Item>
                  </Col>
                  <Col xs={24} lg={8}>
                    <Form.Item label="相似度阈值" name="similarityThreshold">
                      <Slider min={0} max={1} step={0.01} />
                    </Form.Item>
                  </Col>
                  <Col xs={24} lg={8}>
                    <Form.Item label="重排序阈值" name="rerankThreshold">
                      <Slider min={0} max={1} step={0.01} />
                    </Form.Item>
                  </Col>
                </Row>
              </section>
            </Form>

            <Divider />

            <section className="panelSection">
              <div className="sectionHeading">
                <CheckCircleOutlined />
                <div>
                  <Title level={4}>检索体验测试</Title>
                  <Text type="secondary">
                    验证知识库检索效果，检查召回片段与相关性分数。
                  </Text>
                </div>
              </div>

              <Space.Compact className="retrievalSearch">
                <Input
                  aria-label="检索测试问题"
                  value={retrievalQuestion}
                  onChange={(event) => setRetrievalQuestion(event.target.value)}
                />
                <Button icon={<SearchOutlined />} loading={isRetrieving} type="primary" onClick={handleRunRetrievalTest}>
                  测试检索
                </Button>
              </Space.Compact>

              <List
                className="retrievalList"
                dataSource={retrievalResults}
                renderItem={(item) => (
                  <List.Item>
                    <List.Item.Meta
                      title={
                        <Space>
                          <span>{item.documentName}</span>
                          <Tag>{item.sourceType}</Tag>
                        </Space>
                      }
                      description={item.fragment}
                    />
                    <Progress percent={Math.round(item.score * 100)} size="small" type="circle" />
                  </List.Item>
                )}
              />
            </section>

            <div className="actionBar">
              <Text type="secondary">配置修改会在保存后生效</Text>
              <Space>
                <Button icon={<ReloadOutlined />}>刷新</Button>
                <Button>放弃修改</Button>
                <Button
                  icon={<SaveOutlined />}
                  loading={isSaving}
                  onClick={handleSaveConfig}
                  type="primary"
                >
                  保存设置
                </Button>
              </Space>
            </div>
          </Card>
        </Content>
      </Layout>
    </Layout>
  );
};

export default AdminManagementPage;
