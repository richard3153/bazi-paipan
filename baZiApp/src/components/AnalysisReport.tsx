import React, { useState } from 'react';
import { Card, Collapse, Typography, Tag, Space, Divider, Button } from 'antd';
import { BookOutlined, DownOutlined, UpOutlined } from '@ant-design/icons';
import { useAppStore } from '@/store/appStore';
import { AnalysisReport } from '@/types/bazi';

const { Text, Title, Paragraph } = Typography;
const { Panel } = Collapse;

// 解读报告组件
const AnalysisReportComponent: React.FC = () => {
  const { result } = useAppStore();
  const [activePanels, setActivePanels] = useState<string[]>(['overview']);
  
  if (!result) return null;
  
  const { analysis } = result;
  
  // 报告章节配置
  const reportSections = [
    {
      key: 'overview',
      title: '📊 总体概述',
      content: analysis.overview,
      color: '#1890ff'
    },
    {
      key: 'dayMaster',
      title: '🎯 日主分析',
      content: analysis.dayMasterAnalysis,
      color: '#52c41a'
    },
    {
      key: 'wuxing',
      title: '⚖️ 五行分析',
      content: analysis.wuxingAnalysis,
      color: '#faad14'
    },
    {
      key: 'shishen',
      title: '🔮 十神分析',
      content: analysis.shishenAnalysis,
      color: '#722ed1'
    },
    {
      key: 'wealth',
      title: '💰 财运分析',
      content: analysis.wealth,
      color: '#f5222d'
    },
    {
      key: 'career',
      title: '💼 事业分析',
      content: analysis.career,
      color: '#13c2c2'
    },
    {
      key: 'health',
      title: '🏥 健康分析',
      content: analysis.health,
      color: '#eb2f96'
    },
    {
      key: 'marriage',
      title: '💑 婚姻分析',
      content: analysis.marriage,
      color: '#fa8c16'
    },
    {
      key: 'education',
      title: '📚 学业分析',
      content: analysis.education,
      color: '#2f54eb'
    }
  ];
  
  // 展开/折叠所有
  const expandAll = () => {
    setActivePanels(reportSections.map(s => s.key));
  };
  
  const collapseAll = () => {
    setActivePanels([]);
  };
  
  return (
    <Card
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <BookOutlined />
          <span>命理解读报告</span>
        </div>
      }
      extra={
        <Space>
          <Button size="small" onClick={expandAll}>
            展开全部
          </Button>
          <Button size="small" onClick={collapseAll}>
            折叠全部
          </Button>
        </Space>
      }
      style={{ marginBottom: 24 }}
    >
      {/* 建议列表 */}
      {analysis.suggestions && analysis.suggestions.length > 0 && (
        <Card
          size="small"
          style={{ marginBottom: 16, background: '#f6ffed', border: '1px solid #b7eb8f' }}
          bodyStyle={{ padding: '16px' }}
        >
          <Title level={5} style={{ color: '#52c41a', marginBottom: 12 }}>
            💡 改善建议
          </Title>
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            {analysis.suggestions.map((suggestion, index) => (
              <li key={index} style={{ marginBottom: 4 }}>
                <Text>{suggestion}</Text>
              </li>
            ))}
          </ul>
        </Card>
      )}
      
      {/* 详细分析报告 */}
      <Collapse
        activeKey={activePanels}
        onChange={(keys) => setActivePanels(keys as string[])}
        expandIcon={({ isActive }) => (
          <DownOutlined rotate={isActive ? 180 : 0} />
        )}
      >
        {reportSections.map(section => (
          <Panel
            key={section.key}
            header={
              <span style={{ color: section.color, fontWeight: 500 }}>
                {section.title}
              </span>
            }
          >
            <Paragraph
              style={{
                margin: 0,
                lineHeight: 1.8,
                color: '#333',
                textAlign: 'justify'
              }}
            >
              {section.content}
            </Paragraph>
          </Panel>
        ))}
      </Collapse>
      
      {/* 免责声明 */}
      <Divider style={{ margin: '24px 0 16px' }} />
      <Paragraph
        type="secondary"
        style={{
          fontSize: 12,
          textAlign: 'center',
          margin: 0
        }}
      >
        ⚠️ 免责声明：本解读仅供参考娱乐，不构成任何专业建议。命运掌握在自己手中，请理性看待。
      </Paragraph>
    </Card>
  );
};

export default AnalysisReportComponent;
