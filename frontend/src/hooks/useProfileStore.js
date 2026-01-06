import { create } from 'zustand';

const useProfileStore = create((set) => ({
  // 1. 저장할 데이터들
  userProfile: {
    age: '',        // 출생연도
    region: '',     // 거주지
    status: '',     // 취업 상태 (재학, 미취업, 창업 등)
    income: '',     // 소득 구간
    favKeywords: [] // 관심 키워드
  },
  
  // 2. 현재 단계 (Wizard Step)
  currentStep: 1,

  // 3. 데이터를 바꾸는 함수들 (Actions)
  setProfile: (key, value) => set((state) => ({
    userProfile: { ...state.userProfile, [key]: value }
  })),

  nextStep: () => set((state) => ({ currentStep: state.currentStep + 1 })),
  prevStep: () => set((state) => ({ currentStep: state.currentStep - 1 })),
  
  // 초기화 함수 (나중에 쓸 수 있음)
  resetStep: () => set({ 
    currentStep: 1, 
    userProfile: { age: '', region: '', status: '', income: '', favKeywords: [] } 
  }),
}));

// 👇 이 줄이 없으면 에러가 납니다! 꼭 넣어주세요.
export default useProfileStore;