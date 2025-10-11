import React from 'react';
import { BookOpen, Zap, Users } from 'lucide-react';

const LearnSphereLogo = ({ size = 'md', showText = true, className = '' }) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  };

  const textSizeClasses = {
    sm: 'text-lg',
    md: 'text-xl',
    lg: 'text-2xl',
    xl: 'text-3xl'
  };

  return (
    <div className={`flex items-center space-x-3 ${className}`}>
      {/* Logo Icon */}
      <div className="relative">
        {/* Main circle with gradient */}
        <div className={`${sizeClasses[size]} bg-gradient-to-br from-blue-500 via-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg hover:scale-105 transition-transform duration-300`}>
          {/* Inner icon */}
          <BookOpen className={`${size === 'sm' ? 'w-4 h-4' : size === 'md' ? 'w-5 h-5' : size === 'lg' ? 'w-6 h-6' : 'w-8 h-8'} text-white`} />
        </div>
        
        {/* Small accent dots */}
        <div className="absolute -top-1 -right-1">
          <div className="w-3 h-3 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full shadow-sm"></div>
        </div>
        <div className="absolute -bottom-1 -left-1">
          <div className="w-2 h-2 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full shadow-sm"></div>
        </div>
      </div>

      {/* Text */}
      {showText && (
        <div className="flex flex-col">
          <span className={`${textSizeClasses[size]} font-bold tracking-tight font-serif leading-none`} style={{color: '#f5edd7'}}>
            Learn<span style={{color: '#f5edd7'}}>Sphere</span>
          </span>
          {size === 'lg' || size === 'xl' ? (
            <span className="text-xs text-gray-500 font-medium tracking-wide">
              AI-Powered Learning
            </span>
          ) : null}
        </div>
      )}
    </div>
  );
};

export default LearnSphereLogo;
