import React from 'react';

const ProgressBar = ({ currentStep, totalSteps }) => {
  // 진행률 계산 (예: 1단계/3단계 = 33%)
  const progress = (currentStep / totalSteps) * 100;

  return (
    <div className="w-full bg-gray-200 rounded-full h-2.5 mb-6">
      <div 
        className="bg-blue-600 h-2.5 rounded-full transition-all duration-500 ease-out" 
        style={{ width: `${progress}%` }}
      ></div>
      <div className="text-right text-xs text-gray-500 mt-1">
        {currentStep} / {totalSteps} 단계
      </div>
    </div>
  );
};

// 👇 이 줄이 없어서 에러가 난 겁니다! 꼭 넣어주세요.
export default ProgressBar;