import { create } from 'zustand';
import { PaiPanInput, PaiPanResult } from '@/types/bazi';
import { paiPan } from '@/services/baziService';

// 应用状态接口
interface AppState {
  // 加载状态
  loading: boolean;
  setLoading: (loading: boolean) => void;
  
  // 排盘输入
  input: PaiPanInput;
  setInput: (input: Partial<PaiPanInput>) => void;
  resetInput: () => void;
  
  // 排盘结果
  result: PaiPanResult | null;
  setResult: (result: PaiPanResult | null) => void;
  
  // 错误信息
  error: string | null;
  setError: (error: string | null) => void;
  
  // 操作：提交排盘
  submitPaiPan: () => Promise<void>;
  
  // UI状态
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

// 默认输入
const defaultInput: PaiPanInput = {
  name: '',
  gender: '男',
  birthDate: '',
  birthTime: '',
  birthPlace: '',
  paipanMode: 'simple'
};

// 创建Store
export const useAppStore = create<AppState>((set, get) => ({
  // 初始状态
  loading: false,
  input: { ...defaultInput },
  result: null,
  error: null,
  activeTab: 'input',
  
  // Actions
  setLoading: (loading) => set({ loading }),
  
  setInput: (partial) => set((state) => ({
    input: { ...state.input, ...partial }
  })),
  
  resetInput: () => set({ input: { ...defaultInput } }),
  
  setResult: (result) => set({ result }),
  
  setError: (error) => set({ error }),
  
  setActiveTab: (tab) => set({ activeTab: tab }),
  
  // 提交排盘
  submitPaiPan: async () => {
    const { input } = get();
    
    // 验证输入
    if (!input.name.trim()) {
      set({ error: '请输入姓名' });
      return;
    }
    
    if (!input.birthDate) {
      set({ error: '请选择出生日期' });
      return;
    }
    
    if (!input.birthTime) {
      set({ error: '请选择出生时间' });
      return;
    }
    
    if (!input.birthPlace.trim()) {
      set({ error: '请输入出生地点' });
      return;
    }
    
    // 开始加载
    set({ loading: true, error: null });
    
    try {
      const response = await paiPan(input);
      
      if (response.success && response.data) {
        set({
          result: response.data,
          loading: false,
          activeTab: 'result'
        });
      } else {
        set({
          error: response.message || '排盘失败',
          loading: false
        });
      }
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : '排盘失败，请稍后重试',
        loading: false
      });
    }
  }
}));
