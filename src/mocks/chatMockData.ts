import type { ChatStreamCitationPayload } from '@/types/chatStream';

export interface MockCitation
    extends Omit<ChatStreamCitationPayload['citation'], 'markerIndex'> {}

export interface MockScenario {
    /** 精确匹配的用户问题（快捷提问等） */
    exactPrompts: string[];
    /** 关键词模糊匹配（任一命中即可） */
    keywords: string[];
    answer: string;
    citations: MockCitation[];
    thinkingDetails?: Partial<Record<'recall' | 'rerank' | 'generate', string>>;
}

export const MOCK_SCENARIOS: MockScenario[] = [
    {
        exactPrompts: ['介绍一下你自己'],
        keywords: ['你是谁', '介绍自己', '你能做什么'],
        answer: `您好！我是面向电力行业的智能问答助手，主要能力包括：

1. **知识检索**：基于技术监督、规程规范与术语知识库，快速定位相关条文与说明；
2. **智能问答**：结合 RAG 检索增强生成，给出有据可查的回答；
3. **引用溯源**：标注知识来源，支持查看原文片段并下载文档；
4. **多轮对话**：理解上下文，持续跟进您的问题。

您可以询问设备运行、规程条款、检查报告分析等专业问题，我会尽力为您提供准确、可追溯的解答[1]。`,
        citations: [
            {
                id: 'cite-mock-intro-1',
                documentId: 'doc-mock-sys-001',
                documentName: '智能问答系统使用说明.md',
                chapterPath: '第一章 / 产品概述',
                snippet: '本系统面向电力行业用户提供知识检索、智能问答与引用溯源能力，支持多轮对话与多会话管理。',
                relevanceScore: 0.95,
                chunkType: 'paragraph',
            },
        ],
        thinkingDetails: {
            recall: '未命中外部知识库，使用系统内置说明',
            generate: '组织产品介绍与能力说明',
        },
    },
    {
        exactPrompts: ['帮我写一下25年煤库存报告'],
        keywords: ['煤库存', '煤炭库存', '进耗存', '燃料库存报告'],
        answer: `根据知识库中的煤库存管理相关要求，**25年煤库存报告**建议按以下结构撰写[1]：

## 一、库存概况
- 报告期初、期末库存量及可用天数
- 各煤种（贫瘦煤、烟煤等）结构占比
- 与去年同期对比变化

## 二、进耗存分析
- 入厂煤量、耗煤量、库存变动趋势
- 主要供应商及运输通道情况
- 高峰时段保供措施落实情况

## 三、风险研判
- 低库存、结构失衡、接卸瓶颈等风险点
- 迎峰度夏 / 度冬期间供需预判

## 四、整改与建议
- 未闭环问题及整改计划
- 优化采购、调度、存储的建议措施[2]

如需，我可以基于您提供的实际数据，逐章生成详细正文内容。`,
        citations: [
            {
                id: 'cite-mock-coal-1',
                documentId: 'doc-mock-coal-001',
                documentName: '电厂燃料管理制度（2024版）.pdf',
                chapterPath: '第四章 / 库存管理',
                snippet: '电厂应建立燃料进、耗、存月报制度，报告内容须包括库存量、可用天数、煤种结构及风险分析，并报生产技术部备案。',
                relevanceScore: 0.94,
                chunkType: 'paragraph',
            },
            {
                id: 'cite-mock-coal-2',
                documentId: 'doc-mock-coal-002',
                documentName: '25年煤库存专项审计模板.docx',
                chapterPath: '第二节 / 报告提纲',
                snippet: '专项报告须涵盖进耗存分析、结构分析、保供风险研判及整改建议四个部分，并附关键数据图表。',
                relevanceScore: 0.89,
                chunkType: 'heading',
            },
        ],
        thinkingDetails: {
            recall: '命中燃料管理规范与报告模板 2 篇文档',
            rerank: '优先采用制度条文与审计模板章节',
        },
    },
    {
        exactPrompts: ['25年宝钢电厂迎峰度夏闭环检查数据如何?'],
        keywords: ['迎峰度夏', '闭环检查', '宝钢', '度夏检查'],
        answer: `根据知识库中迎峰度夏闭环检查相关材料，**25年宝钢电厂**检查数据可从以下维度汇总[1]：

| 指标 | 参考说明 |
|------|----------|
| 检查项总数 | 按专业分解（锅炉、汽机、电气、燃料等） |
| 已闭环项 | 整改完成并验收通过的数量及占比 |
| 在途整改 | 已制定计划但未完成的遗留项 |
| 重大问题 | 需上级督办或跨部门协调项 |

**重点关注方向：**
- 燃料库存与接卸能力是否满足高峰负荷需求[2]
- 主辅机运行可靠性及备用设备试验情况
- 应急预案演练与物资储备落实情况

建议调取《迎峰度夏闭环检查台账》获取分项得分与未完成项清单[3]，我可以帮您做进一步对比分析。`,
        citations: [
            {
                id: 'cite-mock-summer-1',
                documentId: 'doc-mock-summer-001',
                documentName: '迎峰度夏技术监督工作方案.pdf',
                chapterPath: '第三章 / 闭环检查要求',
                snippet: '迎峰度夏期间应开展闭环检查，检查内容包括燃料供应保障、设备运行状态、应急准备等，检查结果须形成台账并动态更新闭环状态。',
                relevanceScore: 0.93,
                chunkType: 'paragraph',
            },
            {
                id: 'cite-mock-summer-2',
                documentId: 'doc-mock-summer-002',
                documentName: '宝钢电厂25年迎峰度夏检查通报.docx',
                chapterPath: '附件一 / 数据统计表',
                snippet: '本期共检查项目 156 项，已闭环 142 项，闭环率 91.0%；遗留 14 项中燃料接卸能力提升 3 项、辅机检修延期 2 项为重点督办事项。',
                relevanceScore: 0.91,
                chunkType: 'table',
            },
            {
                id: 'cite-mock-summer-3',
                documentId: 'doc-mock-summer-003',
                documentName: '闭环检查评分细则.xlsx',
                chapterPath: 'Sheet1 / 评分标准',
                snippet: '闭环率低于 90% 的单位须提交专项整改方案，并在 15 个工作日内完成复核。',
                relevanceScore: 0.78,
                chunkType: 'table',
            },
        ],
        thinkingDetails: {
            recall: '跨技术监督库与检查报告库联合检索，召回 8 条',
            rerank: '筛选宝钢电厂及25年度相关片段',
        },
    },
    {
        exactPrompts: ['脱硝系统启动的基本条件有哪些'],
        keywords: ['脱硝', 'SCR', '脱硝启动', '氨喷射'],
        answer: `根据规程规范知识库，**脱硝（SCR）系统启动**前通常需满足以下基本条件[1]：

1. **烟气条件**：入口烟气温度达到催化剂活性区间（一般 320℃～420℃，以设备说明书为准）；
2. **吹灰与密封**：相关烟道吹灰完成，人孔门、阀门密封良好，无严重漏风；
3. **氨站就绪**：液氨/尿素制备及供应系统投运正常，喷氨格栅吹扫完毕；
4. **仪表与联锁**：NOx 分析仪、氨流量、温度等测点正常，联锁保护试验合格；
5. **辅机系统**：稀释风机、氨泵、搅拌器等辅机具备启动条件；
6. **环保要求**：当地环保部门允许投运，CEMS 数据正常上传。

实际启动前须对照本厂《脱硝系统运行规程》执行检查表，并完成值长许可[1][2]。`,
        citations: [
            {
                id: 'cite-mock-denox-1',
                documentId: 'doc-mock-denox-001',
                documentName: 'DL-T 335-2010 火电厂烟气脱硝技术规范.pdf',
                chapterPath: '第5章 / 5.1.1 / 基本要求',
                snippet: `## 5.1.1 基本要求

a) SCR 装置启动前，应确认烟气温度不低于催化剂最低投运温度；
b) 氨供应系统、稀释风系统、在线监测仪表均处于正常工作状态；
c) 喷氨格栅吹扫完毕，相关阀门位置正确。`,
                relevanceScore: 0.96,
                chunkType: 'paragraph',
            },
            {
                id: 'cite-mock-denox-2',
                documentId: 'doc-mock-denox-001',
                documentName: 'DL-T 335-2010 火电厂烟气脱硝技术规范.pdf',
                chapterPath: '第5章 / 5.2 / 启动前检查',
                snippet: `启动前检查表包括：烟道吹灰、氨站液位、喷氨格栅吹扫、CEMS 校准、联锁试验记录等 18 项内容，全部合格后方可申请投运。`,
                relevanceScore: 0.92,
                chunkType: 'list',
            },
        ],
        thinkingDetails: {
            recall: '术语库 + 规程规范库检索「脱硝启动」',
            rerank: '厂级规程优先于通用规范',
        },
    },
    {
        exactPrompts: ['请总结当前知识库中的关键流程'],
        keywords: ['知识库', '关键流程', '总结流程', 'RAG'],
        answer: `当前知识库支撑的智能问答流程可概括为以下关键环节：

**一、知识准备阶段**
- 文档上传 → 解析结构化 → 语义切分 → 向量化索引

**二、问答阶段**
- 用户提问 → 意图识别 → 多库联合召回 → 重排序 → 阈值过滤 → LLM 生成

**三、结果呈现**
- 流式输出回答
- 展示思考步骤（召回、重排、生成）
- 标注引用来源，支持原文追溯与下载

**四、运维配置**
- 管理员可配置术语库、技术监督库、Top K、相似度阈值等参数
- 支持检索体验测试验证召回效果

该流程确保回答既有时效反馈，又具备知识溯源能力[1]。`,
        citations: [
            {
                id: 'cite-mock-kb-1',
                documentId: 'doc-mock-kb-001',
                documentName: '智能知识管理与报告生成系统需求说明书.pdf',
                chapterPath: '第3章 / 知识问答',
                snippet: '系统应支持基于 RAG 的知识问答，检索支持跨多个知识库联合检索、语义向量检索及向量检索加重排序两种模式。',
                relevanceScore: 0.97,
                chunkType: 'paragraph',
            },
        ],
        thinkingDetails: {
            recall: '检索系统架构与需求文档',
            generate: '归纳流程为四阶段说明',
        },
    },
    {
        exactPrompts: ['如何排查常见配置问题'],
        keywords: ['配置问题', '排查', '配置错误', '连不上', 'API'],
        answer: `针对系统常见配置问题，建议按以下顺序排查：

**1. 大语言模型配置**
- 检查 API 地址、密钥、模型名称是否正确
- 确认网络可访问云端 API（如 SiliconFlow）
- 查看超时时间是否过短导致流式中断

**2. 知识问答模块配置**
- 术语库、技术监督库是否已正确选择
- Top K、相似度阈值、重排序阈值是否合理（过高会导致无召回）[1]

**3. 检索无结果**
- 文档是否已完成向量化（状态为「就绪」）
- 分段策略变更后是否触发重新处理

**4. 前端会话异常**
- 刷新后检查 localStorage 是否正常
- 流式过程中切换会话可能导致中断，需重新发送[2]

如能提供具体报错信息或配置截图，我可以给出更有针对性的建议。`,
        citations: [
            {
                id: 'cite-mock-config-1',
                documentId: 'doc-mock-config-001',
                documentName: '系统配置管理手册.md',
                chapterPath: '5.1 / 问答模块配置',
                snippet: '问答模块需配置术语知识库与技术监督知识库，并设置 Top K、相似度阈值与重排序阈值；配置变更即时生效，无需重启服务。',
                relevanceScore: 0.88,
                chunkType: 'paragraph',
            },
            {
                id: 'cite-mock-config-2',
                documentId: 'doc-mock-config-002',
                documentName: 'LLM接入配置说明.md',
                chapterPath: '2.3 / 常见问题',
                snippet: '若流式输出中断，请检查 API 密钥有效性、超时设置及服务端 SSE 连接是否被代理截断。',
                relevanceScore: 0.85,
                chunkType: 'paragraph',
            },
        ],
    },
    {
        exactPrompts: [],
        keywords: ['规程', '规范', '标准', '条款'],
        answer: `已在规程规范知识库中检索到相关内容。一般查询规程时建议：

- 明确标准编号或文件名称（如 DL/T、GB 标准）
- 说明适用设备类型与场景
- 如需对比多个版本，请标注年份

请补充更具体的关键词（例如「变压器检修规程」「继电保护整定」），我可以为您精确定位相关条文并附引用来源。`,
        citations: [
            {
                id: 'cite-mock-norm-1',
                documentId: 'doc-mock-norm-001',
                documentName: '规程规范知识库索引目录.pdf',
                chapterPath: '附录A / 分类说明',
                snippet: '规程规范类文档按专业分为锅炉、汽机、电气、热控、环保等类别，检索时可通过文档类型与标签组合过滤。',
                relevanceScore: 0.82,
                chunkType: 'paragraph',
            },
        ],
    },
    {
        exactPrompts: [],
        keywords: ['术语', '什么是', '含义', '定义'],
        answer: `已在术语知识库中检索相关词条。电力技术监督领域术语通常包含：

- **标准定义**：行业规范中的正式解释
- **适用范围**：适用的设备、参数或业务场景
- **关联术语**：上下游或易混淆概念

请提供完整术语名称，我将返回定义、来源文档及引用标注。`,
        citations: [
            {
                id: 'cite-mock-term-1',
                documentId: 'doc-mock-term-001',
                documentName: '电力技术监督术语汇编.pdf',
                chapterPath: '使用说明',
                snippet: '术语条目包含中英文名称、定义、来源标准及备注，支持按拼音、首字母及关键词检索。',
                relevanceScore: 0.86,
                chunkType: 'paragraph',
            },
        ],
    },
    {
        exactPrompts: [],
        keywords: ['你好', '谢谢', '再见', '早上好'],
        answer: `您好！很高兴为您服务。我是电力行业智能问答助手，可以帮您查阅规程规范、分析技术问题、解读检查报告要点等。

请问有什么可以帮您的？您也可以点击下方的快速提问开始对话。`,
        citations: [],
        thinkingDetails: {
            recall: '识别为一般对话意图，跳过知识库检索',
            generate: '生成友好回复',
        },
    },
];

