// src/components/domain/profile/StepResult.jsx
import React, { useEffect } from 'react';
import useProfileStore from '../../../hooks/useProfileStore';
import { useAgentVerify } from '../../../hooks/useAgentVerify';
import Button from '../../common/Button';

const StepResult = () => {
  const { userProfile, prevStep } = useProfileStore();
  const { mutate, isPending, isError, isSuccess, data, error } = useAgentVerify();

  // 컴포넌트가 화면에 뜨자마자(마운트) 검증 요청 시작!
  useEffect(() => {
    if (!isSuccess && !isError) { // 이미 결과가 나온 상태가 아니면 요청
      mutate(userProfile);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 1. 로딩 중 (AI 분석 중)
  if (isPending) {
    return (
      <div className="flex flex-col items-center justify-center h-full animate-fadeIn py-10">
        {/* 빙글빙글 도는 스피너 UI */}
        <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-6"></div>
        <h2 className="text-xl font-bold text-gray-800 mb-2">Agent가 프로필을 분석 중입니다...</h2>
        <p className="text-gray-500 text-center">
          {userProfile.region}에 사는 {userProfile.age}년생 청년에게<br/>
          딱 맞는 혜택을 찾고 있어요! 🕵️‍♂️
        </p>
      </div>
    );
  }

  // 2. 에러 발생 (백엔드 연결 실패 등)
  if (isError) {
    return (
      <div className="flex flex-col h-full animate-fadeIn items-center text-center pt-8">
        <div className="text-5xl mb-4">😵</div>
        <h2 className="text-xl font-bold text-red-500 mb-2">분석에 실패했어요</h2>
        <p className="text-gray-500 mb-8 text-sm break-keep">
          서버와 연결할 수 없거나 문제가 발생했습니다.<br/>
          ({error?.message || '알 수 없는 오류'})
        </p>
        <div className="mt-auto w-full gap-3 flex">
          <Button onClick={prevStep} variant="outline" className="w-1/3 bg-gray-100 text-gray-600 border-none">
            뒤로
          </Button>
          <Button onClick={() => mutate(userProfile)} className="w-2/3">
            다시 시도하기
          </Button>
        </div>
      </div>
    );
  }

  // 3. 성공 (검증 완료)
  if (isSuccess) {
    return (
      <div className="flex flex-col h-full animate-fadeIn items-center text-center pt-8">
        <div className="text-6xl mb-4">🎉</div>
        <h2 className="text-2xl font-bold text-gray-800 mb-2">분석 완료!</h2>
        <p className="text-gray-600 mb-8">
          윤후님에게 딱 맞는<br/>
          <span className="font-bold text-blue-600">맞춤 정책 리스트</span>가 준비되었습니다.
        </p>
        
        {/* 결과 데이터가 있다면 여기에 요약 표시 가능 */}
        {/* <div className="bg-gray-50 p-4 rounded-xl w-full mb-6 text-left">
            <p className="font-bold">💡 Agent 코멘트:</p>
            <p className="text-sm text-gray-600">{data?.message || "조건에 맞는 정책을 찾았습니다."}</p>
        </div> */}

        <div className="mt-auto w-full">
          <Button onClick={() => alert('이제 진짜 정책 리스트 페이지로 이동하면 됩니다!')}>
            결과 보러 가기 👉
          </Button>
        </div>
      </div>
    );
  }

  return null;
};

export default StepResult;