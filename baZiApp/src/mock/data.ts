import { PaiPanResult, PaiPanInput, WuXingCount } from '@/types/bazi';
import { calculateFullBazi, calculateDaYun, calculateLiuNian, calculateTongYun, calculateShenShaFromBazi, WUXING_MAP } from '@/utils/bazi';

// Mock排盘结果
export const mockPaiPanResult: PaiPanResult = {
  input: {
    name: '张三',
    gender: '男',
    birthDate: '1990-05-15',
    birthTime: '14:30',
    birthPlace: '北京'
  },
  sizhu: {
    year: {
      tiangan: '庚',
      dizhi: '午',
      shishen: '正官',
      canggan: ['丁', '己']
    },
    month: {
      tiangan: '辛',
      dizhi: '巳',
      shishen: '七杀',
      canggan: ['丙', '庚', '戊']
    },
    day: {
      tiangan: '甲',
      dizhi: '寅',
      shishen: '日主',
      canggan: ['甲', '丙', '戊']
    },
    hour: {
      tiangan: '辛',
      dizhi: '未',
      shishen: '正财',
      canggan: ['己', '丁', '乙']
    }
  },
  wuxing: [
    { element: '金', count: 3, percentage: 30 },
    { element: '木', count: 2, percentage: 20 },
    { element: '水', count: 0, percentage: 0 },
    { element: '火', count: 3, percentage: 30 },
    { element: '土', count: 2, percentage: 20 }
  ],
  dayMaster: '甲',
  dayMasterStrength: '中和',
  analysis: {
    overview: '此命造日主甲木生于巳月，火炎土燥，需水调候。年柱庚午，金火相战；月柱辛巳，官杀混杂；日柱甲寅，比肩帮身；时柱辛未，财星坐库。整体来看，命主性格刚毅，有领导才能，但需注意情绪管理。',
    dayMasterAnalysis: '日主甲木，属阳木，代表参天大树。甲木之人通常正直、有责任感、领导能力强。生于巳月（初夏），火势渐旺，木气渐衰，需水滋润。日坐寅木强根，得地支助力，身不算弱。',
    wuxingAnalysis: '五行分布：金3、木2、水0、火3、土2。缺水较为明显，水为印星，代表智慧、学识和贵人运。建议平时多接触水相关的事物，如居住近水、佩戴黑色饰品等。火旺克金，需注意呼吸系统健康。',
    shishenAnalysis: '十神配置：年干正官、月干七杀、时干正财。官杀混杂，主事业起伏较大，早年工作压力重，中年后渐入佳境。正财透出，财运稳定，适合稳健投资。日坐比肩，朋友助力多，但竞争也多。',
    wealth: '财运分析：正财格，财运稳定但不暴富。辛金正财透出时干，中年后财运渐佳。建议从事与金、土相关的行业，如金融、房地产、建筑等。避免高风险投资，稳健理财为宜。',
    career: '事业分析：官杀混杂，适合军警、法律、管理等权威性职业。甲木日主有领导才能，可胜任管理岗位。宜往北方（水地）或东方（木地）发展。31-40岁行运最佳，事业上升期。',
    health: '健康分析：五行缺水，需注意肾脏、泌尿系统健康。火旺克金，注意呼吸系统、皮肤问题。建议多喝水、规律作息、适度运动。定期体检，防微杜渐。',
    marriage: '婚姻分析：男命以正财为妻星，辛金正财透出时干，妻缘不错。但日坐比肩，婚姻中易有竞争或第三者干扰。建议晚婚（28岁后），夫妻间多沟通理解。配偶性格坚毅，能持家。',
    education: '学业分析：印星（水）缺失，早年学业不算突出，但甲木日主有上进心，中年后通过学习提升明显。适合学习实用技能，如工程技术、计算机等。终身学习是成功关键。',
    suggestions: [
      '补水：多接触水相关事物，如游泳、养鱼、居住近水',
      '职业发展：往北方或东方发展，从事管理、技术类工作',
      '人际关系的改善：多结交属鼠、属猪（水）的朋友',
      '健康养生：注意补肾，多喝水，少熬夜',
      '投资理财：稳健为主，避免高风险投资',
      '性格修炼：控制脾气，学会柔性处事'
    ]
  }
};

// 模拟API延迟
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// 计算五行统计
function calcWuXing(sizhu: any) {
  const countMap: Record<string, number> = { '金': 0, '木': 0, '水': 0, '火': 0, '土': 0 };
  const all = [
    sizhu.year.tiangan, sizhu.year.dizhi,
    sizhu.month.tiangan, sizhu.month.dizhi,
    sizhu.day.tiangan, sizhu.day.dizhi,
    sizhu.hour.tiangan, sizhu.hour.dizhi
  ];
  for (const k of all) {
    const wx = WUXING_MAP[k as keyof typeof WUXING_MAP];
    if (wx) countMap[wx]++;
  }
  const total = 8;
  return Object.entries(countMap).map(([element, count]) => ({
    element: element as WuXingCount['element'],
    count,
    percentage: Math.round(count / total * 100)
  }));
}

