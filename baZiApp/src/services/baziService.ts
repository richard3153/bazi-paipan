import { PaiPanInput, PaiPanResult, ApiResponse } from '@/types/bazi';
import { mockPaiPan } from '@/mock/data';

// 是否使用Mock数据
const USE_MOCK = false; // 改为false，调用真实后端API

// 实际后端API地址（将来替换）
const API_BASE_URL = 'http://localhost:8001/api';

/**
 * 转换后端响应格式为前端期望格式
 */
function transformBackendResponse(backendData: any, input: PaiPanInput): PaiPanResult {
  // 转换单柱
  const transformPillar = (pillar: any) => ({
    tiangan: pillar.stem,
    dizhi: pillar.branch,
    canggan: pillar.hidden_stems || []
  });
  
  const dayMaster = backendData.day_master;
  
  // 构建四柱
  const sizhu = {
    year: transformPillar(backendData.year_pillar),
    month: transformPillar(backendData.month_pillar),
    day: transformPillar(backendData.day_pillar),
    hour: transformPillar(backendData.hour_pillar)
  };
  
  // 计算五行统计
  const wuxingCount: Record<string, number> = { '金': 0, '木': 0, '水': 0, '火': 0, '土': 0 };
  [backendData.year_pillar, backendData.month_pillar, backendData.day_pillar, backendData.hour_pillar].forEach(p => {
    const wx = p.wuxing;
    if (wx) wuxingCount[wx] = (wuxingCount[wx] || 0) + 1;
  });
  const total = Object.values(wuxingCount).reduce((a: number, b: number) => a + b, 0);
  const wuxing = Object.entries(wuxingCount).map(([element, count]) => ({
    element: element as any,
    count,
    percentage: total > 0 ? Math.round(count / total * 100) : 0
  }));
  
  // 转换分析报告
  const ar = backendData.analysis_report;
  const analysis = ar ? {
    overview: ar.overview || '命盘分析',
    dayMasterAnalysis: ar.dayMasterAnalysis || `日主${dayMaster}，五行${backendData.day_master_wuxing}`,
    wuxingAnalysis: ar.wuxingAnalysis || '五行分析',
    shishenAnalysis: ar.shishenAnalysis || '十神分析',
    wealth: ar.wealth || '财运分析',
    career: ar.career || '事业分析',
    health: ar.health || '健康分析',
    marriage: ar.marriage || '婚姻分析',
    education: ar.education || '学业分析',
    suggestions: ar.suggestions || ['建议1', '建议2']
  } : {
    overview: '命盘分析',
    dayMasterAnalysis: `日主${dayMaster}，五行${backendData.day_master_wuxing}`,
    wuxingAnalysis: '五行分析',
    shishenAnalysis: '十神分析',
    wealth: '财运分析',
    career: '事业分析',
    health: '健康分析',
    marriage: '婚姻分析',
    education: '学业分析',
    suggestions: ['建议1', '建议2']
  };
  
  return {
    input,
    sizhu,
    wuxing,
    dayMaster,
    dayMasterStrength: '中和',
    analysis,
    // 透传后端完整数据
    taiyuan: backendData.taiyuan ? { tiangan: backendData.taiyuan.stem, dizhi: backendData.taiyuan.branch } : undefined,
    minggong: backendData.mggong ? { tiangan: backendData.mggong.stem, dizhi: backendData.mggong.branch } : undefined,
    shengong: backendData.shengong ? { tiangan: backendData.shengong.stem, dizhi: backendData.shengong.branch } : undefined,
    // 大运数据（包含详细的起运/交运信息）
    dayun: (backendData.dayun?.dayun || []).map((d: any) => ({
      index: d.index,
      startAge: d.startAge,
      endAge: d.endAge,
      tiangan: d.stem,
      dizhi: d.branch,
      shishen: '',
      startYear: d.startYear || 0,
      endYear: d.endYear || 0
    })),
    // 童运数据
    tongyun: (backendData.dayun?.tongyun || []).map((t: any) => ({
      age: t.age,
      tiangan: t.stem,
      dizhi: t.branch
    })),
    // 起运信息（qiyun - 不是标准PaiPanResult字段，但前端会用）
    qiyun: backendData.dayun ? {
      forward: backendData.dayun.forward,
      direction: backendData.dayun.direction,
      startAge: backendData.dayun.startAge,
      startAgeXu: backendData.dayun.startAgeXu,
      qiyunDays: backendData.dayun.qiyunDays,
      qiyunMonths: backendData.dayun.qiyunMonths,
      refTerm: backendData.dayun.refTerm,
      jiaoyunYear: backendData.dayun.jiaoyunYear,
      jiaoyunMonth: backendData.dayun.jiaoyunMonth
    } : undefined,
    shensha: transformShensha(backendData.shensha),
  };
}

/**
 * 转换神煞数据格式
 */
function transformShensha(shensha: any): any {
  if (!shensha) return { all: [] };
  const all: Array<{name: string, position?: string}> = [];
  // 后端返回格式: { "year_stem": [...], "year_branch": [...], "month_stem": [...], ... }
  const posMap: Record<string, string> = {
    year_stem: '年干', year_branch: '年支',
    month_stem: '月干', month_branch: '月支',
    day_stem: '日干', day_branch: '日支',
    hour_stem: '时干', hour_branch: '时支',
  };
  for (const [key, list] of Object.entries(shensha)) {
    if (Array.isArray(list)) {
      for (const name of list) {
        all.push({ name, position: posMap[key] || key });
      }
    }
  }
  return { all };
}

