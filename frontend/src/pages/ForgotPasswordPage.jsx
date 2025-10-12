import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import ForgotPassword from '../components/ForgotPassword.jsx';
import OTPVerification from '../components/OTPVerification.jsx';
import {
  CheckCircle,
  ArrowRight
} from 'lucide-react';

const ForgotPasswordPage = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState('email'); // 'email', 'otp', 'success'
  const [email, setEmail] = useState('');

  const handleOTPSent = (userEmail) => {
    setEmail(userEmail);
    setCurrentStep('otp');
  };

  const handleOTPSuccess = () => {
    setCurrentStep('success');
  };

  const handleBackToEmail = () => {
    setCurrentStep('email');
  };

  const handleBackToLogin = () => {
    navigate('/login');
  };

  const handleGoToLogin = () => {
    navigate('/login');
  };

  const renderStep = () => {
    switch (currentStep) {
      case 'email':
        return (
          <ForgotPassword
            onBack={handleBackToLogin}
            onOTPSent={handleOTPSent}
          />
        );
      
      case 'otp':
        return (
          <OTPVerification
            email={email}
            onBack={handleBackToEmail}
            onSuccess={handleOTPSuccess}
            onResend={() => {
              // Optional: Add any additional logic for resend
            }}
          />
        );
      
      case 'success':
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="w-10 h-10 text-green-600" />
            </div>
            
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Password Reset Successful!
            </h2>
            
            <p className="text-gray-600 mb-8 text-lg">
              Your password has been successfully reset. You can now log in with your new password.
            </p>
            
            <button
              onClick={handleGoToLogin}
              className="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors duration-200"
            >
              Go to Login
              <ArrowRight className="w-5 h-5 ml-2" />
            </button>
          </motion.div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <Toaster 
        position="top-center"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />
      
      <div className="w-full max-w-md">
        {/* Progress Indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-center space-x-4">
            <div className={`
              w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold
              ${currentStep === 'email' 
                ? 'bg-blue-600 text-white' 
                : currentStep === 'otp' || currentStep === 'success'
                ? 'bg-green-600 text-white'
                : 'bg-gray-200 text-gray-600'
              }
            `}>
              1
            </div>
            
            <div className={`
              w-16 h-1 rounded-full
              ${currentStep === 'otp' || currentStep === 'success'
                ? 'bg-green-600'
                : 'bg-gray-200'
              }
            `} />
            
            <div className={`
              w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold
              ${currentStep === 'otp'
                ? 'bg-blue-600 text-white'
                : currentStep === 'success'
                ? 'bg-green-600 text-white'
                : 'bg-gray-200 text-gray-600'
              }
            `}>
              2
            </div>
            
            <div className={`
              w-16 h-1 rounded-full
              ${currentStep === 'success'
                ? 'bg-green-600'
                : 'bg-gray-200'
              }
            `} />
            
            <div className={`
              w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold
              ${currentStep === 'success'
                ? 'bg-green-600 text-white'
                : 'bg-gray-200 text-gray-600'
              }
            `}>
              ✓
            </div>
          </div>
          
          <div className="flex justify-between mt-2 text-xs text-gray-500">
            <span>Email</span>
            <span>Verify</span>
            <span>Complete</span>
          </div>
        </div>

        {/* Main Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl shadow-xl p-8"
        >
          {renderStep()}
        </motion.div>

        {/* Footer */}
        <div className="text-center mt-6">
          <p className="text-sm text-gray-500">
            Remember your password?{' '}
            <button
              onClick={handleGoToLogin}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Sign in here
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;
