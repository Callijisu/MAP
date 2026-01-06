// src/pages/Survey.jsx
import React from 'react';
import ProfileWizard from '../components/domain/profile/ProfileWizard';

const Survey = () => {
  return (
    <div className="bg-gray-50 min-h-screen flex items-center justify-center">
      {/* 설문조사 위자드 컨테이너 */}
      <div className="w-full h-full bg-white shadow-xl sm:rounded-3xl sm:max-w-md sm:h-auto sm:overflow-hidden">
        <ProfileWizard />
      </div>
    </div>
  );
};

export default Survey;