/**
 * 排盘API - 获取四柱八字
 * @param input 排盘输入参数
 * @returns 排盘结果
 */
export async function paiPan(input: PaiPanInput): Promise<ApiResponse<PaiPanResult>> {
  try {
    if (USE_MOCK) {
      // 使用Mock数据
      const result = await mockPaiPan(input);
      return {
        success: true,
        data: result
      };
    } else {
      // 调用真实API
      // 转换数据格式：前端PaiPanInput -> 后端BaziRequest
      const requestBody = {
        birth_info: {
          birth_date: input.birthDate,
          birth_time: input.birthTime,
          city: input.birthPlace,
          longitude: input.longitude || null,
          latitude: input.latitude || null,
          use_true_solar: false
        }
      };
      
      const response = await fetch(`${API_BASE_URL}/bazi/calculate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      // 转换后端响应格式为前端期望格式
      const transformedData = transformBackendResponse(result.data, input);
      
      return {
        success: true,
        data: transformedData
      };
    }
  } catch (error) {
    console.error('排盘API调用失败:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : '未知错误',
      message: '排盘失败，请稍后重试'
    };
  }
}

/**
 * 获取中国所有省份列表
 */
export async function getProvinces(): Promise<string[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/geo/provinces`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });
    const result = await response.json();
    if (result.success && Array.isArray(result.data)) {
      return result.data.map((p: { name: string }) => p.name);
    }
    return [];
  } catch (error) {
    console.error('获取省份列表失败:', error);
    return [];
  }
}

/**
 * 根据省份获取城市列表
 */
export async function getCitiesByProvince(province: string): Promise<Array<{
  id: number;
  name: string;
  province: string;
  longitude: number;
  latitude: number;
}>> {
  try {
    const response = await fetch(`${API_BASE_URL}/geo/cities-by-province`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ province })
    });
    const result = await response.json();
    if (result.success && Array.isArray(result.data)) {
      return result.data.map((c: any) => ({
        id: c.id,
        name: c.name,
        province: c.province,
        longitude: c.longitude,
        latitude: c.latitude
      }));
    }
    return [];
  } catch (error) {
    console.error('获取城市列表失败:', error);
    return [];
  }
}

/**
 * 获取城市经纬度（通过城市名称）
 * @param cityName 城市名称
 * @returns 经纬度信息
 */
export async function getCityCoordinates(cityName: string): Promise<{
  longitude: number;
  latitude: number;
} | null> {
  // Mock实现 - 实际应调用地理编码API（如高德、百度地图API）
  const cityDatabase = await import('@/mock/data').then(m => m.cityDatabase);
  const city = cityDatabase.find(c => c.name === cityName);
  
  if (city) {
    return {
      longitude: city.longitude,
      latitude: city.latitude
    };
  }
  
  return null;
}

/**
 * 验证出生日期时间
 * @param date 日期字符串 YYYY-MM-DD
 * @param time 时间字符串 HH:mm
 * @returns 是否有效
 */
export function validateBirthDateTime(date: string, time: string): boolean {
  const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
  const timeRegex = /^\d{2}:\d{2}$/;
  
  if (!dateRegex.test(date) || !timeRegex.test(time)) {
    return false;
  }
  
  const birthDate = new Date(`${date}T${time}:00`);
  const now = new Date();
  
  // 日期不能晚于现在
  if (birthDate > now) {
    return false;
  }
  
  // 日期不能早于1900年
  const minDate = new Date('1900-01-01');
  if (birthDate < minDate) {
    return false;
  }
  
  return true;
}

/**
 * 真太阳时计算（简化版）
 * @param localTime 本地时间
 * @param longitude 经度
 * @returns 真太阳时
 */
export function calculateTrueSolarTime(
  localTime: string,
  longitude: number
): string {
  // 简化实现：经度每差15度，时间差1小时
  const timeDiffMinutes = (longitude - 120) / 15 * 60; // 以120°E为基准
  
  const [hours, minutes] = localTime.split(':').map(Number);
  const totalMinutes = hours * 60 + minutes + timeDiffMinutes;
  
  // 处理跨日
  const adjustedHours = Math.floor((totalMinutes % 1440 + 1440) % 1440 / 60);
  const adjustedMinutes = Math.floor((totalMinutes % 60 + 60) % 60);
  
  return `${String(adjustedHours).padStart(2, '0')}:${String(adjustedMinutes).padStart(2, '0')}`;
}

/**
 * 搜索城市（远程API）
 * @param keyword 搜索关键词
 * @returns 城市列表
 */
export async function searchCities(keyword: string): Promise<Array<{id: number, name: string, province: string | null, longitude: number, latitude: number}>> {
  if (!keyword || keyword.length < 1) {
    return [];
  }
  
  try {
    const response = await fetch(`${API_BASE_URL}/geo/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ city_name: keyword })
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const result = await response.json();
    return (result.data || []) as Array<{id: number, name: string, province: string | null, longitude: number, latitude: number}>;
  } catch (error) {
    console.error('搜索城市失败:', error);
    return [];
  }
}
