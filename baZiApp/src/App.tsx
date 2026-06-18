import React from 'react';
import { useAppStore } from '@/store/appStore';
import InputForm from '@/components/InputForm';
import ResultPage from '@/pages/ResultPage';
import { Layout, Typography, Space } from 'antd';
import { ThunderboltOutlined } from '@ant-design/icons';

const { Header, Content, Footer } = Layout;
const { Title, Text } = Typography;

const App: React.FC = () => {
  const { activeTab } = useAppStore();
  
  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* 头部 */}
      <Header
        style={{
          background: '#fff',
          padding: '0 24px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}
      >
        <Space align="center">
          <ThunderboltOutlined style={{ fontSize: 24, color: '#1890ff' }} />
          <Title level={4} style={{ margin: 0, color: '#1890ff' }}>
            四柱八字排盘系统
          </Title>
        </Space>
        <Text type="secondary">专业的命理分析工具</Text>
      </Header>
      
      {/* 内容区 */}
      <Content style={{ padding: '24px', background: '#f0f2f5' }}>
        {activeTab === 'input' ? <InputForm /> : <ResultPage />}
      </Content>
      
      {/* 页脚 */}
      <Footer style={{ textAlign: 'center', background: '#fff' }}>
        <Text type="secondary">
          ©2024 四柱八字排盘系统 | 本工具仅供娱乐参考
        </Text>
      </Footer>
    </Layout>
  );
};

export default App;
