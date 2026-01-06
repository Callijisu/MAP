import React, { useState } from 'react';
import useProfileStore from '../../../hooks/useProfileStore';
import Input from '../../common/Input';
import Button from '../../common/Button';

const StepBasic = () => {
  const { userProfile, setProfile, nextStep } = useProfileStore();
  const [errors, setErrors] = useState({});

  const validate = () => {
    let newErrors = {};
    const birthYear = parseInt(userProfile.age, 10);

    if (!userProfile.age) {
      newErrors.age = "태어난 연도를 입력해주세요.";
    } else if (birthYear < 1980 || birthYear > 2010) {
      newErrors.age = "1980년~2010년생 사이만 조회가 가능해요.";
    }

    if (!userProfile.region) {
      newErrors.region = "거주하시는 지역을 선택해주세요.";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validate()) nextStep();
  };

  return (
    <div className="flex flex-col h-full animate-fadeIn">
      <h2 className="text-xl font-bold mb-1 text-gray-800">기본 정보를 알려주세요 👋</h2>
      <p className="text-gray-500 mb-8 text-sm">딱 맞는 정책을 찾기 위해 필요해요.</p>

      <Input
        label="태어난 연도 (4자리)"
        type="number"
        placeholder="예) 1999"
        value={userProfile.age}
        onChange={(e) => {
          const val = e.target.value.slice(0, 4);
          setProfile('age', val);
          if(errors.age) setErrors({...errors, age: ''});
        }}
        error={errors.age}
      />

      <div className="flex flex-col mb-8 w-full">
        <label className="text-sm font-semibold text-gray-700 mb-1.5 ml-1">현재 거주지</label>
        <div className="relative">
          <select
            className={`w-full px-4 py-3 rounded-xl border-2 outline-none appearance-none bg-white text-gray-800 text-base transition-colors ${errors.region ? 'border-red-500' : 'border-gray-200 focus:border-blue-500'}`}
            value={userProfile.region}
            onChange={(e) => {
              setProfile('region', e.target.value);
              setErrors({...errors, region: ''});
            }}
          >
            <option value="" disabled>지역을 선택해주세요</option>
            <option value="서울">서울</option>
            <option value="경기">경기</option>
            <option value="인천">인천</option>
            <option value="부산">부산</option>
            {/* 필요한 지역 추가 */}
          </select>
        </div>
        {errors.region && <span className="text-xs text-red-500 mt-1 ml-1">🚨 {errors.region}</span>}
      </div>

      <div className="mt-auto">
        <Button onClick={handleNext}>다음으로</Button>
      </div>
    </div>
  );
};

// 👇 이 줄이 없으면 에러가 납니다!
export default StepBasic;