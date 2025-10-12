import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { toast } from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext.jsx';
import axios from 'axios';
import {
  Lock,
  Eye,
  EyeOff,
  Shield,
  AlertCircle,
  CheckCircle,
  Loader,
  Key
} from 'lucide-react';

// API base URL
const API_BASE_URL = 'http://localhost:8000';

// Validation schema
const passwordSchema = yup.object().shape({
  currentPassword: yup
    .string()
    .required('Current password is required'),
  newPassword: yup
    .string()
    .required('New password is required')
    .min(8, 'New password must be at least 8 characters')
    .matches(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      'Password must contain at least one uppercase letter, one lowercase letter, and one number'
    ),
  confirmPassword: yup
    .string()
    .required('Please confirm your new password')
    .oneOf([yup.ref('newPassword')], 'Passwords must match')
});

const PasswordUpdate = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  });

  const {
    register,
    handleSubmit,
    formState: { errors, isValid },
    reset,
    watch
  } = useForm({
    resolver: yupResolver(passwordSchema),
    mode: 'onChange'
  });

  const watchedValues = watch();

  const togglePasswordVisibility = (field) => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };

  const onSubmit = async (data) => {
    setLoading(true);

    try {
      console.log('Updating password...');

      if (!user || !user.id) {
        toast.error('User session not found. Please log in again.');
        return;
      }

      // Call backend API to update password
      const response = await axios.post(`${API_BASE_URL}/update-password`, {
        user_id: user.id,
        current_password: data.currentPassword,
        new_password: data.newPassword
      });

      if (response.data) {
        // Success
        toast.success('Password updated successfully!');

        // Reset form
        reset();
      }
    } catch (error) {
      console.error('Password update error:', error);

      // Handle specific error cases
      const errorMessage = error.response?.data?.detail || error.message;

      if (errorMessage.includes('Current password is incorrect')) {
        toast.error('Current password is incorrect.');
      } else if (errorMessage.includes('New password must be different')) {
        toast.error('New password must be different from your current password.');
      } else if (errorMessage.includes('User not found')) {
        toast.error('User account not found. Please log in again.');
      } else if (errorMessage.includes('Account not set up for password login')) {
        toast.error('Your account is not set up for password login. Please contact support.');
      } else {
        toast.error('Failed to update password. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const getPasswordStrength = (password) => {
    if (!password) return { strength: 0, label: '', color: '' };
    
    let strength = 0;
    const checks = [
      password.length >= 8,
      /[a-z]/.test(password),
      /[A-Z]/.test(password),
      /\d/.test(password),
      /[!@#$%^&*(),.?":{}|<>]/.test(password)
    ];
    
    strength = checks.filter(Boolean).length;
    
    if (strength <= 2) return { strength, label: 'Weak', color: 'bg-red-500' };
    if (strength <= 3) return { strength, label: 'Fair', color: 'bg-yellow-500' };
    if (strength <= 4) return { strength, label: 'Good', color: 'bg-blue-500' };
    return { strength, label: 'Strong', color: 'bg-green-500' };
  };

  const passwordStrength = getPasswordStrength(watchedValues.newPassword);

  return (
    <div className="card p-6 hover:shadow-xl transition-all duration-300">
      {/* Card Header */}
      <div className="flex items-center space-x-3 mb-6">
        <div className="p-2 bg-red-100 rounded-lg">
          <Lock className="w-5 h-5 text-red-600" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-800">Update Password</h2>
          <p className="text-sm text-gray-600">Change your account password</p>
        </div>
      </div>

      {/* Password Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Current Password */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Current Password *
          </label>
          <div className="relative">
            <Key className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type={showPasswords.current ? 'text' : 'password'}
              {...register('currentPassword')}
              className={`
                w-full pl-10 pr-12 py-3 border rounded-lg transition-all duration-200
                focus:outline-none focus:ring-2 focus:border-transparent bg-white text-gray-800
                ${errors.currentPassword 
                  ? 'border-red-300 focus:ring-red-400' 
                  : 'border-gray-200 focus:ring-blue-400'
                }
              `}
              placeholder="Enter your current password"
            />
            <button
              type="button"
              onClick={() => togglePasswordVisibility('current')}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
            >
              {showPasswords.current ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          </div>
          {errors.currentPassword && (
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-2 text-sm text-red-600 flex items-center space-x-1"
            >
              <AlertCircle className="w-4 h-4" />
              <span>{errors.currentPassword.message}</span>
            </motion.p>
          )}
        </div>

        {/* New Password */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            New Password *
          </label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type={showPasswords.new ? 'text' : 'password'}
              {...register('newPassword')}
              className={`
                w-full pl-10 pr-12 py-3 border rounded-lg transition-all duration-200
                focus:outline-none focus:ring-2 focus:border-transparent bg-white text-gray-800
                ${errors.newPassword 
                  ? 'border-red-300 focus:ring-red-400' 
                  : 'border-gray-200 focus:ring-blue-400'
                }
              `}
              placeholder="Enter your new password"
            />
            <button
              type="button"
              onClick={() => togglePasswordVisibility('new')}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
            >
              {showPasswords.new ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          </div>
          
          {/* Password Strength Indicator */}
          {watchedValues.newPassword && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-2"
            >
              <div className="flex items-center space-x-2 mb-1">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-300 ${passwordStrength.color}`}
                    style={{ width: `${(passwordStrength.strength / 5) * 100}%` }}
                  />
                </div>
                <span className={`text-xs font-medium ${
                  passwordStrength.strength <= 2 ? 'text-red-600' :
                  passwordStrength.strength <= 3 ? 'text-yellow-600' :
                  passwordStrength.strength <= 4 ? 'text-blue-600' : 'text-green-600'
                }`}>
                  {passwordStrength.label}
                </span>
              </div>
            </motion.div>
          )}
          
          {errors.newPassword && (
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-2 text-sm text-red-600 flex items-center space-x-1"
            >
              <AlertCircle className="w-4 h-4" />
              <span>{errors.newPassword.message}</span>
            </motion.p>
          )}
        </div>

        {/* Confirm Password */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Confirm New Password *
          </label>
          <div className="relative">
            <Shield className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type={showPasswords.confirm ? 'text' : 'password'}
              {...register('confirmPassword')}
              className={`
                w-full pl-10 pr-12 py-3 border rounded-lg transition-all duration-200
                focus:outline-none focus:ring-2 focus:border-transparent bg-white text-gray-800
                ${errors.confirmPassword 
                  ? 'border-red-300 focus:ring-red-400' 
                  : 'border-gray-200 focus:ring-blue-400'
                }
              `}
              placeholder="Confirm your new password"
            />
            <button
              type="button"
              onClick={() => togglePasswordVisibility('confirm')}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
            >
              {showPasswords.confirm ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          </div>
          {errors.confirmPassword && (
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-2 text-sm text-red-600 flex items-center space-x-1"
            >
              <AlertCircle className="w-4 h-4" />
              <span>{errors.confirmPassword.message}</span>
            </motion.p>
          )}
        </div>

        {/* Password Requirements */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="text-sm font-semibold text-blue-800 mb-2">Password Requirements:</h4>
          <ul className="text-xs text-blue-700 space-y-1">
            <li>• At least 8 characters long</li>
            <li>• Contains at least one uppercase letter</li>
            <li>• Contains at least one lowercase letter</li>
            <li>• Contains at least one number</li>
            <li>• Special characters recommended for stronger security</li>
          </ul>
        </div>

        {/* Submit Button */}
        <motion.button
          type="submit"
          disabled={loading || !isValid}
          whileHover={{ scale: !loading ? 1.02 : 1 }}
          whileTap={{ scale: !loading ? 0.98 : 1 }}
          className={`
            w-full flex items-center justify-center space-x-2 py-3 px-6 rounded-lg font-semibold
            transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2
            ${loading || !isValid
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white shadow-lg hover:shadow-xl focus:ring-red-500'
            }
          `}
        >
          {loading ? (
            <>
              <Loader className="w-5 h-5 animate-spin" />
              <span>Updating Password...</span>
            </>
          ) : (
            <>
              <Lock className="w-5 h-5" />
              <span>Update Password</span>
            </>
          )}
        </motion.button>
      </form>
    </div>
  );
};

export default PasswordUpdate;
