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
  Tag,
  Play,
  CheckCircle,
  BarChart3,
  Target,
  Timer,
  TrendingUp,
  Award,
  Star
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';
import TeacherRatingModal from './TeacherRatingModal.jsx';

const EnhancedCourseViewModal = ({ isOpen, onClose, course }) => {
  const auth = useAuth();
  const user = auth?.user;
  const [materials, setMaterials] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploadingFile, setUploadingFile] = useState(false);
  const [courseProgress, setCourseProgress] = useState(null);
  const [materialProgress, setMaterialProgress] = useState({});
  const [activeTab, setActiveTab] = useState('materials');
  const [showRatingModal, setShowRatingModal] = useState(false);
  const [enrollmentCount, setEnrollmentCount] = useState(0);
  
  // Check if user is a teacher (can upload/delete materials)
  const isTeacher = user?.role === 'teacher';
  const isStudent = user?.role === 'student';

  useEffect(() => {
    if (isOpen && course) {
      fetchCourseMaterials();
      fetchEnrollmentCount();
      if (isStudent) {
        fetchCourseProgress();
      }
    }
  }, [isOpen, course]);

  const fetchEnrollmentCount = async () => {
    try {
      console.log('Fetching enrollment count for course:', course.id);
      
      const response = await fetch('http://localhost:8000/api/courses/all');
      if (response.ok) {
        const result = await response.json();
        const allCourses = result.data || [];
        
        // Find the current course and get its enrollment count
        const currentCourse = allCourses.find(c => c.id === course.id);
        if (currentCourse) {
          setEnrollmentCount(currentCourse.enrollment_count || 0);
          console.log(`Enrollment count for ${course.title}: ${currentCourse.enrollment_count}`);
        } else {
          setEnrollmentCount(0);
        }
      } else {
        console.log('Error fetching enrollment count');
        setEnrollmentCount(0);
      }
    } catch (error) {
      console.error('Error fetching enrollment count:', error);
      setEnrollmentCount(0);
    }
  };

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

  const fetchCourseProgress = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/progress/course/${course.id}/student/${user.id}`);
      if (response.ok) {
        const progress = await response.json();
        setCourseProgress(progress);
      }
    } catch (error) {
      console.error('Error fetching course progress:', error);
    }
  };

  const trackMaterialView = async (material) => {
    if (!isStudent) return;

    try {
      // Mark material as completed when viewed
      await fetch(`http://localhost:8000/api/progress/material/track?student_id=${user.id}&course_id=${course.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          material_id: material.id,
          status: 'completed', // Auto-complete on view
          progress_percentage: 100,
          time_spent: 60 // 1 minute for viewing
        })
      });

      // Update local progress state
      setMaterialProgress(prev => ({
        ...prev,
        [material.id]: {
          ...prev[material.id],
          status: 'completed',
          progress_percentage: 100,
          view_count: (prev[material.id]?.view_count || 0) + 1
        }
      }));

      // Show success message
      toast.success(`"${material.title}" marked as completed!`);

      // Refresh course progress
      fetchCourseProgress();

      // Trigger dashboard refresh by dispatching custom event
      window.dispatchEvent(new CustomEvent('progressUpdated', {
        detail: { courseId: course.id, studentId: user.id }
      }));
    } catch (error) {
      console.error('Error tracking material view:', error);
      toast.error('Failed to track progress');
    }
  };

  const trackMaterialDownload = async (material) => {
    if (!isStudent) return;

    try {
      // Mark material as completed when downloaded
      await fetch(`http://localhost:8000/api/progress/material/track?student_id=${user.id}&course_id=${course.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          material_id: material.id,
          status: 'completed', // Auto-complete on download
          progress_percentage: 100,
          time_spent: 30 // 30 seconds for download
        })
      });

      // Also track the download specifically
      await fetch(`http://localhost:8000/api/progress/material/download?student_id=${user.id}&course_id=${course.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          material_id: material.id
        })
      });

      // Update local progress state
      setMaterialProgress(prev => ({
        ...prev,
        [material.id]: {
          ...prev[material.id],
          status: 'completed',
          progress_percentage: 100,
          download_count: (prev[material.id]?.download_count || 0) + 1
        }
      }));

      // Show success message
      toast.success(`"${material.title}" downloaded and marked as completed!`);

      // Refresh course progress
      fetchCourseProgress();

      // Trigger dashboard refresh by dispatching custom event
      window.dispatchEvent(new CustomEvent('progressUpdated', {
        detail: { courseId: course.id, studentId: user.id }
      }));
    } catch (error) {
      console.error('Error tracking material download:', error);
      toast.error('Failed to track download progress');
    }
  };

  const markMaterialComplete = async (material) => {
    if (!isStudent) return;
    
    try {
      await fetch(`http://localhost:8000/api/progress/material/track?student_id=${user.id}&course_id=${course.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          material_id: material.id,
          status: 'completed',
          progress_percentage: 100,
          time_spent: 60 // 1 minute for completion
        })
      });
      
      // Update local progress state
      setMaterialProgress(prev => ({
        ...prev,
        [material.id]: { ...prev[material.id], status: 'completed' }
      }));
      
      // Refresh course progress
      fetchCourseProgress();
      toast.success('Material marked as completed!');
    } catch (error) {
      console.error('Error marking material complete:', error);
      toast.error('Failed to mark material as completed');
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      setUploadingFile(true);
      const formData = new FormData();
      formData.append('files', file);
      formData.append('course_id', course.id);
      formData.append('description', `Course material: ${file.name}`);

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
        toast.success('File uploaded successfully!');
        fetchCourseMaterials();
      } else {
        const error = await response.text();
        toast.error(`Upload failed: ${error}`);
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      toast.error('Upload failed');
    } finally {
      setUploadingFile(false);
      event.target.value = '';
    }
  };

  const handleDeleteMaterial = async (materialId) => {
    if (!confirm('Are you sure you want to delete this material?')) return;

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
        fetchCourseMaterials();
      } else {
        toast.error('Failed to delete material');
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
    return new Date(dateString).toLocaleDateString();
  };

  const getProgressColor = (percentage) => {
    if (percentage >= 80) return 'bg-green-500';
    if (percentage >= 50) return 'bg-yellow-500';
    return 'bg-blue-500';
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key="course-modal"
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
          className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <h2 className="text-2xl font-bold mb-2">{course?.title}</h2>
                <p className="text-blue-100 mb-4">{course?.description}</p>
                
                {/* Course Stats */}
                <div className="flex flex-wrap gap-4 text-sm">
                  <div className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    <span>Created: {formatDate(course?.created_at)}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Users className="w-4 h-4" />
                    <span>{enrollmentCount} students</span>
                  </div>
                  {isStudent && courseProgress && (
                    <div className="flex items-center gap-1">
                      <Target className="w-4 h-4" />
                      <span>{courseProgress.overall_progress_percentage}% Complete</span>
                    </div>
                  )}
                </div>

                {/* Rate Teacher Button for Students */}
                {isStudent && (
                  <div className="mt-4">
                    <button
                      onClick={() => setShowRatingModal(true)}
                      className="flex items-center space-x-2 px-4 py-2 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg transition-colors text-white"
                    >
                      <Star className="w-4 h-4" />
                      <span>Rate Teacher</span>
                    </button>
                  </div>
                )}
              </div>
              <button
                onClick={onClose}
                className="text-white hover:text-gray-200 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>

          {/* Progress Bar for Students */}
          {isStudent && courseProgress && (
            <div className="px-6 py-4 bg-gray-50 border-b">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Course Progress</span>
                <span className="text-sm text-gray-600">
                  {courseProgress.materials_completed} of {courseProgress.total_materials} materials completed
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(courseProgress.overall_progress_percentage)}`}
                  style={{ width: `${courseProgress.overall_progress_percentage}%` }}
                ></div>
              </div>
            </div>
          )}

          {/* Tabs */}
          <div className="border-b">
            <div className="flex">
              <button
                onClick={() => setActiveTab('materials')}
                className={`px-6 py-3 font-medium transition-colors ${
                  activeTab === 'materials'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                <FileText className="w-4 h-4 inline mr-2" />
                Materials
              </button>
              {isStudent && (
                <button
                  onClick={() => setActiveTab('progress')}
                  className={`px-6 py-3 font-medium transition-colors ${
                    activeTab === 'progress'
                      ? 'text-blue-600 border-b-2 border-blue-600'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  <BarChart3 className="w-4 h-4 inline mr-2" />
                  Progress
                </button>
              )}
            </div>
          </div>

          {/* Content */}
          <div className="p-6 max-h-96 overflow-y-auto">
            {activeTab === 'materials' && (
              <div>
                {/* Upload Section for Teachers */}
                {isTeacher && (
                  <div className="mb-6 p-4 bg-blue-50 rounded-lg border-2 border-dashed border-blue-300">
                    <div className="text-center">
                      <Upload className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                      <p className="text-blue-800 font-medium mb-2">Upload Course Materials</p>
                      <input
                        type="file"
                        onChange={handleFileUpload}
                        disabled={uploadingFile}
                        className="hidden"
                        id="file-upload"
                        accept=".pdf,.doc,.docx,.ppt,.pptx,.txt,.jpg,.jpeg,.png,.mp4,.mp3"
                      />
                      <label
                        htmlFor="file-upload"
                        className={`inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg cursor-pointer hover:bg-blue-700 transition-colors ${
                          uploadingFile ? 'opacity-50 cursor-not-allowed' : ''
                        }`}
                      >
                        {uploadingFile ? (
                          <>
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                            Uploading...
                          </>
                        ) : (
                          <>
                            <Plus className="w-4 h-4 mr-2" />
                            Choose File
                          </>
                        )}
                      </label>
                    </div>
                  </div>
                )}

                {/* Materials List */}
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
                        className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border hover:bg-gray-100 transition-colors"
                      >
                        <div className="flex items-center space-x-3 flex-1">
                          <FileText className="w-5 h-5 text-blue-600" />
                          <div className="flex-1">
                            <h4 className="font-medium text-gray-800">{material.file_name}</h4>
                            <p className="text-sm text-gray-600">
                              {formatFileSize(material.file_size)} • {formatDate(material.uploaded_at)}
                            </p>
                            {isStudent && materialProgress[material.id] && (
                              <div className="flex items-center gap-2 mt-1">
                                {materialProgress[material.id].status === 'completed' && (
                                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
                                    <CheckCircle className="w-3 h-3 mr-1" />
                                    Completed
                                  </span>
                                )}
                                <span className="text-xs text-gray-500">
                                  Views: {materialProgress[material.id].view_count || 0} • 
                                  Downloads: {materialProgress[material.id].download_count || 0}
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => {
                              trackMaterialView(material);
                              // Open in new tab using backend view API for inline viewing
                              window.open(`http://localhost:8000/api/files/view/material/${material.id}`, '_blank');
                            }}
                            className="p-2 text-blue-600 hover:bg-blue-100 rounded-lg transition-colors"
                            title="View"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          <button
                            onClick={async () => {
                              trackMaterialDownload(material);
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
                            className="p-2 text-green-600 hover:bg-green-100 rounded-lg transition-colors"
                            title="Download"
                          >
                            <Download className="w-4 h-4" />
                          </button>
                          {isStudent && (
                            <button
                              onClick={() => markMaterialComplete(material)}
                              className="p-2 text-purple-600 hover:bg-purple-100 rounded-lg transition-colors"
                              title="Mark as Complete"
                            >
                              <CheckCircle className="w-4 h-4" />
                            </button>
                          )}
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
            )}

            {activeTab === 'progress' && isStudent && courseProgress && (
              <div className="space-y-6">
                {/* Overall Progress Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-blue-600 font-medium">Overall Progress</p>
                        <p className="text-2xl font-bold text-blue-800">{courseProgress.overall_progress_percentage}%</p>
                      </div>
                      <Target className="w-8 h-8 text-blue-600" />
                    </div>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-green-600 font-medium">Materials Completed</p>
                        <p className="text-2xl font-bold text-green-800">
                          {courseProgress.materials_completed}/{courseProgress.total_materials}
                        </p>
                      </div>
                      <CheckCircle className="w-8 h-8 text-green-600" />
                    </div>
                  </div>
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-purple-600 font-medium">Time Spent</p>
                        <p className="text-2xl font-bold text-purple-800">
                          {Math.floor(courseProgress.total_time_spent / 60)}m
                        </p>
                      </div>
                      <Timer className="w-8 h-8 text-purple-600" />
                    </div>
                  </div>
                </div>

                {/* Achievement Badge */}
                {courseProgress.overall_progress_percentage >= 100 && (
                  <div className="bg-gradient-to-r from-yellow-400 to-orange-500 p-4 rounded-lg text-white text-center">
                    <Award className="w-8 h-8 mx-auto mb-2" />
                    <h3 className="font-bold text-lg">Course Completed!</h3>
                    <p className="text-sm opacity-90">Congratulations on completing this course!</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>

      {/* Teacher Rating Modal */}
      <TeacherRatingModal
        isOpen={showRatingModal}
        onClose={() => setShowRatingModal(false)}
        teacher={{
          id: course?.teacher_id,
          name: course?.teacher_name || 'Teacher'
        }}
        course={{
          id: course?.id,
          title: course?.title
        }}
      />
    </AnimatePresence>
  );
};

export default EnhancedCourseViewModal;
