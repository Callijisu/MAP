// src/hooks/useAgentVerify.js
import { useMutation } from '@tanstack/react-query';
import api from '../services/api';

// 👇 실제 서버 대신 응답해줄 가짜 데이터 (Mock Data)
const MOCK_RESPONSE = {
  status: "success",
  message: "맞춤형 정책 3건을 찾았습니다.",
  data: [
    { id: 1, title: "청년 월세 지원", amount: "월 20만원" },
    { id: 2, title: "청년 도약 계좌", amount: "최대 5,000만원" },
    { id: 3, title: "기후동행카드 청년 할인", amount: "월 7,000원 할인" }
  ]
};

const verifyProfileApi = async (profileData) => {
  // 원래 코드는 주석 처리
  // const response = await api.post('/api/v1/agent/validate', profileData);
  // return response.data;

  // 👇 2초 뒤에 무조건 성공하는 가짜 약속(Promise) 생성
  return new Promise((resolve) => {
    setTimeout(() => {
      console.log("📢 [Mock] 가짜 데이터 전송 완료!");
      resolve(MOCK_RESPONSE);
    }, 2000); // 2초 딜레이 (로딩 화면 구경용)
  });
};

export const useAgentVerify = () => {
  return useMutation({
    mutationFn: verifyProfileApi,
    onSuccess: (data) => {
      console.log('검증 성공:', data);
    },
    onError: (error) => {
      console.error('검증 실패:', error);
    },
  });
};