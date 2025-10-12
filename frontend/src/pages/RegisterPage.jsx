import React, { useState, useCallback, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext.jsx';
import Input from '../components/Input.jsx';
import Button from '../components/Button.jsx';
import TeacherVerificationForm from '../components/TeacherVerificationForm.jsx';
import axios from 'axios';
import { toast } from 'react-hot-toast';
import {
  BookOpen,
  Eye,
  EyeOff,
  User,
  Mail,
  Building,
  Lock,
  GraduationCap,
  ArrowRight,
  AlertCircle,
  CheckCircle,
  Shield,
  Zap,
  Camera,
  Upload
} from 'lucide-react';

const RegisterPage = () => {
  const navigate = useNavigate();
  const { register, loginWithGoogle } = useAuth();
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    institution_name: '',
    password: '',
    confirm_password: '',
    role: 'student'
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showEnhancedVerification, setShowEnhancedVerification] = useState(false);
  const [verificationMethod, setVerificationMethod] = useState(null); // 'manual' or 'enhanced'
  const [verificationDocument, setVerificationDocument] = useState(null);

  // Real-time validation states
  const [validationErrors, setValidationErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [emailChecking, setEmailChecking] = useState(false);
  const [emailCheckTimeout, setEmailCheckTimeout] = useState(null);

  // API base URL
  const API_BASE_URL = 'http://localhost:8000';

  // Email availability check function
  const checkEmailAvailability = useCallback(async (email) => {
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return; // Don't check if email format is invalid
    }

    try {
      setEmailChecking(true);
      const response = await axios.post(`${API_BASE_URL}/check-email`, {
        email: email
      });

      if (response.data.exists) {
        setValidationErrors(prev => ({
          ...prev,
          email: 'This email is already registered. Please use a different email or try logging in.'
        }));
      } else {
        // Clear email error if it was about email existence
        setValidationErrors(prev => {
          const newErrors = { ...prev };
          if (newErrors.email && newErrors.email.includes('already registered')) {
            delete newErrors.email;
          }
          return newErrors;
        });
      }
    } catch (error) {
      console.error('Email check failed:', error);
      // Don't show error to user for email check failures
    } finally {
      setEmailChecking(false);
    }
  }, [API_BASE_URL]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (emailCheckTimeout) {
        clearTimeout(emailCheckTimeout);
      }
    };
  }, [emailCheckTimeout]);

  // Real-time validation functions
  const validateField = (name, value) => {
    const errors = {};

    switch (name) {
      case 'full_name':
        if (!value.trim()) {
          errors.full_name = 'Full name is required';
        } else if (value.trim().length < 2) {
          errors.full_name = 'Name must be at least 2 characters long';
        } else if (/\d/.test(value)) {
          errors.full_name = 'Name cannot contain numbers';
        } else if (!/^[a-zA-Z\s'-]+$/.test(value)) {
          errors.full_name = 'Name can only contain letters, spaces, hyphens, and apostrophes';
        }
        break;

      case 'email':
        if (!value.trim()) {
          errors.email = 'Email is required';
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
          errors.email = 'Please enter a valid email address';
        } else {
          // Schedule email availability check with debounce
          if (emailCheckTimeout) {
            clearTimeout(emailCheckTimeout);
          }
          const timeout = setTimeout(() => {
            checkEmailAvailability(value);
          }, 800); // 800ms debounce
          setEmailCheckTimeout(timeout);
        }
        break;

      case 'institution_name':
        if (formData.role === 'teacher' && !value.trim()) {
          errors.institution_name = 'Institution name is required for teachers';
        } else if (value.trim() && value.trim().length < 2) {
          errors.institution_name = 'Institution name must be at least 2 characters long';
        }
        break;

      case 'password':
        if (!value) {
          errors.password = 'Password is required';
        } else if (value.length < 8) {
          errors.password = 'Password must be at least 8 characters long';
        } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(value)) {
          errors.password = 'Password must contain at least one uppercase letter, one lowercase letter, and one number';
        }
        break;

      case 'confirm_password':
        if (!value) {
          errors.confirm_password = 'Please confirm your password';
        } else if (value !== formData.password) {
          errors.confirm_password = 'Passwords do not match';
        }
        break;

      default:
        break;
    }

    return errors;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    setFormData({
      ...formData,
      [name]: value
    });

    // Reset verification method when role changes
    if (name === 'role') {
      setVerificationMethod(null);
    }

    // Mark field as touched
    setTouched({
      ...touched,
      [name]: true
    });

    // Validate field in real-time
    const fieldErrors = validateField(name, value);
    setValidationErrors({
      ...validationErrors,
      ...fieldErrors,
      // Clear error if field is now valid
      ...(Object.keys(fieldErrors).length === 0 && { [name]: undefined })
    });

    // Clear general error
    setError('');
  };

  const handleBlur = (e) => {
    const { name, value } = e.target;

    // Mark field as touched on blur
    setTouched({
      ...touched,
      [name]: true
    });

    // Validate field on blur
    const fieldErrors = validateField(name, value);
    setValidationErrors({
      ...validationErrors,
      ...fieldErrors,
      // Clear error if field is now valid
      ...(Object.keys(fieldErrors).length === 0 && { [name]: undefined })
    });
  };

  const validateForm = () => {
    // Validate all fields
    const allErrors = {};
    Object.keys(formData).forEach(field => {
      if (field !== 'role') {
        const fieldErrors = validateField(field, formData[field]);
        Object.assign(allErrors, fieldErrors);
      }
    });

    // Special case for confirm_password validation
    if (formData.confirm_password !== formData.password) {
      allErrors.confirm_password = 'Passwords do not match';
    }

    setValidationErrors(allErrors);

    // Mark all fields as touched
    const allTouched = {};
    Object.keys(formData).forEach(field => {
      allTouched[field] = true;
    });
    setTouched(allTouched);

    return Object.keys(allErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      if (formData.role === 'teacher' && verificationMethod === 'manual') {
        // Handle manual verification for teachers
        await handleManualTeacherRegistration();
      } else if (formData.role === 'teacher' && verificationMethod === 'enhanced') {
        // Enhanced verification is handled by the modal
        toast.error('Please use the Enhanced Verification modal to complete your registration.');
        setLoading(false);
        return;
      } else {
        // Regular student registration or manual teacher without verification method
        const { confirm_password, ...registerData } = formData;
        const result = await register(registerData);

        if (result.success) {
          if (formData.role === 'teacher') {
            toast.success('Registration successful! Your account is pending admin approval. You will receive an email notification once approved.');
            navigate('/login');
          } else {
            navigate('/dashboard');
          }
        } else {
          setError(result.error);
        }
      }
    } catch (error) {
      setError(error.message || 'Registration failed. Please try again.');
    }

    setLoading(false);
  };

  const handleManualTeacherRegistration = async () => {
    const { confirm_password, ...registerData } = formData;
    
    // Create FormData for file upload
    const formDataToSend = new FormData();
    formDataToSend.append('full_name', registerData.full_name);
    formDataToSend.append('email', registerData.email);
    formDataToSend.append('institution_name', registerData.institution_name);
    formDataToSend.append('password', registerData.password);
    
    // Add verification document if uploaded
    if (verificationDocument) {
      formDataToSend.append('verification_document', verificationDocument);
    } else {
      throw new Error('Verification document is required for manual approval');
    }

    const response = await fetch('http://localhost:8000/api/teacher-verification/register-manual', {
      method: 'POST',
      body: formDataToSend,
    });

    const result = await response.json();
    
    if (response.ok) {
      toast.success(result.message || 'Registration successful! Your documents have been submitted for manual review.');
      navigate('/login?message=manual_verification_submitted');
    } else {
      throw new Error(result.detail || 'Manual registration failed');
    }
  };

  const handleGoogleSignup = async () => {
    setLoading(true);
    setError('');

    const result = await loginWithGoogle();

    if (!result.success) {
      setError(result.error);
      setLoading(false);
    }
  };

  const benefits = [
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Fast Setup",
      description: "Get started in minutes"
    },
    {
      icon: <Shield className="w-6 h-6" />,
      title: "Secure",
      description: "Your data is protected"
    },
    {
      icon: <CheckCircle className="w-6 h-6" />,
      title: "Free Access",
      description: "No hidden fees"
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center page-container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-7xl grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-16 mobile-grid"
      >
        {/* Left Side - Registration Form */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="flex flex-col justify-center lg:w-full lg:max-w-lg xl:max-w-xl mx-auto order-2 lg:order-1"
        >
          {/* Logo and Title */}
          <div className="text-center mb-8">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="flex justify-center mb-6"
            >
              <div className="p-3 bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl hover:scale-110 transition-transform duration-300">
                <BookOpen className="w-8 h-8 text-white" />
              </div>
            </motion.div>
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="text-3xl font-extrabold text-gray-800 tracking-tight mb-3"
            >
              Join LearnSphere
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.5 }}
              className="text-gray-600 font-medium"
            >
              Start your learning journey today
            </motion.p>
          </div>

          {/* Registration Form */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            className="bg-white rounded-2xl shadow-lg border border-gray-100 mobile-padding sm:p-8 lg:p-10 hover:shadow-xl transition-all duration-300 w-full"
          >
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Role Selection - First Step */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-4">
                  I am a
                </label>
                <div className="grid grid-cols-2 gap-4">
                  <label className="flex items-center p-4 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                    <input
                      type="radio"
                      name="role"
                      value="student"
                      checked={formData.role === 'student'}
                      onChange={handleChange}
                      className="sr-only"
                    />
                    <div className={`w-4 h-4 border-2 rounded-full mr-3 flex items-center justify-center ${formData.role === 'student' ? 'border-blue-500 bg-blue-500' : 'border-gray-300'
                      }`}>
                      {formData.role === 'student' && <div className="w-2 h-2 bg-white rounded-full"></div>}
                    </div>
                    <div className="flex items-center">
                      <GraduationCap className="w-5 h-5 text-gray-600 mr-2" />
                      <span className="font-medium text-gray-700">Student</span>
                    </div>
                  </label>
                  <label className="flex items-center p-4 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                    <input
                      type="radio"
                      name="role"
                      value="teacher"
                      checked={formData.role === 'teacher'}
                      onChange={handleChange}
                      className="sr-only"
                    />
                    <div className={`w-4 h-4 border-2 rounded-full mr-3 flex items-center justify-center ${formData.role === 'teacher' ? 'border-blue-500 bg-blue-500' : 'border-gray-300'
                      }`}>
                      {formData.role === 'teacher' && <div className="w-2 h-2 bg-white rounded-full"></div>}
                    </div>
                    <div className="flex items-center">
                      <BookOpen className="w-5 h-5 text-gray-600 mr-2" />
                      <span className="font-medium text-gray-700">Teacher</span>
                    </div>
                  </label>
                </div>
              </div>

              {/* Teacher Verification Method Selection */}
              {formData.role === 'teacher' && !verificationMethod && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className="space-y-4"
                >
                  <div className="text-center">
                    <h3 className="text-lg font-semibold text-gray-800 mb-2">Choose Verification Method</h3>
                    <p className="text-sm text-gray-600">Select how you'd like to verify your teacher status</p>
                  </div>
                  
                  {/* Manual Approval Option */}
                  <button
                    type="button"
                    onClick={() => setVerificationMethod('manual')}
                    className="w-full bg-white border-2 border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors text-left"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center mr-3">
                          <User className="w-5 h-5 text-gray-600" />
                        </div>
                        <div>
                          <h4 className="font-semibold text-gray-900">Manual Approval</h4>
                          <p className="text-sm text-gray-600">Admin will review your application</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="text-xs text-gray-500">2-3 business days</span>
                      </div>
                    </div>
                  </button>

                  {/* Enhanced Verification Option */}
                  <button
                    type="button"
                    onClick={() => setVerificationMethod('enhanced')}
                    className="w-full bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-300 rounded-lg p-4 hover:border-blue-400 transition-colors text-left"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mr-3">
                          <Camera className="w-5 h-5 text-blue-600" />
                        </div>
                        <div>
                          <h4 className="font-semibold text-gray-900">Enhanced Verification</h4>
                          <p className="text-sm text-gray-700">Upload ID card for faster approval</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="text-xs text-blue-600 font-medium">Same day approval</span>
                      </div>
                    </div>
                  </button>
                </motion.div>
              )}

              {/* Form Fields - Show based on role and verification method */}
              {(formData.role === 'student' || (formData.role === 'teacher' && verificationMethod)) && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className="space-y-6"
                >
                  {/* Full Name Input */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Full Name
                </label>
                <div className="relative">
                  <User className={`absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 ${
                    validationErrors.full_name && touched.full_name
                      ? 'text-red-400'
                      : formData.full_name && !validationErrors.full_name && touched.full_name
                      ? 'text-green-400'
                      : 'text-gray-400'
                  }`} />
                  <input
                    type="text"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    placeholder="Enter your full name"
                    required
                    className={`w-full pl-10 pr-10 py-2 bg-white border border-gray-300 rounded-md text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all duration-200 ${
                      validationErrors.full_name && touched.full_name
                        ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
                        : formData.full_name && !validationErrors.full_name && touched.full_name
                        ? 'border-green-300 focus:border-green-500 focus:ring-green-500'
                        : ''
                    }`}
                  />
                  {/* Validation Icon */}
                  {touched.full_name && (
                    <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                      {validationErrors.full_name ? (
                        <AlertCircle className="w-5 h-5 text-red-400" />
                      ) : formData.full_name ? (
                        <CheckCircle className="w-5 h-5 text-green-400" />
                      ) : null}
                    </div>
                  )}
                </div>
                {/* Error Message */}
                {validationErrors.full_name && touched.full_name && (
                  <motion.p
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-2 text-sm text-red-600 flex items-center"
                  >
                    <AlertCircle className="w-4 h-4 mr-1" />
                    {validationErrors.full_name}
                  </motion.p>
                )}
                {/* Success Message */}
                {!validationErrors.full_name && formData.full_name && touched.full_name && (
                  <motion.p
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-2 text-sm text-green-600 flex items-center"
                  >
                    <CheckCircle className="w-4 h-4 mr-1" />
                    Name looks good!
                  </motion.p>
                )}
              </div>

              {/* Email Input */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className={`absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 ${
                    validationErrors.email && touched.email
                      ? 'text-red-400'
                      : formData.email && !validationErrors.email && touched.email
                      ? 'text-green-400'
                      : 'text-gray-400'
                  }`} />
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    placeholder="Enter your email"
                    required
                    className={`w-full pl-10 pr-10 py-2 bg-white border border-gray-300 rounded-md text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all duration-200 ${
                      validationErrors.email && touched.email
                        ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
                        : formData.email && !validationErrors.email && touched.email
                        ? 'border-green-300 focus:border-green-500 focus:ring-green-500'
                        : ''
                    }`}
                  />
                  {/* Validation Icon */}
                  {touched.email && (
                    <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                      {emailChecking ? (
                        <div className="w-5 h-5 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
                      ) : validationErrors.email ? (
                        <AlertCircle className="w-5 h-5 text-red-400" />
                      ) : formData.email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email) ? (
                        <CheckCircle className="w-5 h-5 text-green-400" />
                      ) : null}
                    </div>
                  )}
                </div>
                {/* Error Message */}
                {validationErrors.email && touched.email && (
                  <motion.p
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-2 text-sm text-red-600 flex items-center"
                  >
                    <AlertCircle className="w-4 h-4 mr-1" />
                    {validationErrors.email}
                  </motion.p>
                )}
                {/* Success Message */}
                {!validationErrors.email && formData.email && touched.email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email) && !emailChecking && (
                  <motion.p
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-2 text-sm text-green-600 flex items-center"
                  >
                    <CheckCircle className="w-4 h-4 mr-1" />
                    Email is available!
                  </motion.p>
                )}
                {/* Checking Message */}
                {emailChecking && formData.email && touched.email && (
                  <motion.p
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-2 text-sm text-blue-600 flex items-center"
                  >
                    <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mr-1" />
                    Checking email availability...
                  </motion.p>
                )}
              </div>

              {/* Institution Name Input - Only for Teachers */}
              {formData.role === 'teacher' && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Institution Name
                  </label>
                  <div className="relative">
                    <Building className={`absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 ${
                      validationErrors.institution_name && touched.institution_name
                        ? 'text-red-400'
                        : formData.institution_name && !validationErrors.institution_name && touched.institution_name
                        ? 'text-green-400'
                        : 'text-gray-400'
                    }`} />
                    <input
                      type="text"
                      name="institution_name"
                      value={formData.institution_name}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      placeholder="Enter your institution name"
                      required
                      className={`w-full pl-10 pr-10 py-2 bg-white border border-gray-300 rounded-md text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all duration-200 ${
                        validationErrors.institution_name && touched.institution_name
                          ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
                          : formData.institution_name && !validationErrors.institution_name && touched.institution_name
                          ? 'border-green-300 focus:border-green-500 focus:ring-green-500'
                          : ''
                      }`}
                    />
                    {/* Validation Icon */}
                    {touched.institution_name && (
                      <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                        {validationErrors.institution_name ? (
                          <AlertCircle className="w-5 h-5 text-red-400" />
                        ) : formData.institution_name ? (
                          <CheckCircle className="w-5 h-5 text-green-400" />
                        ) : null}
                      </div>
                    )}
                  </div>
                  {/* Error Message */}
                  {validationErrors.institution_name && touched.institution_name && (
                    <motion.p
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="mt-2 text-sm text-red-600 flex items-center"
                    >
                      <AlertCircle className="w-4 h-4 mr-1" />
                      {validationErrors.institution_name}
                    </motion.p>
                  )}
                  {/* Success Message */}
                  {!validationErrors.institution_name && formData.institution_name && touched.institution_name && (
                    <motion.p
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="mt-2 text-sm text-green-600 flex items-center"
                    >
                      <CheckCircle className="w-4 h-4 mr-1" />
                      Institution name looks good!
                    </motion.p>
                  )}
                </motion.div>
              )}

              {/* Password Input */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Password
                </label>
                <div className="relative">
                  <Lock className={`absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 ${
                    validationErrors.password && touched.password
                      ? 'text-red-400'
                      : formData.password && !validationErrors.password && touched.password
                      ? 'text-green-400'
                      : 'text-gray-400'
                  }`} />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    placeholder="Create a password"
                    required
                    className={`w-full pl-10 pr-20 py-2 bg-white border border-gray-300 rounded-md text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all duration-200 ${
                      validationErrors.password && touched.password
                        ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
                        : formData.password && !validationErrors.password && touched.password
                        ? 'border-green-300 focus:border-green-500 focus:ring-green-500'
                        : ''
                    }`}
                  />
                  {/* Validation Icon */}
                  {touched.password && (
                    <div className="absolute right-12 top-1/2 transform -translate-y-1/2">
                      {validationErrors.password ? (
                        <AlertCircle className="w-5 h-5 text-red-400" />
                      ) : formData.password ? (
                        <CheckCircle className="w-5 h-5 text-green-400" />
                      ) : null}
                    </div>
                  )}
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
                {/* Error Message */}
                {validationErrors.password && touched.password && (
                  <motion.p
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-2 text-sm text-red-600 flex items-center"
                  >
                    <AlertCircle className="w-4 h-4 mr-1" />
                    {validationErrors.password}
                  </motion.p>
                )}
                {/* Success Message */}
                {!validationErrors.password && formData.password && touched.password && (
                  <motion.p
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-2 text-sm text-green-600 flex items-center"
                  >
                    <CheckCircle className="w-4 h-4 mr-1" />
                    Password strength is good!
                  </motion.p>
                )}
              </div>

              {/* Confirm Password Input */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Confirm Password
                </label>
                <div className="relative">
                  <Lock className={`absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 ${
                    validationErrors.confirm_password && touched.confirm_password
                      ? 'text-red-400'
                      : formData.confirm_password && !validationErrors.confirm_password && touched.confirm_password
                      ? 'text-green-400'
                      : 'text-gray-400'
                  }`} />
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    name="confirm_password"
                    value={formData.confirm_password}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    placeholder="Confirm your password"
                    required
                    className={`w-full pl-10 pr-20 py-2 bg-white border border-gray-300 rounded-md text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all duration-200 ${
                      validationErrors.confirm_password && touched.confirm_password
                        ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
                        : formData.confirm_password && !validationErrors.confirm_password && touched.confirm_password
                        ? 'border-green-300 focus:border-green-500 focus:ring-green-500'
                        : ''
                    }`}
                  />
                  {/* Validation Icon */}
                  {touched.confirm_password && (
                    <div className="absolute right-12 top-1/2 transform -translate-y-1/2">
                      {validationErrors.confirm_password ? (
                        <AlertCircle className="w-5 h-5 text-red-400" />
                      ) : formData.confirm_password ? (
                        <CheckCircle className="w-5 h-5 text-green-400" />
                      ) : null}
                    </div>
                  )}
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
                {/* Error Message */}
                {validationErrors.confirm_password && touched.confirm_password && (
                  <motion.p
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-2 text-sm text-red-600 flex items-center"
                  >
                    <AlertCircle className="w-4 h-4 mr-1" />
                    {validationErrors.confirm_password}
                  </motion.p>
                )}
                {/* Success Message */}
                {!validationErrors.confirm_password && formData.confirm_password && touched.confirm_password && (
                  <motion.p
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-2 text-sm text-green-600 flex items-center"
                  >
                    <CheckCircle className="w-4 h-4 mr-1" />
                    Passwords match!
                  </motion.p>
                )}
              </div>

                  {/* Verification Document Upload for Manual Verification */}
                  {formData.role === 'teacher' && verificationMethod === 'manual' && (
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Verification Document
                      </label>
                      <div className={`border-2 border-dashed rounded-lg p-4 text-center transition-colors ${
                        verificationDocument ? 'border-green-300 bg-green-50' : 'border-gray-300 hover:border-blue-400'
                      }`}>
                        {verificationDocument ? (
                          <div className="space-y-2">
                            <CheckCircle className="w-8 h-8 mx-auto text-green-500" />
                            <p className="text-green-600 font-medium">{verificationDocument.name}</p>
                            <p className="text-sm text-gray-500">
                              {(verificationDocument.size / 1024 / 1024).toFixed(2)} MB
                            </p>
                            <button
                              type="button"
                              onClick={() => setVerificationDocument(null)}
                              className="text-red-500 text-sm hover:text-red-700"
                            >
                              Remove file
                            </button>
                          </div>
                        ) : (
                          <div className="space-y-2">
                            <Upload className="w-8 h-8 mx-auto text-gray-400" />
                            <p className="text-gray-600">Upload verification document</p>
                            <p className="text-sm text-gray-500">
                              PNG, JPG, JPEG, PDF, GIF, BMP (Max 10MB)
                            </p>
                            <input
                              type="file"
                              onChange={(e) => {
                                const file = e.target.files[0];
                                if (file) {
                                  const allowedTypes = ['.png', '.jpg', '.jpeg', '.pdf', '.gif', '.bmp'];
                                  const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
                                  
                                  if (allowedTypes.includes(fileExtension)) {
                                    if (file.size > 10 * 1024 * 1024) {
                                      toast.error('File size must be less than 10MB');
                                      return;
                                    }
                                    setVerificationDocument(file);
                                    toast.success('Document uploaded successfully!');
                                  } else {
                                    toast.error('Please upload a valid document file');
                                  }
                                }
                              }}
                              accept=".png,.jpg,.jpeg,.pdf,.gif,.bmp"
                              className="hidden"
                              id="verification-document-upload"
                            />
                            <label
                              htmlFor="verification-document-upload"
                              className="inline-block bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 cursor-pointer transition-colors"
                            >
                              Choose Document
                            </label>
                          </div>
                        )}
                      </div>
                      <p className="mt-2 text-xs text-gray-500">
                        Upload any document that proves your teaching credentials (ID card, certificate, etc.)
                      </p>
                    </div>
                  )}

                  {/* Enhanced Verification Button for Teachers */}
                  {formData.role === 'teacher' && verificationMethod === 'enhanced' && (
                    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <Camera className="w-5 h-5 text-blue-600 mr-2" />
                          <div>
                            <h4 className="font-semibold text-gray-900">Upload ID Card</h4>
                            <p className="text-sm text-gray-700">Complete your enhanced verification</p>
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={() => setShowEnhancedVerification(true)}
                          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                        >
                          Upload Now
                        </button>
                      </div>
                    </div>
                  )}
                </motion.div>
              )}

              {/* Error Message */}
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center space-x-2 p-3 bg-red-50 border border-red-200 rounded-lg"
                >
                  <AlertCircle className="w-5 h-5 text-red-500" />
                  <span className="text-sm text-red-600 font-medium">{error}</span>
                </motion.div>
              )}

              {/* Submit Button */}
              <motion.button
                type="submit"
                disabled={loading || emailChecking || Object.keys(validationErrors).some(key => validationErrors[key])}
                whileHover={{ scale: loading || emailChecking || Object.keys(validationErrors).some(key => validationErrors[key]) ? 1 : 1.02 }}
                whileTap={{ scale: loading || emailChecking || Object.keys(validationErrors).some(key => validationErrors[key]) ? 1 : 0.98 }}
                className={`btn-blue w-full ${loading || emailChecking ? 'opacity-75 cursor-not-allowed' : ''}`}
              >
                {loading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Creating account...</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-center space-x-2">
                    <span>Create Account</span>
                    <ArrowRight className="w-5 h-5" />
                  </div>
                )}
              </motion.button>
            </form>

            {/* Divider */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
              className="mt-6"
            >
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-200"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-4 bg-gray-50 text-gray-500 font-medium">Or continue with</span>
                </div>
              </div>
            </motion.div>

            {/* Google Signup */}
            <motion.button
              type="button"
              onClick={handleGoogleSignup}
              disabled={loading}
              whileHover={{ scale: loading ? 1 : 1.02 }}
              whileTap={{ scale: loading ? 1 : 0.98 }}
              className="btn-card w-full mt-4"
            >
              <div className="flex items-center justify-center space-x-2">
                <svg className="w-5 h-5" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                </svg>
                <span>Sign up with Google</span>
              </div>
            </motion.button>

            {/* Sign In Link */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.7 }}
              className="mt-6 text-center"
            >
              <p className="text-gray-600 mb-2">
                Already have an account?{' '}
                <Link to="/login" className="text-blue-600 hover:text-blue-700 font-semibold transition-colors">
                  Sign in here
                </Link>
              </p>
              <p className="text-xs text-gray-500">
                Google signup automatically creates your account
              </p>
            </motion.div>
          </motion.div>
        </motion.div>

        {/* Right Side - Benefits */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="flex flex-col justify-center lg:w-full lg:max-w-lg xl:max-w-xl mx-auto order-1 lg:order-2"
        >
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 mobile-padding sm:p-8 lg:p-10 hover:shadow-xl transition-all duration-300 w-full">
            <h2 className="text-2xl font-extrabold text-gray-800 mb-6">
              Why Choose LearnSphere?
            </h2>
            <div className="space-y-6">
              {benefits.map((benefit, index) => (
                <motion.div
                  key={benefit.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 + index * 0.1 }}
                  className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 hover:scale-105 transition-all duration-300"
                >
                  <div className="p-2 bg-blue-100 rounded-lg">
                    {benefit.icon}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-800 mb-1">{benefit.title}</h3>
                    <p className="text-gray-600 text-sm">{benefit.description}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      </motion.div>

      {/* Enhanced Verification Modal */}
      {showEnhancedVerification && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={() => setShowEnhancedVerification(false)}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Enhanced Teacher Verification</h2>
                <button
                  onClick={() => setShowEnhancedVerification(false)}
                  className="text-gray-400 hover:text-gray-600 text-2xl"
                >
                  ×
                </button>
              </div>
              <TeacherVerificationForm
                formData={formData}
                onClose={() => setShowEnhancedVerification(false)}
                onSuccess={(result) => {
                  setShowEnhancedVerification(false);
                  toast.success('Registration successful! Your ID is being verified.');
                  navigate('/login?message=registration_successful');
                }}
              />
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
};

export default RegisterPage; 