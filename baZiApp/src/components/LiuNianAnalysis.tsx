import React, { useState, useMemo } from 'react';
import { Card, Row, Col, Tag, Typography, Table, Button, Tabs, Collapse, Alert, Tooltip, Rate } from 'antd';
import { CalendarOutlined, BookOutlined, WarningOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { useAppStore } from '@/store/appStore';
import { 
  DaYun, 
  LiuNian, 
  XiaoYun, 
  TongYun, 
  TianGan, 
  DiZhi, 
  ShiShen,
  WangShuai,
  NaYin
} from '@/types/bazi';
import { 
  calculateDaYun,
  calculateLiuNian,
  calculateXiaoYun,
  calculateTongYun,
  calculateShenSha,
  calculateWangShuai,
  NaYin as NaYinUtil,
  getWuxingColorProfessional
} from '@/utils/bazi';
import {
  interpretDaYun,
  interpretLiuNian,
  interpretXiaoYun,
  interpretTongYun,
  ClassicQuote,
  DaYunInterpretation,
  LiuNianInterpretation,
  MonthFortune
} from '@/utils/bazi_interpreter';

const { Text, Title, Paragraph } = Typography;

// 大运流年分析组件
const LiuNianAnalysis: React.FC = () => {
  const { result } = useAppStore();
  const [selectedDayun, setSelectedDayun] = useState<number>(0);
  const [selectedLiuNian, setSelectedLiuNian] = useState<number | null>(null);
  
  if (!result || !result.sizhu) return null;
  
  const { sizhu, dayMaster, input } = result;
  const gender = input.gender;
  const birthDate = input.birthDate;
  
  // 计算日主强弱（简化）
  const dayMasterStrength = '身旺'; // 实际应根据原局计算
  
  const [birthHour, birthMinute] = input.birthTime ? input.birthTime.split(':').map(Number) : [0, 0];
  const birthYear = new Date(birthDate).getFullYear();

  // 计算大运
  const daYunList = calculateDaYun(birthDate, gender, sizhu.month, dayMaster);
  
  // 当前选中的大运
  const currentDaYun = daYunList[selectedDayun];
  
  // 计算当前大运的流年
  const liuNianList = currentDaYun ? 
    calculateLiuNian(currentDaYun.startYear, currentDaYun.endYear, dayMaster) : 
    [];
  
  // 计算小运
  const currentYear = new Date().getFullYear();
  const xiaoYun = calculateXiaoYun(birthDate, currentYear, birthHour, birthMinute);
  
  // 计算童运
  const tongYunList = calculateTongYun(birthDate, gender, dayMaster);
  
  // 大运解读
  const currentDaYunInterpretation = useMemo(() => {
    if (!currentDaYun) return null;
    return interpretDaYun(currentDaYun, dayMaster, dayMasterStrength, sizhu);
  }, [currentDaYun, dayMaster, dayMasterStrength, sizhu]);
  
  // 选中的流年解读
  const selectedLiuNianInterpretation = useMemo(() => {
    if (selectedLiuNian === null || !currentDaYun) return null;
    const liunian = liuNianList[selectedLiuNian];
    if (!liunian) return null;
    return interpretLiuNian(liunian, currentDaYun, dayMaster, dayMasterStrength, sizhu);
  }, [selectedLiuNian, liuNianList, currentDaYun, dayMaster, dayMasterStrength, sizhu]);
  
  // 小运解读
  const xiaoYunInterpretation = useMemo(() => {
    return interpretXiaoYun(xiaoYun, dayMaster, sizhu);
  }, [xiaoYun, dayMaster, sizhu]);
  
  // 辅助函数：获取天干五行
  function getWuxing(gan: string): '金' | '木' | '水' | '火' | '土' {
    const map: Record<string, '金' | '木' | '水' | '火' | '土'> = {
      '甲': '木', '乙': '木',
      '丙': '火', '丁': '火',
      '戊': '土', '己': '土',
      '庚': '金', '辛': '金',
      '壬': '水', '癸': '水'
    };
    return map[gan] || '木';
  }
    
  // 辅助函数：获取地支五行
  function getWuxingDiZhi(zhi: string): '金' | '木' | '水' | '火' | '土' {
    const map: Record<string, '金' | '木' | '水' | '火' | '土'> = {
      '子': '水', '丑': '土', '寅': '木', '卯': '木',
      '辰': '土', '巳': '火', '午': '火', '未': '土',
      '申': '金', '酉': '金', '戌': '土', '亥': '水'
    };
    return map[zhi] || '土';
  }
  
  // 大运表格列定义
  const daYunColumns = [
    {
      title: '十神',
      dataIndex: 'shishen',
      key: 'shishen',
      render: (text: string) => <Tag color="purple">{text}</Tag>
    },
    {
      title: '大运',
      dataIndex: 'dayun',
      key: 'dayun',
      render: (text: string, record: any) => (
        <Button
          type={selectedDayun === record.index ? 'primary' : 'default'}
          size="small"
          onClick={() => {
            setSelectedDayun(record.index);
            setSelectedLiuNian(null);
          }}
          style={{ fontWeight: selectedDayun === record.index ? 'bold' : 'normal' }}
        >
          {text}
        </Button>
      )
    },
    {
      title: '年龄',
      dataIndex: 'age',
      key: 'age'
    }
  ];
  
  // 大运数据
  const daYunData = daYunList.map((dy, idx) => ({
    key: idx,
    index: idx,
    shishen: dy.shishen,
    dayun: `${dy.tiangan}${dy.dizhi}`,
    age: `${dy.startAge}岁-${dy.endAge}岁`
  }));
  
  // 流年表格列定义
  const liuNianColumns = [
    {
      title: '流年',
      dataIndex: 'year',
      key: 'year',
      width: 80
    },
    {
      title: '天干',
      dataIndex: 'tiangan',
      key: 'tiangan',
      render: (text: string) => {
        const color = getWuxingColorProfessional(getWuxing(text));
        return <span style={{ color, fontWeight: 'bold' }}>{text}</span>;
      }
    },
    {
      title: '地支',
      dataIndex: 'dizhi',
      key: 'dizhi',
      render: (text: string) => {
        const color = getWuxingColorProfessional(getWuxingDiZhi(text));
        return <span style={{ color }}>{text}</span>;
      }
    },
    {
      title: '十神',
      dataIndex: 'shishen',
      key: 'shishen',
      render: (text: string) => <Tag color="blue">{text}</Tag>
    },
    {
      title: '操作',
      key: 'action',
      render: (text: string, record: any) => (
        <Button
          type="link"
          size="small"
          onClick={() => setSelectedLiuNian(record.index)}
        >
          详情
        </Button>
      )
    }
  ];
  
  // 流年数据
  const liuNianData = liuNianList.map((ln, idx) => ({
    key: idx,
    index: idx,
    year: ln.year,
    tiangan: ln.tiangan,
    dizhi: ln.dizhi,
    shishen: ln.shishen
  }));
  
  // 渲染大运解读
  const renderDaYunInterpretation = () => {
    if (!currentDaYunInterpretation) return null;
    const interp = currentDaYunInterpretation;
    
    return (
      <Card
        title={
          <span>
            <BookOutlined /> 当前大运解读
          </span>
        }
        style={{ marginBottom: 24, borderColor: '#1890ff' }}
      >
        {/* 大运基本信息 */}
        <div style={{ marginBottom: 16 }}>
          <Title level={5}>
            第{selectedDayun + 1}步大运：{currentDaYun.tiangan}{currentDaYun.dizhi}
            （{currentDaYun.startYear}-{currentDaYun.endYear}，
            {currentDaYun.startAge}-{currentDaYun.endAge}岁）
          </Title>
          <Tag color="purple" style={{ fontSize: 14, padding: '4px 12px' }}>
            十神：{interp.dayun.shishen}
          </Tag>
        </div>
        
        {/* 经典解读 */}
        {interp.classicQuotes.length > 0 && (
          <div style={{ marginBottom: 16 }}>
            <Title level={5}>
              <BookOutlined /> 经典解读
            </Title>
            {interp.classicQuotes.map((quote: ClassicQuote, idx: number) => (
              <div
                key={idx}
                style={{
                  background: '#f6ffed',
                  border: '1px solid #b7eb8f',
                  borderRadius: 6,
                  padding: '12px',
                  marginBottom: 8
                }}
              >
                <Text strong style={{ color: '#389e0d' }}>
                  【《{quote.book}》】
                </Text>
                <Paragraph style={{ margin: '8px 0', fontStyle: 'italic' }}>
                  {quote.quote}
                </Paragraph>
                <Paragraph style={{ margin: 0, color: '#666' }}>
                  → {quote.explanation}
                </Paragraph>
              </div>
            ))}
          </div>
        )}
        
        {/* 五行与十神分析 */}
        <div style={{ marginBottom: 16 }}>
          <Title level={5}>📊 运势分析</Title>
          <Row gutter={16}>
            <Col span={12}>
              <Card size="small" title="五行分析">
                <Paragraph>{interp.wuxingAnalysis}</Paragraph>
              </Card>
            </Col>
            <Col span={12}>
              <Card size="small" title="十神分析">
                <Paragraph>{interp.shishenAnalysis}</Paragraph>
              </Card>
            </Col>
          </Row>
        </div>
        
        {/* 各方面运势 */}
        <div style={{ marginBottom: 16 }}>
          <Title level={5}>🎯 各方面运势</Title>
          <Row gutter={16}>
            <Col span={6}>
              <Card size="small">
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 16, fontWeight: 'bold', marginBottom: 8 }}>事业</div>
                  <Rate disabled value={interp.overallRating} allowHalf style={{ fontSize: 14 }} />
                  <div style={{ marginTop: 8, color: '#666' }}>{interp.career}</div>
                </div>
              </Card>
            </Col>
            <Col span={6}>
              <Card size="small">
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 16, fontWeight: 'bold', marginBottom: 8 }}>财运</div>
                  <Rate disabled value={interp.overallRating} allowHalf style={{ fontSize: 14 }} />
                  <div style={{ marginTop: 8, color: '#666' }}>{interp.wealth}</div>
                </div>
              </Card>
            </Col>
            <Col span={6}>
              <Card size="small">
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 16, fontWeight: 'bold', marginBottom: 8 }}>婚姻</div>
                  <Rate disabled value={interp.overallRating} allowHalf style={{ fontSize: 14 }} />
                  <div style={{ marginTop: 8, color: '#666' }}>{interp.marriage}</div>
                </div>
              </Card>
            </Col>
            <Col span={6}>
              <Card size="small">
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 16, fontWeight: 'bold', marginBottom: 8 }}>健康</div>
                  <Rate disabled value={interp.overallRating} allowHalf style={{ fontSize: 14 }} />
                  <div style={{ marginTop: 8, color: '#666' }}>{interp.health}</div>
                </div>
              </Card>
            </Col>
          </Row>
        </div>
        
        {/* 警告事项 */}
        {interp.warnings.length > 0 && (
          <div style={{ marginBottom: 16 }}>
            <Title level={5}>
              <WarningOutlined style={{ color: '#faad14' }} /> 重点提示
            </Title>
            {interp.warnings.map((warning: string, idx: number) => (
              <Alert
                key={idx}
                message={warning}
                type={warning.includes('【重大】') || warning.includes('【重要】') ? 'warning' : 'info'}
                showIcon
                style={{ marginBottom: 8 }}
              />
            ))}
          </div>
        )}
      </Card>
    );
  };
  
  // 渲染流年解读
  const renderLiuNianInterpretation = () => {
    if (!selectedLiuNianInterpretation) return null;
    const interp = selectedLiuNianInterpretation;
    const liunian = interp.liunian;
    
    return (
      <Card
        title={
          <span>
            <CalendarOutlined /> {liunian.year}年 流年解读
          </span>
        }
        style={{ marginBottom: 24, borderColor: '#52c41a' }}
      >
        {/* 流年基本信息 */}
        <div style={{ marginBottom: 16 }}>
          <Title level={5}>
            {liunian.year}年 {liunian.tiangan}{liunian.dizhi}年
          </Title>
          <Tag color="blue" style={{ fontSize: 14, padding: '4px 12px', marginRight: 8 }}>
            天干{liunian.tiangan}（{interp.liunian.shishen}）
          </Tag>
          <Tag color="green" style={{ fontSize: 14, padding: '4px 12px' }}>
            地支{liunian.dizhi}
          </Tag>
        </div>
        
        {/* 干支分析 */}
        <div style={{ marginBottom: 16 }}>
          <Title level={5}>📖 流年解读</Title>
          <Paragraph>{interp.ganzhiAnalysis}</Paragraph>
        </div>
        
        {/* 与大运关系 */}
        {interp.dayunRelation && (
          <div style={{ marginBottom: 16 }}>
            <Title level={5}>🔗 与大运关系</Title>
            <Paragraph>{interp.dayunRelation}</Paragraph>
          </div>
        )}
        
        {/* 冲克分析 */}
        {interp.chongkeAnalysis && (
          <div style={{ marginBottom: 16 }}>
            <Title level={5}>⚡ 与原局冲克</Title>
            <Paragraph>{interp.chongkeAnalysis}</Paragraph>
          </div>
        )}
        
        {/* 经典解读 */}
        {interp.classicQuotes.length > 0 && (
          <div style={{ marginBottom: 16 }}>
            <Title level={5}>
              <BookOutlined /> 经典解读
            </Title>
            {interp.classicQuotes.map((quote: ClassicQuote, idx: number) => (
              <div
                key={idx}
                style={{
                  background: '#fff7e6',
                  border: '1px solid #ffd591',
                  borderRadius: 6,
                  padding: '12px',
                  marginBottom: 8
                }}
              >
                <Text strong style={{ color: '#d46b08' }}>
                  【《{quote.book}》】
                </Text>
                <Paragraph style={{ margin: '8px 0', fontStyle: 'italic' }}>
                  {quote.quote}
                </Paragraph>
                <Paragraph style={{ margin: 0, color: '#666' }}>
                  → {quote.explanation}
                </Paragraph>
              </div>
            ))}
          </div>
        )}
        
        {/* 警告事项 */}
        {interp.warnings.length > 0 && (
          <div style={{ marginBottom: 16 }}>
            <Title level={5}>
              <WarningOutlined style={{ color: '#faad14' }} /> 重点提示
            </Title>
            {interp.warnings.map((warning: string, idx: number) => (
              <Alert
                key={idx}
                message={warning}
                type={warning.includes('【重大】') || warning.includes('【重要】') ? 'warning' : 'info'}
                showIcon
                style={{ marginBottom: 8 }}
              />
            ))}
          </div>
        )}
        
        {/* 月份运势 */}
        {interp.monthFortune && interp.monthFortune.length > 0 && (
          <div style={{ marginBottom: 16 }}>
            <Title level={5}>📅 12月运势粗略</Title>
            <Row gutter={[8, 8]}>
              {interp.monthFortune.map((mf: MonthFortune, idx: number) => (
                <Col span={4} key={idx}>
                  <Tooltip title={mf.description}>
                    <Card
                      size="small"
                      style={{
                        textAlign: 'center',
                        borderColor: mf.rating === '吉' ? '#52c41a' : mf.rating === '凶' ? '#ff4d4f' : '#d9d9d9'
                      }}
                    >
                      <div style={{ fontWeight: 'bold' }}>{mf.label}</div>
                      <div style={{ fontSize: 18, margin: '4px 0' }}>
                        {mf.rating === '吉' ? '★★★★★' : mf.rating === '凶' ? '★★☆☆☆' : '★★★☆☆'}
                      </div>
                      <div style={{ fontSize: 12, color: '#666' }}>{mf.ganzhi}</div>
                    </Card>
                  </Tooltip>
                </Col>
              ))}
            </Row>
          </div>
        )}
        
        {/* 总结 */}
        {interp.summary && (
          <div style={{ marginBottom: 16 }}>
            <Title level={5}>
              <CheckCircleOutlined style={{ color: '#52c41a' }} /> 全年总结
            </Title>
            <Paragraph>{interp.summary}</Paragraph>
          </div>
        )}
      </Card>
    );
  };
  
  return (
    <div>
      {/* 大运列表 */}
      <div style={{ marginBottom: 24 }}>
        <Title level={5}>大运</Title>
        <Table
          columns={daYunColumns}
          dataSource={daYunData}
          pagination={false}
          bordered
          size="small"
          style={{ marginBottom: 16 }}
        />
      </div>
      
      {/* 当前大运解读 */}
      {renderDaYunInterpretation()}
      
      {/* 当前大运的流年 */}
      {currentDaYun && (
        <div style={{ marginBottom: 24 }}>
          <Title level={5}>
            流年 - 第{selectedDayun + 1}步大运 ({currentDaYun.tiangan}{currentDaYun.dizhi})
          </Title>
          <Table
            columns={liuNianColumns}
            dataSource={liuNianData}
            pagination={{ pageSize: 10 }}
            bordered
            size="small"
          />
        </div>
      )}
      
      {/* 流年解读详情 */}
      {renderLiuNianInterpretation()}
      
      {/* 小运 */}
      <div style={{ marginBottom: 16 }}>
        <Title level={5}>小运</Title>
        <Row gutter={8}>
          <Col span={4}>
            <Tag color="cyan" style={{ fontSize: 14, padding: '4px 12px' }}>
              小运：{xiaoYun}
            </Tag>
          </Col>
        </Row>
        
        {/* 小运解读 */}
        {xiaoYunInterpretation && (
          <Card
            size="small"
            style={{ marginTop: 8 }}
          >
            <Paragraph>{xiaoYunInterpretation.analysis}</Paragraph>
            <Paragraph type="secondary">{xiaoYunInterpretation.effect}</Paragraph>
          </Card>
        )}
      </div>
      
      {/* 童运（12岁以下显示）*/}
      {result && result.input && calculateAge(birthDate) <= 12 && (
        <div style={{ marginBottom: 16 }}>
          <Title level={5}>童运</Title>
          <Table
            columns={[
              { title: '年龄', dataIndex: 'age', key: 'age', width: 60 },
              { title: '天干', dataIndex: 'tiangan', key: 'tiangan' },
              { title: '地支', dataIndex: 'dizhi', key: 'dizhi' },
              { title: '十神', dataIndex: 'shishen', key: 'shishen', 
                render: (text: string) => <Tag color="green">{text}</Tag>
              }
            ]}
            dataSource={tongYunList.map((ty, idx) => ({
              key: idx,
              age: ty.age,
              tiangan: ty.tiangan,
              dizhi: ty.dizhi,
              shishen: ty.shishen
            }))}
            pagination={false}
            bordered
            size="small"
            style={{ maxWidth: 600, marginBottom: 8 }}
          />
          
          {/* 童运解读（简化） */}
          {tongYunList.slice(0, 3).map((ty, idx) => {
            const interp = interpretTongYun(ty.age, dayMaster, dayMasterStrength, sizhu);
            return (
              <Card
                key={idx}
                size="small"
                title={`${ty.age}岁童运解读`}
                style={{ marginBottom: 8 }}
              >
                <Paragraph>{interp.constitution}</Paragraph>
                <Paragraph type="secondary">{interp.education}</Paragraph>
              </Card>
            );
          })}
        </div>
      )}
      
      {/* 说明 */}
      <div style={{ 
        marginTop: 16, 
        padding: '12px', 
        background: '#fafafa', 
        borderRadius: 6,
        fontSize: 12,
        color: '#666'
      }}>
        <Text type="secondary">
          提示：点击大运按钮可查看该大运期间的流年详情。点击流年表格中的"详情"按钮可查看单年流年的深度解读。
          解读内容基于《三命通会》《滴天髓》《穷通宝鉴》《子平真诠》《渊海子平》五本经典命理书籍。
        </Text>
      </div>
    </div>
  );
};

// 辅助函数：计算年龄
function calculateAge(birthDate: string): number {
  const birth = new Date(birthDate);
  const now = new Date();
  return now.getFullYear() - birth.getFullYear();
}

export default LiuNianAnalysis;
