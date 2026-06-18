import React from 'react';
import { Tabs } from 'antd';
import { useAppStore } from '@/store/appStore';
import SiZhuDisplay from '@/components/SiZhuDisplay';
import WuXingDistribution from '@/components/WuXingDistribution';
import AnalysisReportComponent from '@/components/AnalysisReport';
import LiuNianAnalysis from '@/components/LiuNianAnalysis';
import { Button, Result, Spin } from 'antd';
import { ArrowLeftOutlined, ThunderboltOutlined, BarChartOutlined, LineChartOutlined, FileTextOutlined } from '@ant-design/icons';

// 结果页面
const ResultPage: React.FC = () => {
  const { result, loading, error, setActiveTab } = useAppStore();
  
  // 加载中
  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16, fontSize: 16, color: '#666' }}>
          正在排盘，请稍候...
        </div>
      </div>
    );
  }
  
  // 错误
  if (error && !result) {
    return (
      <Result
        status="error"
        title="排盘失败"
        subTitle={error}
        extra={
          <Button
            type="primary"
            key="retry"
            onClick={() => setActiveTab('input')}
          >
            返回重新输入
          </Button>
        }
      />
    );
  }
  
  // 无结果
  if (!result) {
    return (
      <Result
        status="info"
        title="暂无排盘结果"
        subTitle="请先输入信息并进行排盘"
        extra={
          <Button
            type="primary"
            key="input"
            onClick={() => setActiveTab('input')}
          >
            去排盘
          </Button>
        }
      />
    );
  }
  
  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '20px' }}>
      {/* 返回按钮 */}
      <Button
        type="link"
        icon={<ArrowLeftOutlined />}
        onClick={() => setActiveTab('input')}
        style={{ marginBottom: 16 }}
      >
        返回重新排盘
      </Button>
      
      {/* 用户信息摘要 */}
      <div
        style={{
          background: '#fafafa',
          padding: '16px',
          borderRadius: 8,
          marginBottom: 24
        }}
      >
        <h3 style={{ margin: 0 }}>
          {result.input.name}（{result.input.gender}）
        </h3>
        <div style={{ color: '#666', marginTop: 4 }}>
          出生: {result.input.birthDate} {result.input.birthTime} | 地点: {result.input.birthPlace}
        </div>
      </div>
      
      {/* Tab切换视图 */}
      <Tabs
        defaultActiveKey="sizhu"
        size="large"
        style={{ marginBottom: 24 }}
        items={[
          {
            key: 'sizhu',
            label: (
              <span>
                <ThunderboltOutlined />
                四柱排盘
              </span>
            ),
            children: (
              <div>
                <SiZhuDisplay />
              </div>
            )
          },
          {
            key: 'dayun',
            label: (
              <span>
                <LineChartOutlined />
                大运流年
              </span>
            ),
            children: (
              <div>
                <LiuNianAnalysis />
              </div>
            )
          },
          {
            key: 'wuxing',
            label: (
              <span>
                <BarChartOutlined />
                五行分析
              </span>
            ),
            children: (
              <div>
                <WuXingDistribution />
              </div>
            )
          },
          {
            key: 'analysis',
            label: (
              <span>
                <FileTextOutlined />
                解读报告
              </span>
            ),
            children: (
              <div>
                <AnalysisReportComponent />
              </div>
            )
          }
        ]}
      />
    </div>
  );
};

export default ResultPage;
