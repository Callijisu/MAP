import React from 'react';
import { Link } from 'react-router-dom';
import { FaSearch, FaRobot, FaCheckCircle, FaDatabase, FaArrowRight } from 'react-icons/fa';

const Home = () => {
  return (
    <div className="min-h-screen bg-white flex flex-col font-sans">
      {/* 1. 네비게이션 바 */}
      <nav className="w-full bg-white/80 backdrop-blur-md border-b border-gray-100 fixed top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex-shrink-0 flex items-center gap-2 cursor-pointer">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white text-lg font-bold">Y</div>
              <span className="text-xl font-bold text-gray-900 tracking-tight">온통청년<span className="text-blue-600">AI</span></span>
            </div>
            <div className="hidden md:flex space-x-8 items-center">
              <a href="#" className="text-gray-500 hover:text-blue-600 font-medium transition">정책 둘러보기</a>
              <a href="#" className="text-gray-500 hover:text-blue-600 font-medium transition">커뮤니티</a>
              <Link to="/survey">
                <button className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-full font-bold transition shadow-lg shadow-blue-200">
                  시작하기
                </button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* 2. Hero Section (메인 배너) */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-blue-50 via-white to-indigo-50">
        <div className="max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-white border border-blue-100 px-4 py-1.5 rounded-full shadow-sm mb-8 animate-fade-in-up">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
            <span className="text-sm font-semibold text-blue-800">v1.0 업데이트: 1,604개 정책 데이터 탑재 완료</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-extrabold text-gray-900 tracking-tight leading-tight mb-8">
            나에게 딱 맞는 정책자금 <br className="hidden md:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">AI가 1초 만에</span> 찾아드려요
          </h1>
          
          <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto leading-relaxed">
            복잡한 공고문 읽다가 지치셨나요? <br />
            나이, 거주지, 관심사만 알려주세요. <strong>Agent AI</strong>가 
            신청 가능한 정책만 쏙 골라 추천해 드립니다.
          </p>
          
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link to="/survey">
              <button className="w-full sm:w-auto flex items-center justify-center gap-2 bg-blue-600 text-white px-8 py-4 rounded-xl text-lg font-bold shadow-xl shadow-blue-200 hover:bg-blue-700 hover:scale-105 transition transform">
                <FaSearch /> 내 맞춤 정책 찾기
              </button>
            </Link>
            <button className="w-full sm:w-auto flex items-center justify-center gap-2 bg-white text-gray-700 border border-gray-200 px-8 py-4 rounded-xl text-lg font-bold hover:bg-gray-50 hover:border-gray-300 transition">
              <FaDatabase /> 전체 리스트 보기
            </button>
          </div>
        </div>
      </section>

      {/* 3. 통계 섹션 (Data Stats) */}
      <section className="bg-white border-y border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center divide-x divide-gray-100">
            <div>
              <div className="text-4xl font-black text-gray-900 mb-1">1,604<span className="text-blue-600">+</span></div>
              <div className="text-sm font-medium text-gray-500 uppercase tracking-wide">실시간 정책 데이터</div>
            </div>
            <div>
              <div className="text-4xl font-black text-gray-900 mb-1">98<span className="text-blue-600">%</span></div>
              <div className="text-sm font-medium text-gray-500 uppercase tracking-wide">매칭 정확도</div>
            </div>
            <div>
              <div className="text-4xl font-black text-gray-900 mb-1">0<span className="text-blue-600">원</span></div>
              <div className="text-sm font-medium text-gray-500 uppercase tracking-wide">서비스 이용료</div>
            </div>
            <div>
              <div className="text-4xl font-black text-gray-900 mb-1">24<span className="text-blue-600">h</span></div>
              <div className="text-sm font-medium text-gray-500 uppercase tracking-wide">AI 상시 대기중</div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. 서비스 특징 (Features) */}
      <section className="py-24 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">왜 '온통청년AI'를 써야 할까요?</h2>
            <p className="text-gray-600 text-lg">단순 검색이 아닙니다. Agent가 당신의 상황을 이해하고 분석합니다.</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-xl transition duration-300">
              <div className="w-14 h-14 bg-blue-100 rounded-xl flex items-center justify-center text-blue-600 text-2xl mb-6">
                <FaRobot />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">AI Agent 자동 분석</h3>
              <p className="text-gray-600 leading-relaxed">
                사용자의 자격 요건과 수천 개의 공고를 실시간으로 대조하여 
                <span className="font-semibold text-blue-600"> 지원 가능 확률</span>을 계산해 드립니다.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-xl transition duration-300">
              <div className="w-14 h-14 bg-indigo-100 rounded-xl flex items-center justify-center text-indigo-600 text-2xl mb-6">
                <FaDatabase />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">압도적인 데이터 커버리지</h3>
              <p className="text-gray-600 leading-relaxed">
                온통청년 API는 기본! K-Startup, 지자체 포털까지 통합하여 
                <span className="font-semibold text-indigo-600"> 국내 최대 규모</span>의 DB를 구축했습니다.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-100 hover:shadow-xl transition duration-300">
              <div className="w-14 h-14 bg-teal-100 rounded-xl flex items-center justify-center text-teal-600 text-2xl mb-6">
                <FaCheckCircle />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">놓치지 않는 맞춤 알림</h3>
              <p className="text-gray-600 leading-relaxed">
                신청 마감일이 임박했나요? 
                나에게 딱 맞는 혜택을 놓치지 않도록 <span className="font-semibold text-teal-600">골든타임 알림</span>을 보내드립니다.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 5. CTA Section (하단 강조) */}
      <section className="py-20 px-4">
        <div className="max-w-5xl mx-auto bg-blue-600 rounded-3xl p-12 text-center text-white shadow-2xl">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">지금 바로 내 지원금을 확인해보세요</h2>
          <p className="text-blue-100 text-lg mb-10">회원가입 없이 1분이면 충분합니다. 1,604개의 정책이 당신을 기다립니다.</p>
          <Link to="/survey">
            <button className="bg-white text-blue-700 px-10 py-4 rounded-xl text-lg font-bold hover:bg-gray-100 transition shadow-lg inline-flex items-center gap-2">
              무료로 시작하기 <FaArrowRight />
            </button>
          </Link>
        </div>
      </section>

      {/* 6. Footer */}
      <footer className="bg-gray-50 border-t border-gray-200 py-12">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-gray-400 mb-4">© 2025 Youth Policy AI. All rights reserved.</p>
          <p className="text-sm text-gray-400">Powered by Multi-Agent System & Open Data API</p>
        </div>
      </footer>
    </div>
  );
};

export default Home;