// 判断日主强弱（简化）
function calcDayMasterStrength(sizhu: any): '强' | '弱' | '中和' {
  const wuxingCounts = calcWuXing(sizhu);
  const dmWx = WUXING_MAP[sizhu.day.tiangan as keyof typeof WUXING_MAP];
  const count = wuxingCounts.find((w: any) => w.element === dmWx)?.count || 0;
  if (count >= 3) return '强';
  if (count <= 1) return '弱';
  return '中和';
}

// Mock API: 排盘
export async function mockPaiPan(input: PaiPanInput): Promise<PaiPanResult> {
  await delay(800);

  if (input.paipanMode === 'full') {
    // 全排模式：实时计算真实数据
    const [year, month, day] = input.birthDate.split('-').map(Number);
    const [hour, minute] = input.birthTime.split(':').map(Number);
    const gender = input.gender as '男' | '女';

    const full = calculateFullBazi(year, month, day, hour, minute, gender);
    const dayun = calculateDaYun(
      input.birthDate, gender,
      { tiangan: full.monthPillar.tiangan, dizhi: full.monthPillar.dizhi },
      full.dayMaster
    );
    const currentYear = new Date().getFullYear();
    const liunian = calculateLiuNian(currentYear, currentYear + 10, full.dayMaster);
    const tongyun = calculateTongYun(input.birthDate, gender, full.dayMaster);
    const shensha = calculateShenShaFromBazi(
      { tiangan: full.yearPillar.tiangan, dizhi: full.yearPillar.dizhi },
      { tiangan: full.monthPillar.tiangan, dizhi: full.monthPillar.dizhi },
      { tiangan: full.dayPillar.tiangan, dizhi: full.dayPillar.dizhi },
      { tiangan: full.hourPillar.tiangan, dizhi: full.hourPillar.dizhi },
      full.dayMaster
    );

    const sizhu = {
      year: {
        tiangan: full.yearPillar.tiangan,
        dizhi: full.yearPillar.dizhi,
        canggan: full.yearPillar.tiangan ? [] : []
      },
      month: {
        tiangan: full.monthPillar.tiangan,
        dizhi: full.monthPillar.dizhi,
        canggan: []
      },
      day: {
        tiangan: full.dayPillar.tiangan,
        dizhi: full.dayPillar.dizhi,
        canggan: []
      },
      hour: {
        tiangan: full.hourPillar.tiangan,
        dizhi: full.hourPillar.dizhi,
        canggan: []
      }
    };

    return {
      input,
      sizhu,
      wuxing: calcWuXing(sizhu),
      dayMaster: full.dayMaster,
      dayMasterStrength: calcDayMasterStrength(sizhu),
      analysis: mockPaiPanResult.analysis,
      // 全排专属
      taiyuan: full.taiyuan,
      minggong: full.minggong,
      shengong: full.shengong,
      dayun,
      liunian,
      tongyun,
      shensha,
      emptyPosition: []
    };
  }

  // 普通式：返回静态mock
  return {
    ...mockPaiPanResult,
    input
  };
}

// 城市数据库（部分中国主要城市）
export const cityDatabase = [
  { name: '北京', longitude: 116.4074, latitude: 39.9042 },
  { name: '上海', longitude: 121.4737, latitude: 31.2304 },
  { name: '广州', longitude: 113.2644, latitude: 23.1291 },
  { name: '深圳', longitude: 114.0579, latitude: 22.5431 },
  { name: '成都', longitude: 104.0665, latitude: 30.5723 },
  { name: '杭州', longitude: 120.1614, latitude: 30.2936 },
  { name: '武汉', longitude: 114.3054, latitude: 30.5931 },
  { name: '西安', longitude: 108.9398, latitude: 34.3416 },
  { name: '南京', longitude: 118.7969, latitude: 32.0603 },
  { name: '重庆', longitude: 106.5049, latitude: 29.5332 },
  { name: '天津', longitude: 117.1900, latitude: 39.0842 },
  { name: '苏州', longitude: 120.5853, latitude: 31.2989 },
  { name: '长沙', longitude: 112.9388, latitude: 28.2282 },
  { name: '郑州', longitude: 113.6254, latitude: 34.7466 },
  { name: '沈阳', longitude: 123.4315, latitude: 41.8057 },
  { name: '哈尔滨', longitude: 126.5354, latitude: 45.8025 },
  { name: '昆明', longitude: 102.8329, latitude: 24.8801 },
  { name: '贵阳', longitude: 106.7135, latitude: 26.5783 },
  { name: '福州', longitude: 119.3064, latitude: 26.0745 },
  { name: '厦门', longitude: 118.1689, latitude: 24.4798 }
];