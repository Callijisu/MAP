// src/components/domain/profile/ProfileWizard.jsx
import React from 'react';
import useProfileStore from '../../../hooks/useProfileStore';
import ProgressBar from '../../common/ProgressBar';

// 각 단계별 컴포넌트 임포트
import StepBasic from './StepBasic';
import StepStatus from './StepStatus';
import StepResult from './StepResult'; // 아직 내용이 없어도 파일만 있으면 에러 안 남

const ProfileWizard = () => {
  // 1. Zustand에서 현재 단계(currentStep) 가져오기
  const { currentStep } = useProfileStore();

  // 2. 단계에 따라 보여줄 화면 결정하는 함수
  const renderStep = () => {
    switch(currentStep) {
      case 1: return <StepBasic />;
      case 2: return <StepStatus />;
      case 3: return <StepResult />;
      default: return <StepBasic />;
    }
  };

  return (
    <div className="w-full max-w-lg mx-auto p-6 min-h-[80vh] flex flex-col">
      {/* 상단: 진행률 표시바 (총 3단계) */}
      <ProgressBar currentStep={currentStep} totalSteps={3} />

      {/* 메인: 단계별 질문 화면 */}
      <div className="flex-1 mt-4 animate-fadeIn">
        {renderStep()}
      </div>
    </div>
  );
};

export default ProfileWizard;