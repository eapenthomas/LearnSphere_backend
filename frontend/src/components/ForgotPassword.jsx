import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { toast } from 'react-hot-toast';
import axios from 'axios';
import {
  Mail,
  ArrowLeft,
  Loader,
  Shield,
  Clock,
  CheckCircle
} from 'lucide-react';

// API base URL
const API_BASE_URL = 'http://localhost:8000';

// Validation schema
const emailSchema = yup.object().shape({
  email: yup
    .string()
    .email('Please enter a valid email address')
    .required('Email is required')
});

const ForgotPassword = ({ onBack, onOTPSent }) => {
  const [loading, setLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    getValues
  } = useForm({
    resolver: yupResolver(emailSchema),
    mode: 'onChange'
  });

  const onSubmit = async (data) => {
    setLoading(true);
    
    try {
      console.log('Requesting password reset for:', data.email);
      
      const response = await axios.post(`${API_BASE_URL}/forgot-password`, {
        email: data.email
      });

      if (response.data) {
        setEmailSent(true);
        toast.success('Password reset code sent to your email!');
        
        // Call parent callback with email
        if (onOTPSent) {
          onOTPSent(data.email);
        }
      }
    } catch (error) {
      console.error('Forgot password error:', error);
      
      const errorMessage = error.response?.data?.detail || error.message;
      
      if (errorMessage.includes('not set up for password login')) {
        toast.error('This account uses Google login. Please sign in with Google.');
      } else {
        toast.error('Failed to send reset code. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  if (emailSent) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <CheckCircle className="w-8 h-8 text-green-600" />
        </div>
        
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Check Your Email
        </h2>
        
        <p className="text-gray-600 mb-6">
          We've sent a 6-digit verification code to:
        </p>
        
        <p className="text-lg font-semibold text-blue-600 mb-6">
          {getValues('email')}
        </p>
        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-center justify-center mb-2">
            <Clock className="w-5 h-5 text-blue-600 mr-2" />
            <span className="text-blue-800 font-medium">Code expires in 10 minutes</span>
          </div>
          <p className="text-blue-700 text-sm">
            Enter the code on the next page to reset your password
          </p>
        </div>
        
        <button
          onClick={() => setEmailSent(false)}
          className="text-blue-600 hover:text-blue-700 font-medium"
        >
          Didn't receive the code? Try again
        </button>
      </motion.div>
    );
  }

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
          Forgot Password?
        </h2>
        
        <p className="text-gray-600">
          Enter your email address and we'll send you a verification code to reset your password.
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Email Address
          </label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="email"
              {...register('email')}
              className={`
                w-full pl-10 pr-4 py-3 border rounded-lg transition-all duration-200
                focus:outline-none focus:ring-2 focus:border-transparent bg-white text-gray-800
                ${errors.email 
                  ? 'border-red-300 focus:ring-red-400' 
                  : 'border-gray-200 focus:ring-blue-400'
                }
              `}
              placeholder="Enter your email address"
            />
          </div>
          {errors.email && (
            <p className="mt-2 text-sm text-red-600">{errors.email.message}</p>
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
              Sending Code...
            </div>
          ) : (
            'Send Reset Code'
          )}
        </button>

        {/* Back Button */}
        <button
          type="button"
          onClick={onBack}
          className="w-full flex items-center justify-center py-3 px-4 text-gray-600 hover:text-gray-800 font-medium transition-colors duration-200"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back to Login
        </button>
      </form>
    </motion.div>
  );
};

export default ForgotPassword;
