import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext.jsx';
import {
  Clock,
  AlertTriangle,
  XCircle,
  Mail,
  Phone,
  CheckCircle,
  ArrowLeft,
  RefreshCw
} from 'lucide-react';

const TeacherApprovalCheck = () => {
  const { user, logout, refreshUserData } = useAuth();
  const [refreshing, setRefreshing] = useState(false);

  const getStatusInfo = () => {
    switch (user?.approvalStatus) {
      case 'pending':
        return {
          icon: Clock,
          title: 'Account Pending Approval',
          message: 'Your teacher account is currently under review by our administrators.',
          description: 'We typically review applications within 24-48 hours. You will receive an email notification once your account has been approved.',
          color: 'yellow',
          bgColor: 'from-yellow-50 to-orange-50',
          iconBg: 'bg-yellow-100',
          iconColor: 'text-yellow-600',
          buttonColor: 'bg-yellow-600 hover:bg-yellow-700'
        };
      case 'rejected':
        return {
          icon: XCircle,
          title: 'Account Application Rejected',
          message: 'Unfortunately, your teacher account application has been rejected.',
          description: 'If you believe this was an error or would like to reapply, please contact our support team.',
          color: 'red',
          bgColor: 'from-red-50 to-pink-50',
          iconBg: 'bg-red-100',
          iconColor: 'text-red-600',
          buttonColor: 'bg-red-600 hover:bg-red-700'
        };
      default:
        return {
          icon: AlertTriangle,
          title: 'Account Status Unknown',
          message: 'There seems to be an issue with your account status.',
          description: 'Please contact support for assistance.',
          color: 'gray',
          bgColor: 'from-gray-50 to-gray-100',
          iconBg: 'bg-gray-100',
          iconColor: 'text-gray-600',
          buttonColor: 'bg-gray-600 hover:bg-gray-700'
        };
    }
  };

  const statusInfo = getStatusInfo();
  const StatusIcon = statusInfo.icon;

  const handleRefreshStatus = async () => {
    setRefreshing(true);
    try {
      console.log('TeacherApprovalCheck - Refreshing approval status...');
      await refreshUserData();
    } catch (error) {
      console.error('TeacherApprovalCheck - Error refreshing status:', error);
    } finally {
      setRefreshing(false);
    }
  };

  const handleBackToLogin = async () => {
    await logout();
    window.location.href = '/login';
  };

  const handleContactSupport = () => {
    window.location.href = 'mailto:support@learnsphere.com?subject=Teacher Account Support';
  };

  return (
    <div className={`min-h-screen bg-gradient-to-br ${statusInfo.bgColor} flex items-center justify-center p-4`}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-md w-full"
      >
        {/* Main Card */}
        <div className="bg-white rounded-2xl shadow-2xl p-8 text-center">
          {/* Status Icon */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2 }}
            className={`w-20 h-20 ${statusInfo.iconBg} rounded-full flex items-center justify-center mx-auto mb-6`}
          >
            <StatusIcon className={`w-10 h-10 ${statusInfo.iconColor}`} />
          </motion.div>

          {/* Title */}
          <motion.h1
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-2xl font-bold text-gray-800 mb-4"
          >
            {statusInfo.title}
          </motion.h1>

          {/* Message */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-gray-600 mb-4 leading-relaxed"
          >
            {statusInfo.message}
          </motion.p>

          {/* Description */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className="text-sm text-gray-500 mb-8 leading-relaxed"
          >
            {statusInfo.description}
          </motion.p>

          {/* User Info */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="bg-gray-50 rounded-xl p-4 mb-6"
          >
            <div className="flex items-center justify-center space-x-2 text-sm text-gray-600 mb-2">
              <Mail className="w-4 h-4" />
              <span>{user?.email}</span>
            </div>
            <div className="text-sm font-medium text-gray-800">
              {user?.fullName}
            </div>
          </motion.div>

          {/* Action Buttons */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7 }}
            className="space-y-3"
          >
            {user?.approvalStatus === 'pending' && (
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-4">
                <div className="flex items-center justify-center space-x-2 text-blue-700 mb-2">
                  <CheckCircle className="w-5 h-5" />
                  <span className="font-semibold">What happens next?</span>
                </div>
                <ul className="text-sm text-blue-600 space-y-1 text-left">
                  <li>• Admin reviews your application</li>
                  <li>• You'll receive an email notification</li>
                  <li>• If approved, you can access your teacher dashboard</li>
                </ul>
              </div>
            )}

            <div className="space-y-3">
              <button
                onClick={handleRefreshStatus}
                disabled={refreshing}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white py-3 px-6 rounded-xl font-semibold transition-all duration-200 hover:shadow-lg flex items-center justify-center space-x-2"
              >
                <RefreshCw className={`w-5 h-5 ${refreshing ? 'animate-spin' : ''}`} />
                <span>{refreshing ? 'Checking Status...' : 'Check Status'}</span>
              </button>

              <button
                onClick={handleContactSupport}
                className={`w-full ${statusInfo.buttonColor} text-white font-semibold py-3 px-6 rounded-xl transition-colors flex items-center justify-center space-x-2`}
              >
                <Mail className="w-5 h-5" />
                <span>Contact Support</span>
              </button>

              <button
                onClick={handleBackToLogin}
                className="w-full bg-gray-100 text-gray-700 font-semibold py-3 px-6 rounded-xl hover:bg-gray-200 transition-colors flex items-center justify-center space-x-2"
              >
                <ArrowLeft className="w-5 h-5" />
                <span>Back to Login</span>
              </button>
            </div>
          </motion.div>
        </div>

        {/* Additional Info */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="mt-6 text-center"
        >
          <p className="text-sm text-gray-500">
            Need immediate assistance?{' '}
            <a
              href="mailto:support@learnsphere.com"
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Email us
            </a>{' '}
            or call{' '}
            <a
              href="tel:+1234567890"
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              (123) 456-7890
            </a>
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default TeacherApprovalCheck;
