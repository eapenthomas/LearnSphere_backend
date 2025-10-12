import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import {
  X,
  Upload,
  Image as ImageIcon,
  Loader,
  Save,
  AlertCircle,
  CheckCircle
} from 'lucide-react';

// Validation schema
const courseSchema = yup.object().shape({
  title: yup
    .string()
    .required('Course title is required')
    .min(3, 'Title must be at least 3 characters')
    .max(100, 'Title must be less than 100 characters'),
  description: yup
    .string()
    .max(500, 'Description must be less than 500 characters'),
  status: yup
    .string()
    .oneOf(['active', 'draft'], 'Status must be either active or draft')
    .required('Status is required'),
  is_paid: yup.boolean(),
  price: yup
    .number()
    .when('is_paid', {
      is: true,
      then: (schema) => schema.required('Price is required for paid courses').min(1, 'Price must be at least ₹1'),
      otherwise: (schema) => schema.notRequired()
    })
});

const CourseFormModal = ({ 
  isOpen, 
  onClose, 
  onSubmit, 
  course = null, 
  loading = false 
}) => {
  const [thumbnailFile, setThumbnailFile] = useState(null);
  const [thumbnailPreview, setThumbnailPreview] = useState(null);
  const [uploadingThumbnail, setUploadingThumbnail] = useState(false);

  const isEditing = !!course;

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
    watch
  } = useForm({
    resolver: yupResolver(courseSchema),
    defaultValues: {
      title: '',
      description: '',
      status: 'active',
      is_paid: false,
      price: 0
    }
  });

  // Reset form when modal opens/closes or course changes
  useEffect(() => {
    if (isOpen) {
      if (course) {
        setValue('title', course.title || '');
        setValue('description', course.description || '');
        setValue('status', course.status || 'active');
        setValue('is_paid', course.is_paid || false);
        setValue('price', course.price || 0);
        setThumbnailPreview(course.thumbnail_url || null);
      } else {
        reset({
          title: '',
          description: '',
          status: 'active',
          is_paid: false,
          price: 0
        });
        setThumbnailPreview(null);
      }
      setThumbnailFile(null);
    }
  }, [isOpen, course, setValue, reset]);

  const handleThumbnailChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
      }

      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert('File size must be less than 5MB');
        return;
      }

      setThumbnailFile(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setThumbnailPreview(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleFormSubmit = async (data) => {
    try {
      await onSubmit({
        ...data,
        thumbnailFile,
        id: course?.id
      });
    } catch (error) {
      console.error('Form submission error:', error);
    }
  };

  const handleClose = () => {
    reset();
    setThumbnailFile(null);
    setThumbnailPreview(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className="bg-white shadow rounded-xl border border-gray-200 w-full max-w-2xl max-h-[95vh] overflow-hidden flex flex-col"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-100">
            <h2 className="text-xl font-semibold text-gray-900">
              {isEditing ? 'Edit Course' : 'Create New Course'}
            </h2>
            <button
              onClick={handleClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit(handleFormSubmit)} className="flex flex-col flex-1 min-h-0">
            <div className="px-6 pt-6 pb-2 space-y-6 overflow-y-auto flex-1 min-h-0">
              {/* Course Title */}
              <div>
                <label className="block text-sm font-semibold mb-2" style={{color: '#000000'}}>
                  Course Title *
                </label>
                <input
                  type="text"
                  {...register('title')}
                  className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:border-transparent transition-all duration-200 ${
                    errors.title
                      ? 'border-red-300 focus:ring-red-400'
                      : 'border-gray-200 focus:ring-blue-400'
                  }`}
                  style={{color: '#000000', backgroundColor: '#ffffff'}}
                  placeholder="Enter course title"
                />
                {errors.title && (
                  <motion.p
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-2 text-sm text-red-600 flex items-center"
                  >
                    <AlertCircle className="w-4 h-4 mr-1" />
                    {errors.title.message}
                  </motion.p>
                )}
              </div>

              {/* Course Description */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Course Description
                </label>
                <textarea
                  {...register('description')}
                  rows={4}
                  className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:border-transparent transition-all duration-200 resize-none text-gray-900 placeholder-gray-500 ${
                    errors.description
                      ? 'border-red-300 focus:ring-red-400'
                      : 'border-gray-200 focus:ring-indigo-400'
                  }`}
                  placeholder="Enter course description (optional)"
                />
                {errors.description && (
                  <motion.p
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-2 text-sm text-red-600 flex items-center"
                  >
                    <AlertCircle className="w-4 h-4 mr-1" />
                    {errors.description.message}
                  </motion.p>
                )}
              </div>

              {/* Thumbnail Upload */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Course Thumbnail
                </label>
                
                {/* Thumbnail Preview */}
                {thumbnailPreview && (
                  <div className="mb-4">
                    <img
                      src={thumbnailPreview}
                      alt="Thumbnail preview"
                      className="w-full h-32 object-cover rounded-xl border border-gray-200"
                    />
                  </div>
                )}

                {/* Upload Button */}
                <div className="relative">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleThumbnailChange}
                    className="hidden"
                    id="thumbnail-upload"
                  />
                  <label
                    htmlFor="thumbnail-upload"
                    className="flex items-center justify-center w-full h-32 border-2 border-dashed border-gray-300 rounded-xl hover:border-indigo-400 hover:bg-indigo-50 transition-all duration-200 cursor-pointer"
                  >
                    <div className="text-center">
                      {uploadingThumbnail ? (
                        <Loader className="w-8 h-8 text-indigo-500 animate-spin mx-auto mb-2" />
                      ) : (
                        <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                      )}
                      <p className="text-sm text-gray-600">
                        {thumbnailPreview ? 'Change thumbnail' : 'Upload thumbnail'}
                      </p>
                      <p className="text-xs text-gray-400">PNG, JPG up to 5MB</p>
                    </div>
                  </label>
                </div>
              </div>

              {/* Course Type and Pricing */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  Course Type
                </label>
                <div className="space-y-4">
                  {/* Free/Paid Toggle */}
                  <div className="flex items-center space-x-6">
                    <label className="flex items-center">
                      <input
                        type="radio"
                        {...register('is_paid')}
                        value={false}
                        className="mr-2 text-indigo-600"
                      />
                      <span className="text-gray-700">Free Course</span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="radio"
                        {...register('is_paid')}
                        value={true}
                        className="mr-2 text-indigo-600"
                      />
                      <span className="text-gray-700">Paid Course</span>
                    </label>
                  </div>

                  {/* Price Input (shown only for paid courses) */}
                  {watch('is_paid') === 'true' && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="mt-4"
                    >
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Price (₹) *
                      </label>
                      <input
                        type="number"
                        {...register('price', { valueAsNumber: true })}
                        min="1"
                        step="1"
                        className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:border-transparent transition-all duration-200 text-gray-900 ${
                          errors.price
                            ? 'border-red-300 focus:ring-red-400'
                            : 'border-gray-200 focus:ring-indigo-400'
                        }`}
                        placeholder="Enter course price"
                      />
                      {errors.price && (
                        <motion.p
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="mt-2 text-sm text-red-600 flex items-center"
                        >
                          <AlertCircle className="w-4 h-4 mr-1" />
                          {errors.price.message}
                        </motion.p>
                      )}
                    </motion.div>
                  )}
                </div>
              </div>

              {/* Status */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Course Status *
                </label>
                <select
                  {...register('status')}
                  className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:border-transparent transition-all duration-200 text-gray-900 ${
                    errors.status
                      ? 'border-red-300 focus:ring-red-400'
                      : 'border-gray-200 focus:ring-indigo-400'
                  }`}
                >
                  <option value="active">Active</option>
                  <option value="draft">Draft</option>
                </select>
                {errors.status && (
                  <motion.p
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-2 text-sm text-red-600 flex items-center"
                  >
                    <AlertCircle className="w-4 h-4 mr-1" />
                    {errors.status.message}
                  </motion.p>
                )}
              </div>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-end space-x-4 p-6 border-t border-gray-100 flex-shrink-0 bg-white">
              <button
                type="button"
                onClick={handleClose}
                className="px-6 py-2 text-gray-600 hover:text-gray-800 font-medium transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className={`px-6 py-2 bg-gradient-to-r from-indigo-500 to-blue-500 text-white font-semibold rounded-xl shadow-md hover:shadow-lg transition-all duration-200 flex items-center space-x-2 ${
                  loading ? 'opacity-50 cursor-not-allowed' : 'hover:from-indigo-600 hover:to-blue-600'
                }`}
              >
                {loading ? (
                  <>
                    <Loader className="w-4 h-4 animate-spin" />
                    <span>{isEditing ? 'Updating...' : 'Creating...'}</span>
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    <span>{isEditing ? 'Update Course' : 'Create Course'}</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};

export default CourseFormModal;
