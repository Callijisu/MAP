// src/components/common/Button.jsx
import React from 'react';

const Button = ({ children, onClick, disabled, className = '' }) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        w-full py-4 rounded-xl font-bold text-lg text-white shadow-md transition-all 
        transform active:scale-95 bg-blue-600 hover:bg-blue-700 
        disabled:bg-gray-300 disabled:cursor-not-allowed ${className}
      `}
    >
      {children}
    </button>
  );
};
export default Button;