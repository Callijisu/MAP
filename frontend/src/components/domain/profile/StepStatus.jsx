// src/components/domain/profile/StepStatus.jsx
import React, { useState } from 'react';
import useProfileStore from '../../../hooks/useProfileStore';
import Button from '../../common/Button';

const StepStatus = () => {
  const { userProfile, setProfile, nextStep, prevStep } = useProfileStore();
  const [error, setError] = useState('');

  // 선택지 목록 (온통청년 정책 분류 기준)
  const statusOptions = [
    { label: '🎓 대학생/대학원생', value: '재학' },
    { label: '💼 취업 준비생 (미취업)', value: '미취업' },
    { label: '🏢 직장인 (재직자)', value: '재직' },
    { label: '🚀 창업/프리랜서', value: '창업' },
    { label: '🏠 단기근로/아르바이트', value: '단기근로' },
  ];

  // 옵션 선택 핸들러
  const handleSelect = (value) => {
    setProfile('status', value);
    setError(''); // 선택하면 에러 메시지 삭제
  };

  const handleNext = () => {
    if (!userProfile.status) {
      setError('현재 본인에게 해당하는 상태를 하나 선택해주세요!');
      return;
    }
    nextStep();
  };

  return (
    <div className="flex flex-col h-full animate-fadeIn">
      <h2 className="text-xl font-bold mb-1 text-gray-800">현재 어떤 상황이신가요? 🤔</h2>
      <p className="text-gray-500 mb-6 text-sm">상황에 딱 맞는 지원금을 찾아드릴게요.</p>

      {/* 선택 버튼 그리드 (2열 배치) */}
      <div className="grid grid-cols-1 gap-3 mb-4">
        {statusOptions.map((option) => (
          <button
            key={option.value}
            onClick={() => handleSelect(option.value)}
            className={`
              p-4 rounded-xl border-2 text-left transition-all duration-200 flex items-center
              ${userProfile.status === option.value
                ? 'border-blue-500 bg-blue-50 text-blue-700 font-bold shadow-md transform scale-[1.02]'
                : 'border-gray-200 bg-white text-gray-600 hover:border-blue-200 hover:bg-gray-50'
              }
            `}
          >
            {/* 라디오 버튼 모양 UI (장식용) */}
            <div className={`
              w-5 h-5 rounded-full border-2 mr-3 flex items-center justify-center
              ${userProfile.status === option.value ? 'border-blue-500' : 'border-gray-300'}
            `}>
              {userProfile.status === option.value && (
                <div className="w-2.5 h-2.5 rounded-full bg-blue-500" />
              )}
            </div>
            <span className="text-lg">{option.label}</span>
          </button>
        ))}
      </div>

      {/* 에러 메시지 */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-500 text-sm rounded-lg flex items-center animate-pulse">
          🚨 {error}
        </div>
      )}

      {/* 하단 버튼 영역 (이전 / 다음) */}
      <div className="mt-auto flex gap-3">
        {/* 이전 버튼: 중요도가 낮으므로 회색/흰색 스타일 적용 */}
        <button 
          onClick={prevStep}
          className="w-1/3 py-4 rounded-xl font-bold text-gray-500 bg-gray-100 hover:bg-gray-200 transition-colors"
        >
          이전
        </button>
        
        <Button onClick={handleNext} className="w-2/3">
          다음으로
        </Button>
      </div>
    </div>
  );
};

export default StepStatus;