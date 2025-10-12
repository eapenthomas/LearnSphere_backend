import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { toast } from 'react-hot-toast';
import axios from 'axios';
import {
  Shield,
  ArrowLeft,
  Loader,
  Eye,
  EyeOff,
  CheckCircle,
  RefreshCw
} from 'lucide-react';

// API base URL
const API_BASE_URL = 'http://localhost:8000';

// Validation schema
const otpSchema = yup.object().shape({
  otp: yup
    .string()
    .required('Verification code is required')
    .matches(/^\d{6}$/, 'Code must be exactly 6 digits'),
  newPassword: yup
    .string()
    .required('New password is required')
    .min(8, 'Password must be at least 8 characters')
    .matches(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      'Password must contain at least one uppercase letter, one lowercase letter, and one number'
    ),
  confirmPassword: yup
    .string()
    .required('Please confirm your new password')
    .oneOf([yup.ref('newPassword')], 'Passwords must match')
});

const OTPVerification = ({ email, onBack, onSuccess, onResend }) => {
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [otpValues, setOtpValues] = useState(['', '', '', '', '', '']);
  const otpRefs = useRef([]);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch
  } = useForm({
    resolver: yupResolver(otpSchema),
    mode: 'onChange'
  });

  const watchedOtp = watch('otp');

  // Handle OTP input
  const handleOtpChange = (index, value) => {
    if (value.length > 1) return; // Prevent multiple characters
    
    const newOtpValues = [...otpValues];
    newOtpValues[index] = value;
    setOtpValues(newOtpValues);
    
    // Update form value
    const otpString = newOtpValues.join('');
    setValue('otp', otpString);
    
    // Auto-focus next input
    if (value && index < 5) {
      otpRefs.current[index + 1]?.focus();
    }
  };

  // Handle backspace
  const handleOtpKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !otpValues[index] && index > 0) {
      otpRefs.current[index - 1]?.focus();
    }
  };

  // Handle paste
  const handleOtpPaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
    const newOtpValues = pastedData.split('').concat(Array(6).fill('')).slice(0, 6);
    setOtpValues(newOtpValues);
    setValue('otp', pastedData);
    
    // Focus the next empty input or the last one
    const nextEmptyIndex = newOtpValues.findIndex(val => !val);
    const focusIndex = nextEmptyIndex === -1 ? 5 : nextEmptyIndex;
    otpRefs.current[focusIndex]?.focus();
  };

  const onSubmit = async (data) => {
    setLoading(true);
    
    try {
      console.log('Verifying OTP and resetting password...');
      
      const response = await axios.post(`${API_BASE_URL}/verify-otp-reset`, {
        email: email,
        otp_code: data.otp,
        new_password: data.newPassword
      });

      if (response.data) {
        toast.success('Password reset successfully!');
        
        if (onSuccess) {
          onSuccess();
        }
      }
    } catch (error) {
      console.error('OTP verification error:', error);
      
      const errorMessage = error.response?.data?.detail || error.message;
      
      if (errorMessage.includes('Invalid or expired')) {
        toast.error('Invalid or expired verification code. Please try again.');
      } else if (errorMessage.includes('expired')) {
        toast.error('Verification code has expired. Please request a new one.');
      } else {
        toast.error('Failed to reset password. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleResendCode = async () => {
    try {
      await axios.post(`${API_BASE_URL}/forgot-password`, { email });
      toast.success('New verification code sent!');
      
      // Clear current OTP
      setOtpValues(['', '', '', '', '', '']);
      setValue('otp', '');
      otpRefs.current[0]?.focus();
      
      if (onResend) {
        onResend();
      }
    } catch (error) {
      toast.error('Failed to resend code. Please try again.');
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      {/* Header */}
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Shield className="w-8 h-8 text-blue-600" />
        </div>
        
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Enter Verification Code
        </h2>
        
        <p className="text-gray-600 mb-2">
          We sent a 6-digit code to:
        </p>
        
        <p className="text-lg font-semibold text-blue-600">
          {email}
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* OTP Input */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-3 text-center">
            Verification Code
          </label>
          <div className="flex justify-center space-x-3 mb-4">
            {otpValues.map((value, index) => (
              <input
                key={index}
                ref={el => otpRefs.current[index] = el}
                type="text"
                inputMode="numeric"
                maxLength={1}
                value={value}
                onChange={(e) => handleOtpChange(index, e.target.value.replace(/\D/g, ''))}
                onKeyDown={(e) => handleOtpKeyDown(index, e)}
                onPaste={handleOtpPaste}
                className={`
                  w-12 h-12 text-center text-xl font-bold border rounded-lg
                  focus:outline-none focus:ring-2 focus:border-transparent
                  ${errors.otp 
                    ? 'border-red-300 focus:ring-red-400' 
                    : 'border-gray-200 focus:ring-blue-400'
                  }
                `}
              />
            ))}
          </div>
          {errors.otp && (
            <p className="text-sm text-red-600 text-center">{errors.otp.message}</p>
          )}
          
          <div className="text-center">
            <button
              type="button"
              onClick={handleResendCode}
              className="text-blue-600 hover:text-blue-700 font-medium text-sm flex items-center justify-center mx-auto"
            >
              <RefreshCw className="w-4 h-4 mr-1" />
              Resend Code
            </button>
          </div>
        </div>

        {/* New Password */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            New Password
          </label>
          <div className="relative">
            <input
              type={showPassword ? 'text' : 'password'}
              {...register('newPassword')}
              className={`
                w-full pr-12 pl-4 py-3 border rounded-lg transition-all duration-200
                focus:outline-none focus:ring-2 focus:border-transparent bg-white text-gray-800
                ${errors.newPassword 
                  ? 'border-red-300 focus:ring-red-400' 
                  : 'border-gray-200 focus:ring-blue-400'
                }
              `}
              placeholder="Enter new password"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          </div>
          {errors.newPassword && (
            <p className="mt-2 text-sm text-red-600">{errors.newPassword.message}</p>
          )}
        </div>

        {/* Confirm Password */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Confirm New Password
          </label>
          <div className="relative">
            <input
              type={showConfirmPassword ? 'text' : 'password'}
              {...register('confirmPassword')}
              className={`
                w-full pr-12 pl-4 py-3 border rounded-lg transition-all duration-200
                focus:outline-none focus:ring-2 focus:border-transparent bg-white text-gray-800
                ${errors.confirmPassword 
                  ? 'border-red-300 focus:ring-red-400' 
                  : 'border-gray-200 focus:ring-blue-400'
                }
              `}
              placeholder="Confirm new password"
            />
            <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          </div>
          {errors.confirmPassword && (
            <p className="mt-2 text-sm text-red-600">{errors.confirmPassword.message}</p>
          )}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className={`
            w-full py-3 px-4 rounded-lg font-semibold text-white transition-all duration-200
            ${loading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:ring-blue-200'
            }
          `}
        >
          {loading ? (
            <div className="flex items-center justify-center">
              <Loader className="w-5 h-5 animate-spin mr-2" />
              Resetting Password...
            </div>
          ) : (
            'Reset Password'
          )}
        </button>

        {/* Back Button */}
        <button
          type="button"
          onClick={onBack}
          className="w-full flex items-center justify-center py-3 px-4 text-gray-600 hover:text-gray-800 font-medium transition-colors duration-200"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back
        </button>
      </form>
    </motion.div>
  );
};

export default OTPVerification;
