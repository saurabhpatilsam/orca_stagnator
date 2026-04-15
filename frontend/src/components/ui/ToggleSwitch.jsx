/**
 * ToggleSwitch Component
 * Accessible toggle switch with keyboard support
 */

import React from 'react';

const ToggleSwitch = ({
  enabled = false,
  onChange,
  label,
  disabled = false,
  size = 'medium'
}) => {
  const handleToggle = () => {
    if (!disabled && onChange) {
      onChange(!enabled);
    }
  };

  const handleKeyDown = (e) => {
    if (disabled) return;
    
    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault();
      handleToggle();
    }
  };

  // Size classes
  const sizeClasses = {
    small: {
      track: 'h-5 w-9',
      knob: 'h-4 w-4',
      translate: 'translate-x-4'
    },
    medium: {
      track: 'h-6 w-11',
      knob: 'h-5 w-5',
      translate: 'translate-x-5'
    },
    large: {
      track: 'h-7 w-14',
      knob: 'h-6 w-6',
      translate: 'translate-x-7'
    }
  };

  const currentSize = sizeClasses[size] || sizeClasses.medium;

  return (
    <div className="flex items-center gap-3">
      <button
        type="button"
        role="switch"
        aria-checked={enabled}
        aria-label={label || 'Toggle switch'}
        disabled={disabled}
        onClick={handleToggle}
        onKeyDown={handleKeyDown}
        className={`
          relative inline-flex flex-shrink-0 ${currentSize.track} 
          border-2 border-transparent rounded-full cursor-pointer 
          transition-colors ease-in-out duration-200 
          focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 focus:ring-offset-gray-900
          ${enabled ? 'bg-purple-600' : 'bg-gray-600'}
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-opacity-90'}
        `}
      >
        <span className="sr-only">{label}</span>
        <span
          aria-hidden="true"
          className={`
            ${currentSize.knob}
            pointer-events-none inline-block rounded-full bg-white shadow-lg 
            transform ring-0 transition ease-in-out duration-200
            ${enabled ? currentSize.translate : 'translate-x-0'}
          `}
        />
      </button>
      {label && (
        <span className={`text-sm font-medium ${disabled ? 'text-gray-500' : 'text-gray-300'}`}>
          {label}
        </span>
      )}
    </div>
  );
};

export default ToggleSwitch;
