// src/App.jsx
import React from 'react';
import Survey from './pages/Survey'; 

function App() {
  return (
    // 라우터 없이 일단 바로 Survey 페이지만 보여줍니다.
    <div>
      <Survey />
    </div>
  );
}

export default App;