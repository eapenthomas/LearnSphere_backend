import React from 'react';
import { motion } from 'framer-motion';

const LoadingSkeleton = () => {
  return (
    <div className="space-y-6">
      {/* Breadcrumb Skeleton */}
      <div className="flex items-center space-x-2">
        <div className="w-4 h-4 bg-gray-200 rounded animate-pulse"></div>
        <div className="w-16 h-4 bg-gray-200 rounded animate-pulse"></div>
        <div className="w-4 h-4 bg-gray-200 rounded animate-pulse"></div>
        <div className="w-24 h-4 bg-gray-200 rounded animate-pulse"></div>
      </div>

      {/* Header Skeleton */}
      <div className="flex items-center space-x-4">
        <div className="w-14 h-14 bg-gray-200 rounded-xl animate-pulse"></div>
        <div className="space-y-2">
          <div className="w-48 h-8 bg-gray-200 rounded animate-pulse"></div>
          <div className="w-64 h-4 bg-gray-200 rounded animate-pulse"></div>
        </div>
      </div>

      {/* Main Content Grid Skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Profile Information Card Skeleton */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6"
        >
          {/* Card Header */}
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-9 h-9 bg-gray-200 rounded-lg animate-pulse"></div>
            <div className="space-y-2">
              <div className="w-32 h-5 bg-gray-200 rounded animate-pulse"></div>
              <div className="w-40 h-3 bg-gray-200 rounded animate-pulse"></div>
            </div>
          </div>

          {/* Form Fields */}
          <div className="space-y-6">
            {/* Full Name Field */}
            <div>
              <div className="w-20 h-4 bg-gray-200 rounded animate-pulse mb-2"></div>
              <div className="w-full h-12 bg-gray-200 rounded-lg animate-pulse"></div>
            </div>

            {/* Email Field */}
            <div>
              <div className="w-24 h-4 bg-gray-200 rounded animate-pulse mb-2"></div>
              <div className="w-full h-12 bg-gray-200 rounded-lg animate-pulse"></div>
            </div>

            {/* Role Field */}
            <div>
              <div className="w-16 h-4 bg-gray-200 rounded animate-pulse mb-2"></div>
              <div className="w-full h-12 bg-gray-200 rounded-lg animate-pulse"></div>
            </div>

            {/* Phone Field */}
            <div>
              <div className="w-28 h-4 bg-gray-200 rounded animate-pulse mb-2"></div>
              <div className="w-full h-12 bg-gray-200 rounded-lg animate-pulse"></div>
            </div>

            {/* Buttons */}
            <div className="flex space-x-3 pt-4">
              <div className="flex-1 h-12 bg-gray-200 rounded-lg animate-pulse"></div>
              <div className="w-20 h-12 bg-gray-200 rounded-lg animate-pulse"></div>
            </div>
          </div>
        </motion.div>

        {/* Password Update Card Skeleton */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6"
        >
          {/* Card Header */}
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-9 h-9 bg-gray-200 rounded-lg animate-pulse"></div>
            <div className="space-y-2">
              <div className="w-32 h-5 bg-gray-200 rounded animate-pulse"></div>
              <div className="w-40 h-3 bg-gray-200 rounded animate-pulse"></div>
            </div>
          </div>

          {/* Form Fields */}
          <div className="space-y-6">
            {/* Current Password */}
            <div>
              <div className="w-28 h-4 bg-gray-200 rounded animate-pulse mb-2"></div>
              <div className="w-full h-12 bg-gray-200 rounded-lg animate-pulse"></div>
            </div>

            {/* New Password */}
            <div>
              <div className="w-24 h-4 bg-gray-200 rounded animate-pulse mb-2"></div>
              <div className="w-full h-12 bg-gray-200 rounded-lg animate-pulse"></div>
              <div className="w-full h-2 bg-gray-200 rounded-full animate-pulse mt-2"></div>
            </div>

            {/* Confirm Password */}
            <div>
              <div className="w-32 h-4 bg-gray-200 rounded animate-pulse mb-2"></div>
              <div className="w-full h-12 bg-gray-200 rounded-lg animate-pulse"></div>
            </div>

            {/* Requirements Box */}
            <div className="bg-gray-100 rounded-lg p-4">
              <div className="w-32 h-4 bg-gray-200 rounded animate-pulse mb-2"></div>
              <div className="space-y-1">
                <div className="w-40 h-3 bg-gray-200 rounded animate-pulse"></div>
                <div className="w-48 h-3 bg-gray-200 rounded animate-pulse"></div>
                <div className="w-44 h-3 bg-gray-200 rounded animate-pulse"></div>
                <div className="w-36 h-3 bg-gray-200 rounded animate-pulse"></div>
              </div>
            </div>

            {/* Submit Button */}
            <div className="w-full h-12 bg-gray-200 rounded-lg animate-pulse"></div>
          </div>
        </motion.div>
      </div>

      {/* Additional Cards Skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Security Overview Card */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6"
        >
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-9 h-9 bg-gray-200 rounded-lg animate-pulse"></div>
            <div className="w-32 h-5 bg-gray-200 rounded animate-pulse"></div>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="w-40 h-4 bg-gray-200 rounded animate-pulse"></div>
              <div className="w-20 h-4 bg-gray-200 rounded animate-pulse"></div>
            </div>
            <div className="flex items-center justify-between">
              <div className="w-32 h-4 bg-gray-200 rounded animate-pulse"></div>
              <div className="w-16 h-4 bg-gray-200 rounded animate-pulse"></div>
            </div>
            <div className="flex items-center justify-between">
              <div className="w-36 h-4 bg-gray-200 rounded animate-pulse"></div>
              <div className="w-12 h-4 bg-gray-200 rounded animate-pulse"></div>
            </div>
          </div>
        </motion.div>

        {/* Preferences Card */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6"
        >
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-9 h-9 bg-gray-200 rounded-lg animate-pulse"></div>
            <div className="w-24 h-5 bg-gray-200 rounded animate-pulse"></div>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="w-36 h-4 bg-gray-200 rounded animate-pulse"></div>
              <div className="w-16 h-4 bg-gray-200 rounded animate-pulse"></div>
            </div>
            <div className="flex items-center justify-between">
              <div className="w-20 h-4 bg-gray-200 rounded animate-pulse"></div>
              <div className="w-12 h-4 bg-gray-200 rounded animate-pulse"></div>
            </div>
            <div className="flex items-center justify-between">
              <div className="w-24 h-4 bg-gray-200 rounded animate-pulse"></div>
              <div className="w-16 h-4 bg-gray-200 rounded animate-pulse"></div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default LoadingSkeleton;
