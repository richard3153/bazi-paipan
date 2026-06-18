import React from 'react';
import { Card, Progress, Row, Col, Tag, Typography, Statistic, Tooltip, Alert } from 'antd';
import { FireOutlined, ExperimentOutlined, ThunderboltOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import { useAppStore } from '@/store/appStore';
import { WuXing, WuXingCount } from '@/types/bazi';
import { getWuxingColor, getWuxingIcon } from '@/utils/bazi';

const { Text, Title, Paragraph } = Typography;

// 地支藏干权重表（经典算法）
const HIDDEN_STEM_WEIGHTS: Record<string, Record<string, number>> = {
  '子': { '癸': 100 },
  '丑': { '己': 60, '癸': 30, '辛': 10 },
  '寅': { '甲': 60, '丙': 30, '戊': 10 },
  '卯': { '乙': 100 },
  '辰': { '戊': 60, '乙': 30, '癸': 10 },
  '巳': { '丙': 60, '戊': 30, '庚': 10 },
  '午': { '丁': 70, '己': 30 },
  '未': { '己': 60, '丁': 30, '乙': 10 },
  '申': { '庚': 60, '壬': 30, '戊': 10 },
  '酉': { '辛': 100 },
  '戌': { '戊': 60, '辛': 30, '丁': 10 },
  '亥': { '壬': 70, '甲': 30 },
};

// 五行属性映射
const WUXING_MAP: Record<string, string> = {
  '甲': '木', '乙': '木',
  '丙': '火', '丁': '火',
  '戊': '土', '己': '土',
  '庚': '金', '辛': '金',
  '壬': '水', '癸': '水',
  '子': '水', '丑': '土', '寅': '木', '卯': '木',
  '辰': '土', '巳': '火', '午': '火', '未': '土',
  '申': '金', '酉': '金', '戌': '土', '亥': '水',
};

// 五行旺相休囚死状态表（月令）
const WANGXIUANG死亡率: Record<string, Record<string, string>> = {
  '寅': { '木': '旺', '火': '相', '土': '死', '金': '囚', '水': '休' },
  '卯': { '木': '旺', '火': '相', '土': '死', '金': '囚', '水': '休' },
  '辰': { '木': '相', '火': '旺', '土': '旺', '金': '休', '水': '囚' },
  '巳': { '火': '旺', '土': '相', '金': '死', '木': '囚', '水': '休' },
  '午': { '火': '旺', '土': '相', '金': '死', '木': '囚', '水': '休' },
  '未': { '火': '相', '土': '旺', '金': '休', '木': '囚', '水': '死' },
  '申': { '金': '旺', '水': '相', '木': '死', '火': '囚', '土': '休' },
  '酉': { '金': '旺', '水': '相', '木': '死', '火': '囚', '土': '休' },
  '戌': { '金': '相', '水': '旺', '土': '旺', '木': '休', '火': '囚' },
  '亥': { '水': '旺', '木': '相', '火': '死', '土': '囚', '金': '休' },
  '子': { '水': '旺', '木': '相', '火': '死', '土': '囚', '金': '休' },
  '丑': { '土': '旺', '金': '相', '木': '死', '水': '囚', '火': '休' },
};

// 五行属性说明
const wuxingDescriptions: Record<WuXing, string> = {
  '金': '代表肃杀、决断、义气、财富',
  '木': '代表生长、仁慈、向上、健康',
  '水': '代表智慧、流动、变通、情感',
  '火': '代表热情、礼仪、光明、能量',
  '土': '代表承载、诚信、稳定、包容'
};

// 状态颜色映射
const stateColors: Record<string, string> = {
  '旺': '#52c41a',  // 旺盛
  '相': '#1890ff',  // 次旺
  '休': '#faad14',  // 退休
  '囚': '#f5222d',  // 被囚
  '死': '#8c8c8c',  // 衰落
};

// 计算详细五行分布（考虑藏干权重）
const calculateDetailedWuxing = (result: any): { element: WuXing, count: number, percentage: number, details: string[] }[] => {
  if (!result || !result.sizhu) return [];
  
  const { sizhu } = result;
  const wuxingScores: Record<string, number> = { '金': 0, '木': 0, '水': 0, '火': 0, '土': 0 };
  const details: Record<string, string[]> = {
    '金': [], '木': [], '水': [], '火': [], '土': []
  };
  
  // 四柱数据
  const pillars = [
    { tiangan: sizhu.year.tiangan, dizhi: sizhu.year.dizhi, label: '年' },
    { tiangan: sizhu.month.tiangan, dizhi: sizhu.month.dizhi, label: '月' },
    { tiangan: sizhu.day.tiangan, dizhi: sizhu.day.dizhi, label: '日' },
    { tiangan: sizhu.hour.tiangan, dizhi: sizhu.hour.dizhi, label: '时' },
  ];
  
  pillars.forEach(p => {
    // 天干直接计算
    const tgWx = WUXING_MAP[p.tiangan];
    if (tgWx) {
      wuxingScores[tgWx] += 100;
      details[tgWx].push(`${p.label}干${p.tiangan}(100分)`);
    }
    
    // 地支：先算地支本身五行，再按权重分配藏干
    const dzWx = WUXING_MAP[p.dizhi];
    const hiddenStems = HIDDEN_STEM_WEIGHTS[p.dizhi] || {};
    
    // 地支本气属于地支五行
    if (dzWx) {
      // 地支本气权重（简化：本气60%归地支五行，40%归藏干）
      const benqiWeight = Object.entries(hiddenStems)[0]; // 本气是第一个
      if (benqiWeight) {
        const [, weight] = benqiWeight;
        const benqiWx = WUXING_MAP[benqiWeight[0]];
        if (benqiWx) {
          wuxingScores[benqiWx] += weight; // 本气全归本气五行
          details[benqiWx].push(`${p.label}支${p.dizhi}本气${benqiWeight[0]}(${weight}分)`);
        }
      }
      
      // 中气和余气
      let rank = 0;
      for (const [stem, weight] of Object.entries(hiddenStems)) {
        if (rank > 0) { // 跳过本气
          const stemWx = WUXING_MAP[stem];
          if (stemWx) {
            wuxingScores[stemWx] += weight;
            details[stemWx].push(`${p.label}支${p.dizhi}${rank === 1 ? '中气' : '余气'}${stem}(${weight}分)`);
          }
        }
        rank++;
      }
    }
  });
  
  const total = Object.values(wuxingScores).reduce((a, b) => a + b, 0);
  return Object.entries(wuxingScores)
    .map(([element, count]) => ({
      element: element as WuXing,
      count,
      percentage: total > 0 ? Math.round(count / total * 100) : 0,
      details: details[element as WuXing]
    }))
    .sort((a, b) => b.count - a.count);
};

// 五行分布组件
const WuXingDistribution: React.FC = () => {
  const { result } = useAppStore();
  
  if (!result) return null;
  
  const { wuxing, sizhu } = result;
  const detailedWuxing = calculateDetailedWuxing(result);
  const monthBranch = sizhu.month.dizhi;
  const monthStates = WANGXIUANG死亡率[monthBranch] || {};
  
  return (
    <Card
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <ExperimentOutlined />
          <span>五行分布分析</span>
          <Tooltip title="五行计算依据《滴天髓》《子平真诠》：天干100分/个，地支藏干按本气(60%)、中气(30%)、余气(10%)分配">
            <QuestionCircleOutlined style={{ color: '#999', cursor: 'help' }} />
          </Tooltip>
        </div>
      }
      style={{ marginBottom: 24 }}
    >
      {/* 计算方法说明 */}
      <Alert
        message="计算依据（经典命理算法）"
        description={
          <div style={{ fontSize: 12 }}>
            <p style={{ marginBottom: 4 }}>
              <strong>天干：</strong>每个天干计100分，归其所属五行
            </p>
            <p style={{ marginBottom: 4 }}>
              <strong>地支藏干：</strong>本气60% + 中气30% + 余气10%（如未含本气则100%归本气）
            </p>
            <p style={{ margin: 0 }}>
              <strong>月令旺衰：</strong>月支为当令之五行得旺，相次之五行得休...（依据《三命通会》五行旺相休囚死表）
            </p>
          </div>
        }
        type="info"
        style={{ marginBottom: 16 }}
        showIcon
      />

      {/* 五行统计（详细） */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {detailedWuxing.map((item) => (
          <Col span={4} key={item.element}>
            <Card
              size="small"
              bodyStyle={{
                padding: '12px',
                textAlign: 'center',
                background: `${getWuxingColor(item.element)}15`,
                border: `1px solid ${getWuxingColor(item.element)}`
              }}
            >
              <div style={{ fontSize: 32, marginBottom: 8 }}>
                {getWuxingIcon(item.element)}
              </div>
              <Title level={4} style={{ margin: '8px 0', color: getWuxingColor(item.element) }}>
                {item.element}
              </Title>
              <Progress
                type="circle"
                percent={item.percentage}
                size={80}
                strokeColor={getWuxingColor(item.element)}
                format={() => (
                  <span style={{ color: getWuxingColor(item.element), fontSize: 16 }}>
                    {item.count}
                  </span>
                )}
              />
              <div style={{ marginTop: 8, fontSize: 11, color: '#666' }}>
                {item.details.length}项 / {item.percentage}%
              </div>
            </Card>
          </Col>
        ))}
      </Row>
      
      {/* 月令旺衰 */}
      <Card
        size="small"
        title={`月令旺衰分析（月支为${monthBranch}）`}
        bodyStyle={{ padding: '12px' }}
        style={{ marginBottom: 16 }}
      >
        <Row gutter={16}>
          {Object.entries(monthStates).map(([wx, state]) => (
            <Col span={4} key={wx}>
              <Tag 
                color={stateColors[state] || 'default'}
                style={{ width: '100%', textAlign: 'center', padding: '4px 8px' }}
              >
                <div>{wx} <strong>{state}</strong></div>
              </Tag>
            </Col>
          ))}
        </Row>
        <Text type="secondary" style={{ fontSize: 12, marginTop: 8, display: 'block' }}>
          月令为{monthBranch}，当令五行得<span style={{ color: stateColors['旺'] }}>旺</span>，进气五行得<span style={{ color: stateColors['相'] }}>相</span>...
          （依据经典命理：木旺于春，火旺于夏，金旺于秋，水旺于冬，土旺于四季）
        </Text>
      </Card>
      
      {/* 五行详细得分 */}
      <Card
        size="small"
        title="详细得分分解"
        bodyStyle={{ padding: '12px' }}
        style={{ marginBottom: 16 }}
      >
        {detailedWuxing.map(item => (
          <div key={item.element} style={{ marginBottom: 12 }}>
            <Tag color={getWuxingColor(item.element)} style={{ marginRight: 8 }}>
              {item.element}
            </Tag>
            <span style={{ marginRight: 8 }}>{item.count}分 ({item.percentage}%)</span>
            <Text type="secondary" style={{ fontSize: 11 }}>
              {item.details.join(' + ') || '无'}
            </Text>
          </div>
        ))}
      </Card>
      
      {/* 五行缺失提示 */}
      {detailedWuxing.filter(w => w.count === 0).length > 0 && (
        <Card
          size="small"
          style={{ marginBottom: 16, background: '#fff2e8', border: '1px solid #ffa39e' }}
          bodyStyle={{ padding: '12px' }}
        >
          <Text strong style={{ color: '#cf1322' }}>
            ⚠️ 五行缺失提醒:
          </Text>
          <span style={{ marginLeft: 8 }}>
            {detailedWuxing
              .filter(w => w.count === 0)
              .map(w => (
                <Tag key={w.element} color={getWuxingColor(w.element)}>
                  {w.element}缺失
                </Tag>
              ))}
          </span>
          <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
            五行缺失会影响命局平衡，建议通过名字、风水、服饰等补充缺失的五行能量
          </div>
        </Card>
      )}
      
      {/* 五行说明 */}
      <Row gutter={16}>
        <Col span={12}>
          <Card
            size="small"
            title="五行属性（十天干、十二地支）"
            bodyStyle={{ padding: '12px' }}
          >
            <div style={{ marginBottom: 8 }}>
              <Text strong>天干：</Text>
              <div style={{ fontSize: 12 }}>
                <Tag color="green">甲乙木</Tag>
                <Tag color="red">丙丁火</Tag>
                <Tag color="orange">戊己土</Tag>
                <Tag color="#d9d9d9">庚辛金</Tag>
                <Tag color="blue">壬癸水</Tag>
              </div>
            </div>
            <div style={{ marginBottom: 8 }}>
              <Text strong>地支（正化）：</Text>
              <div style={{ fontSize: 12 }}>
                <Tag>子亥水</Tag>
                <Tag>寅卯木</Tag>
                <Tag>巳午火</Tag>
                <Tag>申酉金</Tag>
                <Tag>辰戌丑未土</Tag>
              </div>
            </div>
            {Object.entries(wuxingDescriptions).map(([element, desc]) => (
              <div key={element} style={{ marginBottom: 4 }}>
                <Tag color={getWuxingColor(element as WuXing)}>
                  {getWuxingIcon(element as WuXing)} {element}
                </Tag>
                <Text style={{ fontSize: 11 }}>{desc}</Text>
              </div>
            ))}
          </Card>
        </Col>
        
        <Col span={12}>
          <Card
            size="small"
            title="五行关系（相生相克）"
            bodyStyle={{ padding: '12px' }}
          >
            <div style={{ marginBottom: 12 }}>
              <Text strong>相生（木→火→土→金→水→木）：</Text>
              <div style={{ fontSize: 12, color: '#52c41a', marginTop: 4 }}>
                {wuxingRelations['相生']}
              </div>
              <Text type="secondary" style={{ fontSize: 10 }}>生我者为印绶，主庇护、成长</Text>
            </div>
            <div style={{ marginBottom: 12 }}>
              <Text strong>相克（木→土→水→火→金→木）：</Text>
              <div style={{ fontSize: 12, color: '#f5222d', marginTop: 4 }}>
                {wuxingRelations['相克']}
              </div>
              <Text type="secondary" style={{ fontSize: 10 }}>克我者为官杀，主约束、压力</Text>
            </div>
            <div style={{ marginBottom: 4 }}>
              <Text strong>同类：</Text>
              <Text type="secondary" style={{ fontSize: 11 }}>比肩、劫财，主竞争、自立</Text>
            </div>
            <div>
              <Text strong>异类：</Text>
              <Text type="secondary" style={{ fontSize: 11 }}>食神、伤官、偏财、正财</Text>
            </div>
          </Card>
        </Col>
      </Row>
    </Card>
  );
};

// 五行相生相克
const wuxingRelations = {
  '相生': '木生火 → 火生土 → 土生金 → 金生水 → 水生木',
  '相克': '木克土 → 土克水 → 水克火 → 火克金 → 金克木'
};

export default WuXingDistribution;
