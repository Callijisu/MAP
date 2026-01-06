// src/components/common/Input.jsx
import React from 'react';

const Input = ({ label, error, helperText, ...props }) => {
  return (
    <div className="flex flex-col mb-4 w-full">
      {label && (
        <label className="text-sm font-semibold text-gray-700 mb-1.5 ml-1">
          {label}
        </label>
      )}
      <input
        className={`
          w-full px-4 py-3 rounded-xl border-2 outline-none transition-all duration-200
          text-gray-800 placeholder-gray-400 text-base
          ${error 
            ? 'border-red-500 focus:border-red-500 bg-red-50' 
            : 'border-gray-200 focus:border-blue-500 bg-white'
          }
        `}
        {...props}
      />
      {error && (
        <span className="text-xs text-red-500 mt-1 ml-1">🚨 {error}</span>
      )}
    </div>
  );
};
export default Input;