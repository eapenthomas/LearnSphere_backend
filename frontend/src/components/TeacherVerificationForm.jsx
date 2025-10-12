import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  Camera,
  X
} from 'lucide-react';

const TeacherVerificationForm = ({ onSuccess, formData, onClose }) => {
  const navigate = useNavigate();
  const [idCard, setIdCard] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [errors, setErrors] = useState({});

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const allowedTypes = ['.png', '.jpg', '.jpeg', '.pdf', '.gif', '.bmp'];
      const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      
      if (allowedTypes.includes(fileExtension)) {
        if (file.size > 10 * 1024 * 1024) { // 10MB limit
          toast.error('File size must be less than 10MB');
          return;
        }
        setIdCard(file);
        toast.success('ID card uploaded successfully!');
        setErrors(prev => ({ ...prev, idCard: null }));
      } else {
        toast.error('Please upload a valid image or PDF file');
        setErrors(prev => ({ ...prev, idCard: 'Invalid file format' }));
      }
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!idCard) {
      newErrors.idCard = 'ID card is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setUploading(true);
    
    try {
      const formDataToSend = new FormData();
      formDataToSend.append('full_name', formData.full_name);
      formDataToSend.append('email', formData.email);
      formDataToSend.append('institution_name', formData.institution_name);
      formDataToSend.append('password', formData.password);
      formDataToSend.append('id_card', idCard);

      const response = await fetch('http://localhost:8000/api/teacher-verification/register', {
        method: 'POST',
        body: formDataToSend,
      });

      const result = await response.json();
      
      if (response.ok) {
        // Show appropriate message based on OCR status
        if (result.ocr_status === 'passed') {
          toast.success('Registration successful! Your ID card has been verified and your account is now active.');
        } else {
          toast.error('Registration completed. Your ID verification requires manual review. You will receive an email once reviewed.');
        }
        
        if (onSuccess) {
          onSuccess(result);
        } else {
          navigate('/login?message=registration_successful');
        }
      } else {
        toast.error(result.detail || 'Registration failed');
      }
    } catch (error) {
      console.error('Registration error:', error);
      toast.error('Registration failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Camera className="w-8 h-8 text-blue-600" />
        </div>
        <h3 className="text-xl font-bold text-gray-900">Upload Your ID Card</h3>
        <p className="text-gray-600 mt-2">Complete your enhanced verification</p>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* ID Card Upload */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            ID Card Upload
          </label>
          <div className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
            idCard ? 'border-green-300 bg-green-50' : 'border-gray-300 hover:border-blue-400'
          }`}>
            {idCard ? (
              <div className="space-y-2">
                <CheckCircle className="w-8 h-8 mx-auto text-green-500" />
                <p className="text-green-600 font-medium">{idCard.name}</p>
                <p className="text-sm text-gray-500">
                  {(idCard.size / 1024 / 1024).toFixed(2)} MB
                </p>
                <button
                  type="button"
                  onClick={() => setIdCard(null)}
                  className="text-red-500 text-sm hover:text-red-700"
                >
                  Remove file
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                <Camera className="w-8 h-8 mx-auto text-gray-400" />
                <p className="text-gray-600">Upload your ID Card</p>
                <p className="text-sm text-gray-500">
                  PNG, JPG, JPEG, PDF, GIF, BMP (Max 10MB)
                </p>
                <input
                  type="file"
                  onChange={handleFileUpload}
                  accept=".png,.jpg,.jpeg,.pdf,.gif,.bmp"
                  className="hidden"
                  id="id-card-upload"
                />
                <label
                  htmlFor="id-card-upload"
                  className="inline-block bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 cursor-pointer transition-colors"
                >
                  Choose File
                </label>
              </div>
            )}
          </div>
          {errors.idCard && (
            <p className="text-red-500 text-sm mt-1 flex items-center">
              <AlertCircle className="w-4 h-4 mr-1" />
              {errors.idCard}
            </p>
          )}
        </div>

        {/* Submit Button */}
        <div className="flex gap-3">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 bg-gray-100 text-gray-700 py-3 px-4 rounded-lg font-semibold hover:bg-gray-200 transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={uploading || !idCard}
            className="flex-1 bg-gradient-to-r from-blue-500 to-blue-600 text-white py-3 px-4 rounded-lg font-semibold hover:from-blue-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center"
          >
            {uploading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Verifying...
              </>
            ) : (
              <>
                <Camera className="w-5 h-5 mr-2" />
                Complete Verification
              </>
            )}
          </button>
        </div>
      </form>

      <div className="mt-6 text-center">
        <p className="text-sm text-gray-600">
          Already have an account?{' '}
          <button
            onClick={() => navigate('/login')}
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            Sign in here
          </button>
        </p>
      </div>
    </div>
  );
};

export default TeacherVerificationForm;

