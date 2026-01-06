import React, { useState, useEffect } from 'react';
import { useLocation, Link } from 'react-router-dom';
import Papa from 'papaparse'; 
import { FaExternalLinkAlt, FaArrowLeft, FaCalendarAlt, FaMapMarkerAlt, FaInfoCircle, FaSearch } from 'react-icons/fa';

const Result = () => {
  const [loading, setLoading] = useState(true);
  const [policies, setPolicies] = useState([]); 
  const [error, setError] = useState(null);
  
  // ✅ [추가] 검색어 상태 관리
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    const fetchRawData = async () => {
      try {
        setLoading(true);
        const response = await fetch('/policies_raw.csv');
        
        if (!response.ok) {
          throw new Error("CSV 파일을 찾을 수 없습니다. (public 폴더를 확인해주세요)");
        }

        const csvText = await response.text();

        Papa.parse(csvText, {
          header: true, 
          skipEmptyLines: true,
          complete: (results) => {
            console.log("로드된 데이터 개수:", results.data.length);
            setPolicies(results.data);
            setLoading(false);
          },
          error: (err) => {
            setError("데이터 파싱 중 에러가 발생했습니다.");
            setLoading(false);
          }
        });

      } catch (err) {
        console.error(err);
        setError(err.message);
        setLoading(false);
      }
    };

    fetchRawData();
  }, []);

  // 헬퍼 함수
  const getField = (item, keys) => {
    if (!item) return "";
    for (const key of keys) {
      if (item[key] && item[key].trim() !== "") {
        return item[key];
      }
    }
    return "";
  };

  const formatDate = (dateStr) => {
    if (!dateStr || dateStr.length !== 8) return dateStr;
    return `${dateStr.slice(0, 4)}-${dateStr.slice(4, 6)}-${dateStr.slice(6, 8)}`;
  };

  // ✅ [핵심] 검색 필터링 로직
  // 검색어가 있으면 리스트를 걸러내고, 없으면 전체를 보여줍니다.
  const filteredPolicies = policies.filter((policy) => {
    if (searchTerm === "") return true; // 검색어 없으면 다 보여줌

    // 검색 대상 필드 추출 (제목, 지역, 내용)
    const title = getField(policy, ['polyBizSjnm', 'plcyNm', 'name', 'title']);
    const region = getField(policy, ['ctpvNm', 'plcyRgn', 'region', 'sggNm']);
    const content = getField(policy, ['polyItcnCn', 'plcyExplnCn', 'support_content']);

    // 검색어와 비교 (대소문자 무시)
    const lowerSearch = searchTerm.toLowerCase();
    
    return (
      title.toLowerCase().includes(lowerSearch) ||
      region.toLowerCase().includes(lowerSearch) ||
      content.toLowerCase().includes(lowerSearch)
    );
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
        <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mb-4"></div>
        <p className="text-gray-600 font-medium animate-pulse">최신 정책 데이터를 불러오는 중...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 font-sans pb-20">
      <nav className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center text-gray-500 hover:text-blue-600 font-bold transition">
            <FaArrowLeft className="mr-2" /> 메인으로
          </Link>
          <span className="font-bold text-lg text-blue-600">온통청년 (Raw Data)</span>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-4 pt-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            전체 정책 리스트 (<span className="text-blue-600">{filteredPolicies.length}</span> / {policies.length})
          </h1>
          
          {/* ✅ [추가] 검색창 UI */}
          <div className="relative mt-4">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <FaSearch className="text-gray-400" />
            </div>
            <input
              type="text"
              className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-xl leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 sm:text-sm shadow-sm transition"
              placeholder="지역, 정책 이름, 내용을 검색해보세요 (예: 서울, 학자금, 취업)"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div className="bg-blue-50 text-blue-700 p-3 rounded-lg text-sm flex items-center gap-2 mt-4 border border-blue-100">
            <FaInfoCircle />
            <span>
              <strong>Tip:</strong> 원하는 키워드를 입력하면 실시간으로 정책을 찾아줍니다.
            </span>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 text-red-600 p-4 rounded-xl text-center font-bold mb-8 border border-red-100">
            🚨 {error}
          </div>
        )}

        {/* 정책 리스트 (필터링된 목록 사용) */}
        <div className="space-y-4">
          {filteredPolicies.map((policy, index) => {
            const title = getField(policy, ['polyBizSjnm', 'plcyNm', 'name', 'title']) || '제목 없음';
            
            const regionMain = getField(policy, ['ctpvNm', 'plcyRgn', 'region']);
            const regionSub = getField(policy, ['sggNm']); 
            const region = regionSub ? `${regionMain} ${regionSub}` : (regionMain || '전국/기타');

            const startDate = getField(policy, ['bizPrdBgngYmd', 'start_date']);
            const endDate = getField(policy, ['bizPrdEndYmd', 'end_date']);
            const periodText = getField(policy, ['rqutPrdCn', 'plcyPrdCn']);
            
            let periodDisplay = "기간 정보 없음";
            if (startDate && endDate) {
              periodDisplay = `${formatDate(startDate)} ~ ${formatDate(endDate)}`;
            } else if (periodText) {
              periodDisplay = periodText;
            }

            const desc = getField(policy, ['polyItcnCn', 'plcyExplnCn', 'support_content']) || '상세 내용은 상세보기를 참조하세요.';
            const url = getField(policy, ['rqutUrla', 'etct', 'url', 'polyBizSecdUrl']);

            return (
              <div key={index} className="bg-white rounded-xl p-5 shadow-sm border border-gray-100 hover:shadow-md hover:border-blue-200 transition group">
                <div className="flex flex-col md:flex-row justify-between items-start gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded text-xs font-medium flex items-center gap-1 group-hover:bg-blue-50 group-hover:text-blue-600 transition">
                         <FaMapMarkerAlt /> {region}
                      </span>
                    </div>
                    
                    <h3 className="text-lg font-bold text-gray-900 mb-2 leading-tight break-keep group-hover:text-blue-700 transition">
                      {title}
                    </h3>
                    
                    <p className="text-sm text-gray-500 mb-3 flex items-center gap-1.5 font-medium">
                      <FaCalendarAlt className="text-gray-400" /> 
                      <span className={periodDisplay === "기간 정보 없음" ? "text-gray-400" : "text-gray-700"}>
                        {periodDisplay}
                      </span>
                    </p>
                    
                    <p className="text-sm text-gray-600 line-clamp-2 leading-relaxed">
                       {desc.replace(/<[^>]*>?/g, '')}
                    </p>
                  </div>

                  {url && (
                    <a 
                      href={url} 
                      target="_blank" 
                      rel="noreferrer"
                      className="shrink-0 w-full md:w-auto text-center bg-blue-50 text-blue-600 px-4 py-3 rounded-xl font-bold text-sm hover:bg-blue-600 hover:text-white transition flex justify-center items-center gap-2"
                    >
                      신청하기 <FaExternalLinkAlt size={12}/>
                    </a>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* 검색 결과가 없을 때 */}
        {!loading && filteredPolicies.length === 0 && (
          <div className="text-center py-20 bg-white rounded-2xl border border-dashed border-gray-300">
            <div className="text-4xl mb-3">🔍</div>
            <p className="text-gray-900 font-bold text-lg">검색 결과가 없습니다.</p>
            <p className="text-gray-500">다른 키워드로 검색해보세요.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Result;