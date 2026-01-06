import axios from 'axios';

const api = axios.create({
  // FastAPI 기본 주소 (나중에 배포하면 바뀝니다)
  baseURL: 'http://localhost:8000', 
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청을 보내기 전에 가로채서 로그를 찍거나 설정을 추가하는 곳
api.interceptors.request.use((config) => {
  console.log(`[API 요청] ${config.method.toUpperCase()} ${config.url}`);
  return config;
});

// 👇 이 줄이 빠져서 에러가 난 겁니다! 꼭 넣어주세요.
export default api;