export const MOCK_DEFAULT_ANSWER_PREFIX = '（Mock 回答）';

export function resolveMockScenario(userContent: string): MockScenario | null {
    const trimmed = userContent.trim();
    if (!trimmed) {
        return null;
    }

    const lower = trimmed.toLowerCase();

    for (const scenario of MOCK_SCENARIOS) {
        if (scenario.exactPrompts.some((prompt) => prompt === trimmed)) {
            return scenario;
        }
    }

    for (const scenario of MOCK_SCENARIOS) {
        if (scenario.keywords.some((keyword) => lower.includes(keyword.toLowerCase()))) {
            return scenario;
        }
    }

    return null;
}

export function buildDefaultMockAnswer(userContent: string): string {
    const trimmed = userContent.trim();
    return `${MOCK_DEFAULT_ANSWER_PREFIX}已收到您的问题：「${trimmed}」。

当前为前端 Mock 流式模式，后端就绪后将切换至真实 RAG 检索与生成。

**Mock 提示**：您可尝试以下类型的问题以获得更丰富的演示数据：
- 脱硝系统启动的基本条件有哪些
- 请总结当前知识库中的关键流程
- 如何排查常见配置问题
- 煤库存 / 迎峰度夏 / 规程规范 / 术语定义等相关关键词`;
}
