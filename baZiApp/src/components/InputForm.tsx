import React, { useState, useCallback, useEffect } from 'react';
import { Form, Input, Select, DatePicker, TimePicker, Button, Row, Col, Card, Space, message, Tag } from 'antd';
import { UserOutlined, CalendarOutlined, SwapOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { useAppStore } from '@/store/appStore';
import { getProvinces, getCitiesByProvince } from '@/services/baziService';
import type { PaiPanInput } from '@/types/bazi';

const InputForm: React.FC = () => {
  const { input, setInput, submitPaiPan, loading, error } = useAppStore();
  const [form] = Form.useForm();
  
  // 级联城市选择相关状态
  const [provinces, setProvinces] = useState<string[]>([]);
  const [cities, setCities] = useState<Array<{id: number, name: string, longitude: number, latitude: number}>>([]);
  const [cityLoading, setCityLoading] = useState(false);
  const [selectedProvince, setSelectedProvince] = useState<string>(input.birthPlace ? '' : '');

  // 加载省份列表
  useEffect(() => {
    getProvinces().then(provinceList => {
      setProvinces(provinceList);
    });
  }, []);

  // 省份选择变化
  const handleProvinceChange = useCallback(async (province: string) => {
    setSelectedProvince(province);
    form.setFieldsValue({ birthPlace: undefined });
    setInput({ birthPlace: '', longitude: undefined, latitude: undefined });
    if (province) {
      setCityLoading(true);
      try {
        const cityList = await getCitiesByProvince(province);
        setCities(cityList);
      } catch (err) {
        console.error('加载城市失败:', err);
      } finally {
        setCityLoading(false);
      }
    } else {
      setCities([]);
    }
  }, [form, setInput]);

  // 城市选择变化
  const handleCityChange = (cityName: string) => {
    const city = cities.find(c => c.name === cityName);
    if (city) {
      setInput({
        birthPlace: city.name,
        longitude: city.longitude,
        latitude: city.latitude
      });
    }
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
    
    if (changedValues.province !== undefined) {
      // province handled by handleProvinceChange, no need to update input
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
          <Col span={8}>
            <Form.Item
              label="省份"
              name="province"
            >
              <Select
                placeholder="请选择省份"
                showSearch
                optionFilterProp="label"
                value={selectedProvince || undefined}
                onChange={handleProvinceChange}
                options={provinces.map(p => ({ label: p, value: p }))}
              />
            </Form.Item>
          </Col>
          <Col span={16}>
            <Form.Item
              label="城市"
              name="birthPlace"
              rules={[{ required: true, message: '请选择出生城市' }]}
              extra={input.longitude && input.latitude ? `已选择：${input.longitude.toFixed(4)}°E, ${input.latitude.toFixed(4)}°N` : '选择省份和城市后将自动获取经纬度'}
            >
              <Select
                placeholder={selectedProvince ? '请选择城市' : '请先选择省份'}
                loading={cityLoading}
                disabled={!selectedProvince}
                value={input.birthPlace || undefined}
                onChange={handleCityChange}
                options={cities.map(c => ({
                  label: (
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span>{c.name}</span>
                      <Tag color="blue" style={{ marginLeft: 8, fontSize: 10 }}>{c.longitude.toFixed(2)}°E, {c.latitude.toFixed(2)}°N</Tag>
                    </div>
                  ),
                  value: c.name
                }))}
                showSearch
                optionFilterProp="label"
              />
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
