import React from 'react';
import { Card, Row, Col, Tag, Typography, Table, Divider } from 'antd';
import { ThunderboltOutlined } from '@ant-design/icons';
import { useAppStore } from '@/store/appStore';
import { TianGan, DiZhi } from '@/types/bazi';
import { WUXING_MAP, DIZHI_CANGGAN, NaYin, getWuxingColorProfessional, calculateShiShen, calculateWangShuai } from '@/utils/bazi';

const { Text } = Typography;

// 专业四柱排盘表格组件
const SiZhuDisplay: React.FC = () => {
  const { result } = useAppStore();

  if (!result || !result.sizhu) return null;

  const { sizhu, dayMaster } = result;
  const mode = result.input.paipanMode || 'simple';
  const isFull = mode === 'full';

  const columns = [
    {
      title: '',
      dataIndex: 'label',
      key: 'label',
      width: 80,
      render: (text: string) => <Text strong>{text}</Text>
    },
    {
      title: '年柱',
      dataIndex: 'year',
      key: 'year',
      render: (_: any, record: any) => renderCell(record, 'year')
    },
    {
      title: '月柱',
      dataIndex: 'month',
      key: 'month',
      render: (_: any, record: any) => renderCell(record, 'month')
    },
    {
      title: '日柱',
      dataIndex: 'day',
      key: 'day',
      render: (_: any, record: any) => renderCell(record, 'day')
    },
    {
      title: '时柱',
      dataIndex: 'hour',
      key: 'hour',
      render: (_: any, record: any) => renderCell(record, 'hour')
    }
  ];

  const dataSource = [
    {
      key: 'shishen',
      label: '十神',
      year: calcShiShen(dayMaster, sizhu.year.tiangan),
      month: calcShiShen(dayMaster, sizhu.month.tiangan),
      day: '日主',
      hour: calcShiShen(dayMaster, sizhu.hour.tiangan)
    },
    {
      key: 'tiangan',
      label: '天干',
      year: sizhu.year.tiangan,
      month: sizhu.month.tiangan,
      day: sizhu.day.tiangan,
      hour: sizhu.hour.tiangan
    },
    {
      key: 'dizhi',
      label: '地支',
      year: sizhu.year.dizhi,
      month: sizhu.month.dizhi,
      day: sizhu.day.dizhi,
      hour: sizhu.hour.dizhi
    },
    {
      key: 'canggan',
      label: '藏干',
      year: DIZHI_CANGGAN[sizhu.year.dizhi].join(' '),
      month: DIZHI_CANGGAN[sizhu.month.dizhi].join(' '),
      day: DIZHI_CANGGAN[sizhu.day.dizhi].join(' '),
      hour: DIZHI_CANGGAN[sizhu.hour.dizhi].join(' ')
    }
  ];

  // 全排专属内容
  const renderFullContent = () => {
    if (!isFull) return null;
    const ty = result.taiyuan;
    const mg = result.minggong;
    const sg = result.shengong;
    const dayun = result.dayun || [];
    const tongyun = result.tongyun || [];
    const shensha = result.shensha || { all: [] };

    return (
      <>
        {/* 胎元、命宫、身宫 */}
        <Card size="small" style={{ marginTop: 16 }} bodyStyle={{ padding: '12px' }}>
          <Row gutter={16}>
            <Col span={8}>
              <Text strong>胎元：</Text>
              <Text style={{ marginLeft: 8 }}>
                {ty ? `${ty.tiangan}${ty.dizhi}` : '-'}
              </Text>
            </Col>
            <Col span={8}>
              <Text strong>命宫：</Text>
              <Text style={{ marginLeft: 8 }}>
                {mg ? `${mg.tiangan}${mg.dizhi}` : '-'}
              </Text>
            </Col>
            <Col span={8}>
              <Text strong>身宫：</Text>
              <Text style={{ marginLeft: 8 }}>
                {sg ? `${sg.tiangan}${sg.dizhi}` : '-'}
              </Text>
            </Col>
          </Row>
        </Card>

        {/* 起运、交运信息 */}
        {result.qiyun && (
          <Card size="small" style={{ marginTop: 8, background: '#f0f5ff', border: '1px solid #adc6ff' }} bodyStyle={{ padding: '12px' }}>
            <Row gutter={16}>
              <Col span={6}>
                <Text strong>起运年龄：</Text>
                <Text style={{ marginLeft: 4 }}>{result.qiyun.startAge}岁（虚岁{result.qiyun.startAgeXu}岁）</Text>
              </Col>
              <Col span={6}>
                <Text strong>大运方向：</Text>
                <Text style={{ marginLeft: 4 }}>{result.qiyun.direction}</Text>
              </Col>
              <Col span={6}>
                <Text strong>计算依据：</Text>
                <Text style={{ marginLeft: 4 }}>距{result.qiyun.refTerm}{result.qiyun.qiyunDays}天÷3</Text>
              </Col>
              <Col span={6}>
                <Text strong>交运年份：</Text>
                <Text style={{ marginLeft: 4, color: '#1890ff', fontWeight: 500 }}>
                  {result.qiyun.jiaoyunYear}年{result.qiyun.jiaoyunMonth}月
                </Text>
              </Col>
            </Row>
          </Card>
        )}

        {/* 旺衰 */}
        <Card size="small" style={{ marginTop: 8 }} bodyStyle={{ padding: '12px' }}>
          <Text strong>旺衰（十二状态）：</Text>
          <div style={{ marginTop: 6 }}>
            {[
              { label: '年支', zhi: sizhu.year.dizhi },
              { label: '月支', zhi: sizhu.month.dizhi },
              { label: '日支', zhi: sizhu.day.dizhi },
              { label: '时支', zhi: sizhu.hour.dizhi }
            ].map(item => (
              <Tag key={item.label} color="blue" style={{ marginRight: 8 }}>
                {item.label} {calculateWangShuai(dayMaster, item.zhi)}
              </Tag>
            ))}
          </div>
        </Card>

        {/* 纳音 */}
        <Card size="small" style={{ marginTop: 8 }} bodyStyle={{ padding: '12px' }}>
          <Text strong>纳音五行：</Text>
          <div style={{ marginTop: 6 }}>
            {[
              { label: '年', tiangan: sizhu.year.tiangan, dizhi: sizhu.year.dizhi },
              { label: '月', tiangan: sizhu.month.tiangan, dizhi: sizhu.month.dizhi },
              { label: '日', tiangan: sizhu.day.tiangan, dizhi: sizhu.day.dizhi },
              { label: '时', tiangan: sizhu.hour.tiangan, dizhi: sizhu.hour.dizhi }
            ].map(item => (
              <Tag key={item.label} color="orange" style={{ marginRight: 8 }}>
                {item.label}柱 [{NaYin(item.tiangan, item.dizhi)}]
              </Tag>
            ))}
          </div>
        </Card>

        {/* 神煞 */}
        {shensha.all && shensha.all.length > 0 && (
          <Card size="small" style={{ marginTop: 8 }} bodyStyle={{ padding: '12px' }}>
            <Text strong>神煞：</Text>
            <div style={{ marginTop: 6 }}>
              {shensha.all.map((sha: any, idx: number) => (
                <Tag key={idx} color="red" style={{ marginRight: 4, marginBottom: 4 }}>
                  {sha.name}{sha.position ? `（${sha.position}）` : ''}
                </Tag>
              ))}
            </div>
          </Card>
        )}

        {/* 大运（详细信息）*/}
        {dayun.length > 0 && (
          <Card size="small" style={{ marginTop: 8 }} bodyStyle={{ padding: '12px' }}>
            <Text strong>大运：</Text>
            <div style={{ marginTop: 6, display: 'flex', flexWrap: 'wrap', gap: 4 }}>
              {dayun.map((d: any) => (
                <Tag key={d.index} color="purple" style={{ padding: '4px 8px' }}>
                  <div>第{d.index}步 {d.tiangan}{d.dizhi}</div>
                  <div style={{ fontSize: 11, opacity: 0.8 }}>
                    {d.startAge}-{d.endAge}岁
                    {d.startYear > 0 && `（${d.startYear}-${d.endYear}年）`}
                  </div>
                </Tag>
              ))}
            </div>
          </Card>
        )}

        {/* 童运（详细信息）*/}
        {tongyun && tongyun.length > 0 && (
          <Card size="small" style={{ marginTop: 8, background: '#f6ffed', border: '1px solid #b7eb8f' }} bodyStyle={{ padding: '12px' }}>
            <Text strong>童运（1-12岁）：</Text>
            <div style={{ marginTop: 6, display: 'flex', flexWrap: 'wrap', gap: 4 }}>
              {tongyun.slice(0, 12).map((t: any) => (
                <Tag key={t.age} color="green">
                  {t.age}岁 {t.tiangan}{t.dizhi}
                </Tag>
              ))}
            </div>
          </Card>
        )}
      </>
    );
  };

  return (
    <Card
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <ThunderboltOutlined />
          <span>四柱八字排盘</span>
        </div>
      }
      style={{ marginBottom: 24 }}
    >
      {/* 顶部信息栏 */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        marginBottom: 16,
        padding: '12px',
        background: '#fafafa',
        borderRadius: 6,
        flexWrap: 'wrap',
        gap: 8
      }}>
        <div>
          <Text><Text strong>姓名：</Text>{result.input.name || 'XXX'}</Text>
          <Text style={{ marginLeft: 16 }}><Text strong>出生地：</Text>{result.input.birthPlace || '不填写'}</Text>
          <Tag color={isFull ? 'blue' : 'default'} style={{ marginLeft: 16 }}>
            {isFull ? '全排' : '普通式'}
          </Tag>
        </div>
        <div>
          <Text><Text strong>公历：</Text>{result.input.birthDate} {result.input.birthTime}</Text>
        </div>
      </div>

      {/* 四柱核心排盘表格 */}
      <Table
        columns={columns}
        dataSource={dataSource}
        pagination={false}
        bordered
        size="middle"
        style={{ marginBottom: 16 }}
        components={{
          body: {
            cell: (props: any) => {
              const { children, ...restProps } = props;
              const isDay = props.record?.key === 'day';
              return (
                <td {...restProps} style={{
                  textAlign: 'center',
                  fontWeight: isDay ? 'bold' : 'normal',
                  backgroundColor: isDay ? '#e6f7ff' : 'transparent',
                  border: isDay ? '2px solid #1890ff' : undefined
                }}>
                  <div>{children}</div>
                </td>
              );
            }
          }
        }}
      />

      {/* 全排专属内容 */}
      {renderFullContent()}
    </Card>
  );
};

// 渲染单元格内容（带五行颜色）
function renderCell(record: any, columnKey: string): React.ReactNode {
  const text = record[columnKey];
  if (!text) return null;

  // 十神行
  if (record.key === 'shishen') {
    return <Tag color="purple">{text}</Tag>;
  }

  // 天干行
  if (record.key === 'tiangan') {
    const color = getWuxingColorProfessional(WUXING_MAP[text as TianGan]);
    const isDay = columnKey === 'day';
    return (
      <span style={{
        color,
        fontWeight: isDay ? 'bold' : 'normal',
        fontSize: isDay ? 20 : 16
      }}>
        {text}
      </span>
    );
  }

  // 地支行
  if (record.key === 'dizhi') {
    const color = getWuxingColorProfessional(WUXING_MAP[text as DiZhi]);
    return <span style={{ color, fontSize: 16 }}>{text}</span>;
  }

  // 藏干行
  if (record.key === 'canggan') {
    return <Text type="secondary" style={{ fontSize: 12 }}>{text}</Text>;
  }

  return <span>{text}</span>;
}

function calcShiShen(dayMaster: TianGan, target: TianGan): string {
  return calculateShiShen(dayMaster, target);
}

export default SiZhuDisplay;