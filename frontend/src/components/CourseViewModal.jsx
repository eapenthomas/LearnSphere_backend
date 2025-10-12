import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  BookOpen,
  Calendar,
  Users,
  FileText,
  Upload,
  Download,
  Trash2,
  Plus,
  Eye,
  Clock,
  Tag
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';

const CourseViewModal = ({ isOpen, onClose, course }) => {
  const auth = useAuth();
  const user = auth?.user;
  const [materials, setMaterials] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploadingFile, setUploadingFile] = useState(false);
  
  // Check if user is a teacher (can upload/delete materials)
  const isTeacher = user?.role === 'teacher';

  useEffect(() => {
    if (isOpen && course) {
      fetchCourseMaterials();
    }
  }, [isOpen, course]);

  const fetchCourseMaterials = async () => {
    try {
      setLoading(true);
      console.log('Fetching materials for course:', course.id);
      
      const headers = {};
      if (user?.id) {
        headers['Authorization'] = `Bearer ${user.id}`;
      }
      
      const response = await fetch(`http://localhost:8000/api/course-materials/course/${course.id}`, {
        headers
      });
      if (response.ok) {
        const result = await response.json();
        setMaterials(result.materials || []);
      } else {
        console.log('No materials found or error fetching materials');
        setMaterials([]);
      }
    } catch (error) {
      console.error('Error fetching course materials:', error);
      setMaterials([]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      setUploadingFile(true);
      console.log('Uploading file:', file.name);

      const formData = new FormData();
      formData.append('files', file); // Changed from 'file' to 'files'
      formData.append('course_id', course.id);
      formData.append('description', `Uploaded file: ${file.name}`); // Removed 'title'

      const headers = {};
      if (user?.id) {
        headers['Authorization'] = `Bearer ${user.id}`;
      }

      const response = await fetch('http://localhost:8000/api/course-materials/upload', {
        method: 'POST',
        headers,
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        toast.success('File uploaded successfully!');
        fetchCourseMaterials(); // Refresh materials list
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Upload failed');
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      toast.error(`Upload failed: ${error.message}`);
    } finally {
      setUploadingFile(false);
      event.target.value = ''; // Reset file input
    }
  };

  const handleDeleteMaterial = async (materialId) => {
    try {
      const headers = {};
      if (user?.id) {
        headers['Authorization'] = `Bearer ${user.id}`;
      }

      const response = await fetch(`http://localhost:8000/api/course-materials/${materialId}`, {
        method: 'DELETE',
        headers
      });

      if (response.ok) {
        toast.success('Material deleted successfully!');
        fetchCourseMaterials(); // Refresh materials list
      } else {
        throw new Error('Delete failed');
      }
    } catch (error) {
      console.error('Error deleting material:', error);
      toast.error('Failed to delete material');
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!course || !auth) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
            className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[95vh] overflow-hidden flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <BookOpen className="w-8 h-8" />
                  <div>
                    <h2 className="text-2xl font-bold">{course.title}</h2>
                    <p className="text-blue-100">Course Code: {course.code}</p>
                  </div>
                </div>
                <button
                  onClick={onClose}
                  className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
              {/* Course Info */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3" style={{color: '#000000'}}>Course Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-center space-x-2" style={{color: '#000000'}}>
                    <Tag className="w-4 h-4" />
                    <span>Status: <span className="font-medium">{course.status}</span></span>
                  </div>
                  <div className="flex items-center space-x-2" style={{color: '#000000'}}>
                    <Calendar className="w-4 h-4" />
                    <span>Created: {formatDate(course.created_at)}</span>
                  </div>
                </div>
                {course.description && (
                  <div className="mt-3">
                    <p style={{color: '#000000'}}>{course.description}</p>
                  </div>
                )}
              </div>

              {/* Course Materials */}
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-800">Course Materials</h3>
                  {isTeacher && (
                    <div className="flex items-center space-x-2">
                      <input
                        type="file"
                        id="file-upload"
                        className="hidden"
                        onChange={handleFileUpload}
                        disabled={uploadingFile}
                      />
                      <label
                        htmlFor="file-upload"
                        className={`px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 cursor-pointer ${
                          uploadingFile ? 'opacity-50 cursor-not-allowed' : ''
                        }`}
                      >
                        <Upload className="w-4 h-4" />
                        <span>{uploadingFile ? 'Uploading...' : 'Upload File'}</span>
                      </label>
                    </div>
                  )}
                </div>

                {loading ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="text-gray-600 mt-2">Loading materials...</p>
                  </div>
                ) : materials.length > 0 ? (
                  <div className="space-y-3">
                    {materials.map((material) => (
                      <div
                        key={material.id}
                        className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border"
                      >
                        <div className="flex items-center space-x-3">
                          <FileText className="w-5 h-5 text-blue-600" />
                          <div>
                            <h4 className="font-medium text-gray-800">{material.file_name}</h4>
                            <p className="text-sm text-gray-600">
                              {formatFileSize(material.file_size)} • {formatDate(material.uploaded_at)}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={async () => {
                              try {
                                // Use backend download API
                                const response = await fetch(`http://localhost:8000/api/files/download/course-material/${material.id}`, {
                                  headers: {
                                    'Authorization': `Bearer ${user.accessToken}`
                                  }
                                });
                                
                                if (response.ok) {
                                  // Get filename from response headers or use material name
                                  const contentDisposition = response.headers.get('content-disposition');
                                  let filename = material.file_name || 'material';
                                  if (contentDisposition) {
                                    const filenameMatch = contentDisposition.match(/filename="(.+)"/);
                                    if (filenameMatch) {
                                      filename = filenameMatch[1];
                                    }
                                  }
                                  
                                  // Create blob and download
                                  const blob = await response.blob();
                                  const url = window.URL.createObjectURL(blob);
                                  const link = document.createElement('a');
                                  link.href = url;
                                  link.download = filename;
                                  document.body.appendChild(link);
                                  link.click();
                                  document.body.removeChild(link);
                                  window.URL.revokeObjectURL(url);
                                  
                                  toast.success('Download started!');
                                } else {
                                  throw new Error('Failed to download file');
                                }
                              } catch (error) {
                                console.error('Error downloading material:', error);
                                toast.error('Failed to download file');
                              }
                            }}
                            className="p-2 text-blue-600 hover:bg-blue-100 rounded-lg transition-colors"
                            title="Download"
                          >
                            <Download className="w-4 h-4" />
                          </button>
                          {isTeacher && (
                            <button
                              onClick={() => handleDeleteMaterial(material.id)}
                              className="p-2 text-red-600 hover:bg-red-100 rounded-lg transition-colors"
                              title="Delete"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <FileText className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                    <p>No materials uploaded yet</p>
                    {isTeacher ? (
                      <p className="text-sm">Upload files to share with your students</p>
                    ) : (
                      <p className="text-sm">Check back later for course materials</p>
                    )}
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default CourseViewModal;
