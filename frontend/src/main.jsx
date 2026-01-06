import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

// 👇 1. React Query 라이브러리 불러오기
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// 👇 2. 클라이언트 생성하기 (이 친구가 데이터를 관리합니다)
const queryClient = new QueryClient()

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    {/* 👇 3. 앱 전체를 Provider로 감싸주기 */}
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
)