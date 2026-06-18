import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Form, Input, Select, DatePicker, TimePicker, Button, Row, Col, Card, Space, message, AutoComplete, Tag } from 'antd';
import { UserOutlined, CalendarOutlined, SearchOutlined, SwapOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { useAppStore } from '@/store/appStore';
import { searchCities } from '@/services/baziService';
import type { PaiPanInput } from '@/types/bazi';

const InputForm: React.FC = () => {
  const { input, setInput, submitPaiPan, loading, error } = useAppStore();
  const [form] = Form.useForm();
  
  // 城市搜索相关状态
  const [cityOptions, setCityOptions] = useState<Array<{label: React.ReactNode, value: string, longitude: number, latitude: number}>>([]);
  const [cityLoading, setCityLoading] = useState(false);
  const [searching, setSearching] = useState(false);
  
  // 搜索城市（防抖）
  const searchTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleCitySearch = useCallback(async (keyword: string) => {
    if (searchTimerRef.current) {
      clearTimeout(searchTimerRef.current);
    }
    if (!keyword || keyword.length < 1) {
      setCityOptions([]);
      setSearching(false);
      return;
    }
    setSearching(true);
    searchTimerRef.current = setTimeout(async () => {
      setCityLoading(true);
      try {
        const cities = await searchCities(keyword);
        const options = cities.map(c => ({
          label: (
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>{c.name}{c.province ? ` (${c.province})` : ''}</span>
              <Tag color="blue" style={{ marginLeft: 8, fontSize: 10 }}>{c.longitude.toFixed(2)}°E, {c.latitude.toFixed(2)}°N</Tag>
            </div>
          ),
          value: c.name,
          longitude: c.longitude,
          latitude: c.latitude
        }));
        setCityOptions(options);
      } catch (err) {
        console.error('搜索城市失败:', err);
      } finally {
        setCityLoading(false);
        setSearching(false);
      }
    }, 500);
  }, []);

  useEffect(() => {
    return () => {
      if (searchTimerRef.current) clearTimeout(searchTimerRef.current);
    };
  }, []);
  
  // 城市选择变化
  const handleCitySelect = (value: string, option: any) => {
    setInput({ 
      birthPlace: value,
      longitude: option.longitude,
      latitude: option.latitude
    });
  };
  
  // 提交表单
  const handleSubmit = async () => {
    try {
      await form.validateFields();
      await submitPaiPan();
    } catch (err) {
      message.error('请填写完整信息');
    }
  };
  
  // 重置表单
  const handleReset = () => {
    form.resetFields();
    useAppStore.getState().resetInput();
  };
  
  // 表单值变化
  const onValuesChange = (changedValues: any) => {
    const updates: Partial<PaiPanInput> = {};
    
    if (changedValues.name !== undefined) {
      updates.name = changedValues.name;
    }
    
    if (changedValues.gender !== undefined) {
      updates.gender = changedValues.gender;
    }
    
    if (changedValues.birthDate !== undefined) {
      updates.birthDate = changedValues.birthDate.format('YYYY-MM-DD');
    }
    
    if (changedValues.birthTime !== undefined) {
      updates.birthTime = changedValues.birthTime.format('HH:mm');
    }
    
    if (changedValues.birthPlace !== undefined) {
      updates.birthPlace = changedValues.birthPlace;
    }
    
    // 始终使用全排模式
    updates.paipanMode = 'full';
    
    if (Object.keys(updates).length > 0) {
      setInput(updates);
    }
  };
  
  return (
    <Card
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <CalendarOutlined />
          <span>四柱八字排盘 - 输入信息</span>
          <Tag color="blue" style={{ marginLeft: 8 }}>全排模式</Tag>
        </div>
      }
      style={{ maxWidth: 800, margin: '0 auto' }}
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          name: input.name,
          gender: input.gender,
          birthDate: input.birthDate ? dayjs(input.birthDate) : null,
          birthTime: input.birthTime ? dayjs(input.birthTime, 'HH:mm') : null,
          birthPlace: input.birthPlace
        }}
        onValuesChange={onValuesChange}
      >
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              label="姓名"
              rules={[{ required: true, message: '请输入姓名' }]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="请输入姓名"
                value={input.name}
                onChange={(e) => setInput({ name: e.target.value })}
              />
            </Form.Item>
          </Col>
          
          <Col span={12}>
            <Form.Item
              label="性别"
              rules={[{ required: true, message: '请选择性别' }]}
            >
              <Select
                value={input.gender}
                onChange={(value) => setInput({ gender: value })}
                options={[
                  { label: '男', value: '男' },
                  { label: '女', value: '女' }
                ]}
              />
            </Form.Item>
          </Col>
        </Row>
        
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              label="出生日期"
              rules={[{ required: true, message: '请选择出生日期' }]}
            >
              <DatePicker
                style={{ width: '100%' }}
                placeholder="选择出生日期"
                value={input.birthDate ? dayjs(input.birthDate) : null}
                onChange={(date) => setInput({ birthDate: date ? date.format('YYYY-MM-DD') : '' })}
              />
            </Form.Item>
          </Col>
          
          <Col span={12}>
            <Form.Item
              label="出生时间"
              rules={[{ required: true, message: '请选择出生时间' }]}
            >
              <TimePicker
                style={{ width: '100%' }}
                placeholder="选择出生时间"
                format="HH:mm"
                minuteStep={5}
                value={input.birthTime ? dayjs(input.birthTime, 'HH:mm') : null}
                onChange={(time) => setInput({ birthTime: time ? time.format('HH:mm') : '' })}
              />
            </Form.Item>
          </Col>
        </Row>
        
        <Row gutter={16}>
          <Col span={24}>
            <Form.Item
              label="出生地点"
              name="birthPlace"
              rules={[{ required: true, message: '请搜索并选择出生城市' }]}
              extra={input.longitude && input.latitude ? `已选择：${input.longitude.toFixed(4)}°E, ${input.latitude.toFixed(4)}°N` : '搜索城市后将自动获取经纬度'}
            >
              <AutoComplete
                value={input.birthPlace || ''}
                options={cityOptions}
                onSearch={handleCitySearch}
                onSelect={handleCitySelect}
                onChange={(value) => setInput({ birthPlace: value })}
                placeholder="输入城市名称搜索..."
                style={{ width: '100%' }}
                notFoundContent={cityLoading ? '搜索中...' : (searching ? '输入更多字符搜索...' : '未找到匹配城市')}
              >
                <Input
                  prefix={<SearchOutlined />}
                  suffix={cityLoading && <span style={{ color: '#1890ff' }}>搜索中</span>}
                />
              </AutoComplete>
            </Form.Item>
          </Col>
        </Row>
        
        <Row gutter={16}>
          <Col span={24}>
            <Form.Item label="手动调整经纬度（可选）">
              <Space.Compact style={{ width: '100%' }}>
                <Input
                  style={{ width: '50%' }}
                  prefix="经度"
                  type="number"
                  step="0.0001"
                  placeholder="自动从城市获取"
                  value={input.longitude}
                  onChange={(e) => setInput({ longitude: parseFloat(e.target.value) || undefined })}
                />
                <Input
                  style={{ width: '50%' }}
                  prefix="纬度"
                  type="number"
                  step="0.0001"
                  placeholder="自动从城市获取"
                  value={input.latitude}
                  onChange={(e) => setInput({ latitude: parseFloat(e.target.value) || undefined })}
                />
              </Space.Compact>
            </Form.Item>
          </Col>
        </Row>
        
        {error && (
          <div style={{ color: 'red', marginBottom: 16 }}>
            {error}
          </div>
        )}
        
        <Form.Item>
          <Row gutter={16}>
            <Col span={12}>
              <Button
                type="primary"
                size="large"
                block
                icon={<CalendarOutlined />}
                loading={loading}
                onClick={handleSubmit}
              >
                开始排盘
              </Button>
            </Col>
            <Col span={12}>
              <Button
                size="large"
                block
                icon={<SwapOutlined />}
                onClick={handleReset}
              >
                重置
              </Button>
            </Col>
          </Row>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default InputForm;
