import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext.jsx';
import TeacherDashboardLayout from '../../layouts/TeacherDashboardLayout.jsx';
import { toast } from 'react-hot-toast';
import {
  FileText,
  Calendar,
  Clock,
  Download,
  Upload,
  CheckCircle,
  AlertTriangle,
  Eye,
  Search,
  Filter,
  RefreshCw,
  Plus,
  Users,
  BookOpen,
  Edit,
  Trash2,
  GraduationCap
} from 'lucide-react';

const TeacherAssignments = () => {
  const { user } = useAuth();
  const [assignments, setAssignments] = useState([]);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [courseFilter, setCourseFilter] = useState('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showSubmissionsModal, setShowSubmissionsModal] = useState(false);
  const [selectedAssignment, setSelectedAssignment] = useState(null);
  const [submissions, setSubmissions] = useState([]);
  const [submissionsLoading, setSubmissionsLoading] = useState(false);
  const [editingGrade, setEditingGrade] = useState(null); // Track which submission is being edited

  // Form state for creating assignments
  const [formData, setFormData] = useState({
    course_id: '',
    title: '',
    description: '',
    due_date: '',
    max_score: 100,
    allow_late_submission: false
  });
  const [assignmentFile, setAssignmentFile] = useState(null);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    if (user?.id) {
      fetchAssignments();
      fetchCourses();
    }
  }, [user]);

  const fetchAssignments = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/assignments/teacher/${user.id}`);
      
      if (response.ok) {
        const data = await response.json();
        setAssignments(data);
      } else {
        throw new Error('Failed to fetch assignments');
      }
    } catch (error) {
      console.error('Error fetching assignments:', error);
      toast.error('Failed to load assignments');
    } finally {
      setLoading(false);
    }
  };

  const fetchCourses = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/courses/teacher/${user.id}`);
      
      if (response.ok) {
        const data = await response.json();
        // Backend returns { success: boolean, data: Course[] }
        setCourses(Array.isArray(data) ? data : (data?.data || []));
      } else {
        throw new Error('Failed to fetch courses');
      }
    } catch (error) {
      console.error('Error fetching courses:', error);
      toast.error('Failed to load courses');
    }
  };

  const fetchSubmissions = async (assignmentId) => {
    try {
      setSubmissionsLoading(true);
      const response = await fetch(`http://localhost:8000/api/assignments/submissions/${assignmentId}?teacher_id=${user.id}`);
      
      if (response.ok) {
        const data = await response.json();
        setSubmissions(data);
      } else {
        throw new Error('Failed to fetch submissions');
      }
    } catch (error) {
      console.error('Error fetching submissions:', error);
      toast.error('Failed to load submissions');
    } finally {
      setSubmissionsLoading(false);
    }
  };

  const handleCreateAssignment = async () => {
    if (!formData.course_id || !formData.title || !formData.due_date) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      setCreating(true);
      
      const formDataToSend = new FormData();
      
      // Add assignment data
      const assignmentData = {
        ...formData,
        due_date: new Date(formData.due_date).toISOString()
      };
      
      // Append assignment data as JSON
      Object.keys(assignmentData).forEach(key => {
        formDataToSend.append(key, assignmentData[key]);
      });
      
      // Add file if provided
      if (assignmentFile) {
        formDataToSend.append('file', assignmentFile);
      }

      const response = await fetch(`http://localhost:8000/api/assignments/create?teacher_id=${user.id}`, {
        method: 'POST',
        body: formDataToSend
      });

      if (response.ok) {
        toast.success('Assignment created successfully!');
        setShowCreateModal(false);
        resetForm();
        fetchAssignments();
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create assignment');
      }
    } catch (error) {
      console.error('Error creating assignment:', error);
      toast.error(error.message || 'Failed to create assignment');
    } finally {
      setCreating(false);
    }
  };

  const handleGradeSubmission = async (submissionId, score, feedback = '') => {
    try {
      const response = await fetch(`http://localhost:8000/api/assignments/grade/${submissionId}?teacher_id=${user.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ score, feedback })
      });

      if (response.ok) {
        toast.success('Submission graded successfully!');
        fetchSubmissions(selectedAssignment.id); // Refresh submissions
        fetchAssignments(); // Refresh assignments to update submission counts
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to grade submission');
      }
    } catch (error) {
      console.error('Error grading submission:', error);
      toast.error(error.message || 'Failed to grade submission');
    }
  };

  const handleDownloadFile = async (fileType, fileId) => {
    try {
      // Use backend download API directly
      const response = await fetch(`http://localhost:8000/api/files/download/${fileType}/${fileId}`, {
        headers: {
          'Authorization': `Bearer ${user.accessToken}`
        }
      });
      
      if (response.ok) {
        // Get filename from response headers
        const contentDisposition = response.headers.get('content-disposition');
        let filename = 'file.pdf';
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
      console.error('Error downloading file:', error);
      toast.error('Failed to download file');
    }
  };

  const resetForm = () => {
    setFormData({
      course_id: '',
      title: '',
      description: '',
      due_date: '',
      max_score: 100,
      allow_late_submission: false
    });
    setAssignmentFile(null);
  };

  const filteredAssignments = assignments.filter(assignment => {
    const matchesSearch = assignment.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         assignment.course_title?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCourse = courseFilter === 'all' || assignment.course_id === courseFilter;
    return matchesSearch && matchesCourse;
  });

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getSubmissionStats = (assignment) => {
    const submitted = assignment.submission_count || 0;
    const total = assignment.total_students || 0;
    const percentage = total > 0 ? Math.round((submitted / total) * 100) : 0;
    return { submitted, total, percentage };
  };

  return (
    <TeacherDashboardLayout>
      <div className="min-h-screen teacher-page-bg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-8">
            <div className="mb-4 lg:mb-0">
              <h1 className="text-heading-xl font-bold mb-2 font-serif" style={{color: '#000000'}}>
                Assignment Management
              </h1>
              <p className="text-body-lg" style={{color: '#000000'}}>
                Create and manage assignments for your courses. {filteredAssignments.length} assignment{filteredAssignments.length !== 1 ? 's' : ''} found.
              </p>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={fetchAssignments}
                disabled={loading}
                className="btn-primary px-4 py-3 rounded-lg transition-all duration-300 flex items-center space-x-2 font-medium"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
              
              <button
                onClick={() => setShowCreateModal(true)}
                className="btn-primary px-6 py-3 rounded-lg font-medium transition-all duration-300 flex items-center space-x-2 shadow-elegant hover:shadow-lg"
              >
                <Plus className="w-5 h-5" />
                <span>Create Assignment</span>
              </button>
            </div>
          </div>

          {/* Search and Filters */}
          <div className="teacher-course-card rounded-lg shadow-elegant p-6 mb-8 border border-border-primary">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
              {/* Search */}
              <div className="relative flex-1 lg:max-w-md">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5" style={{color: '#000000'}} />
                <input
                  type="text"
                  placeholder="Search assignments..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all duration-200"
                  style={{color: '#000000', backgroundColor: '#ffffff'}}
                />
              </div>

              {/* Course Filter */}
              <div className="flex items-center space-x-4">
                <label className="text-sm font-medium" style={{color: '#000000'}}>Filter by course:</label>
                <select
                  value={courseFilter}
                  onChange={(e) => setCourseFilter(e.target.value)}
                  className="px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-400 focus:border-transparent"
                  style={{color: '#000000', backgroundColor: '#ffffff'}}
                >
                  <option value="all">All Courses</option>
                  {courses.map(course => (
                    <option key={course.id} value={course.id}>{course.title}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Content */}
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="w-8 h-8 text-primary-500 animate-spin" />
              <span className="ml-3" style={{color: '#000000'}}>Loading assignments...</span>
            </div>
          ) : filteredAssignments.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center py-12"
            >
              <FileText className="w-16 h-16 mx-auto mb-4" style={{color: '#000000'}} />
              <h3 className="text-heading-md font-semibold mb-2" style={{color: '#000000'}}>
                {searchTerm || courseFilter !== 'all' ? 'No assignments found' : 'No assignments created yet'}
              </h3>
              <p className="text-body-lg mb-6" style={{color: '#000000'}}>
                {searchTerm || courseFilter !== 'all'
                  ? 'Try adjusting your search or filter criteria'
                  : 'Create your first assignment to get started'
                }
              </p>
              {!searchTerm && courseFilter === 'all' && (
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="btn-primary px-6 py-3 rounded-lg font-medium flex items-center space-x-2 mx-auto"
                >
                  <Plus className="w-5 h-5" />
                  <span>Create Assignment</span>
                </button>
              )}
            </motion.div>
          ) : (
            <div className="grid gap-6">
              {filteredAssignments.map((assignment, index) => {
                const stats = getSubmissionStats(assignment);
                return (
                  <motion.div
                    key={assignment.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="teacher-course-card rounded-xl p-6 transition-all duration-300"
                  >
                    <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
                      <div className="flex-1 mb-4 lg:mb-0">
                        {/* Assignment Title and Course */}
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <h3 className="text-lg font-semibold mb-1" style={{color: '#000000'}}>
                              {assignment.title}
                            </h3>
                            <div className="flex items-center space-x-2 text-sm" style={{color: '#000000'}}>
                              <BookOpen className="w-4 h-4" />
                              <span>{assignment.course_title}</span>
                            </div>
                          </div>
                        </div>

                        {/* Description */}
                        {assignment.description && (
                          <p className="text-sm mb-3 line-clamp-2" style={{color: '#000000'}}>
                            {assignment.description}
                          </p>
                        )}

                        {/* Stats and Due Date */}
                        <div className="flex items-center space-x-4 text-sm">
                          <div className="flex items-center space-x-1" style={{color: '#000000'}}>
                            <Calendar className="w-4 h-4" />
                            <span>Due: {formatDate(assignment.due_date)}</span>
                          </div>
                          <div className="flex items-center space-x-1" style={{color: '#000000'}}>
                            <Users className="w-4 h-4" />
                            <span>{stats.submitted}/{stats.total} submitted ({stats.percentage}%)</span>
                          </div>
                          <div className="flex items-center space-x-1" style={{color: '#000000'}}>
                            <GraduationCap className="w-4 h-4" />
                            <span>Max Score: {assignment.max_score}</span>
                          </div>
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex items-center space-x-3">
                        {assignment.file_url && (
                          <button
                            onClick={() => handleDownloadFile('assignment', assignment.id)}
                            className="flex items-center space-x-2 px-4 py-2 text-blue-600 hover:text-blue-800 border border-blue-200 rounded-lg hover:bg-blue-50 transition-colors"
                          >
                            <Download className="w-4 h-4" />
                            <span>Download</span>
                          </button>
                        )}
                        
                        <button
                          onClick={() => {
                            setSelectedAssignment(assignment);
                            setShowSubmissionsModal(true);
                            fetchSubmissions(assignment.id);
                          }}
                          className="btn-primary px-4 py-2 rounded-lg flex items-center space-x-2"
                        >
                          <Eye className="w-4 h-4" />
                          <span>View Submissions</span>
                        </button>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Create Assignment Modal */}
      <AnimatePresence>
        {showCreateModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowCreateModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold" style={{color: '#000000'}}>
                  Create New Assignment
                </h3>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="space-y-6">
                {/* Course Selection */}
                <div>
                  <label className="block text-sm font-medium mb-2" style={{color: '#000000'}}>
                    Course *
                  </label>
                  <select
                    value={formData.course_id}
                    onChange={(e) => setFormData({...formData, course_id: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-400 focus:border-transparent"
                    style={{color: '#000000', backgroundColor: '#ffffff'}}
                    required
                  >
                    <option value="">Select a course</option>
                    {courses.map(course => (
                      <option key={course.id} value={course.id}>{course.title}</option>
                    ))}
                  </select>
                </div>

                {/* Assignment Title */}
                <div>
                  <label className="block text-sm font-medium mb-2" style={{color: '#000000'}}>
                    Assignment Title *
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({...formData, title: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-400 focus:border-transparent"
                    style={{color: '#000000', backgroundColor: '#ffffff'}}
                    placeholder="Enter assignment title"
                    required
                  />
                </div>

                {/* Description */}
                <div>
                  <label className="block text-sm font-medium mb-2" style={{color: '#000000'}}>
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-400 focus:border-transparent"
                    style={{color: '#000000', backgroundColor: '#ffffff'}}
                    placeholder="Enter assignment description"
                    rows={4}
                  />
                </div>

                {/* Due Date */}
                <div>
                  <label className="block text-sm font-medium mb-2" style={{color: '#000000'}}>
                    Due Date *
                  </label>
                  <input
                    type="datetime-local"
                    value={formData.due_date}
                    onChange={(e) => setFormData({...formData, due_date: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-400 focus:border-transparent"
                    style={{color: '#000000', backgroundColor: '#ffffff'}}
                    required
                  />
                </div>

                {/* Max Score */}
                <div>
                  <label className="block text-sm font-medium mb-2" style={{color: '#000000'}}>
                    Maximum Score
                  </label>
                  <input
                    type="number"
                    value={formData.max_score}
                    onChange={(e) => setFormData({...formData, max_score: parseInt(e.target.value)})}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-400 focus:border-transparent"
                    style={{color: '#000000', backgroundColor: '#ffffff'}}
                    min="1"
                    max="1000"
                  />
                </div>

                {/* File Upload */}
                <div>
                  <label className="block text-sm font-medium mb-2" style={{color: '#000000'}}>
                    Assignment File (PDF or DOCX, max 10MB)
                  </label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                    <input
                      type="file"
                      accept=".pdf,.docx,.doc"
                      onChange={(e) => setAssignmentFile(e.target.files[0])}
                      className="hidden"
                      id="assignment-file"
                    />
                    <label
                      htmlFor="assignment-file"
                      className="cursor-pointer flex flex-col items-center space-y-2"
                    >
                      <Upload className="w-8 h-8 text-gray-400" />
                      <span className="text-sm" style={{color: '#000000'}}>
                        {assignmentFile ? assignmentFile.name : 'Click to upload file (optional)'}
                      </span>
                    </label>
                  </div>
                </div>

                {/* Allow Late Submission */}
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="allow-late"
                    checked={formData.allow_late_submission}
                    onChange={(e) => setFormData({...formData, allow_late_submission: e.target.checked})}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="allow-late" className="text-sm" style={{color: '#000000'}}>
                    Allow late submissions
                  </label>
                </div>
              </div>

              <div className="flex items-center justify-end space-x-3 mt-8">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="px-6 py-2 text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateAssignment}
                  disabled={creating || !formData.course_id || !formData.title || !formData.due_date}
                  className="btn-primary px-6 py-2 rounded-lg flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {creating ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>Creating...</span>
                    </>
                  ) : (
                    <>
                      <Plus className="w-4 h-4" />
                      <span>Create Assignment</span>
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Submissions Modal */}
      <AnimatePresence>
        {showSubmissionsModal && selectedAssignment && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowSubmissionsModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white rounded-xl shadow-2xl max-w-6xl w-full max-h-[90vh] overflow-y-auto p-6"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-xl font-semibold" style={{color: '#000000'}}>
                    Submissions for: {selectedAssignment.title}
                  </h3>
                  <p className="text-sm" style={{color: '#000000'}}>
                    Course: {selectedAssignment.course_title}
                  </p>
                </div>
                <button
                  onClick={() => setShowSubmissionsModal(false)}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {submissionsLoading ? (
                <div className="flex items-center justify-center py-12">
                  <RefreshCw className="w-8 h-8 text-primary-500 animate-spin" />
                  <span className="ml-3" style={{color: '#000000'}}>Loading submissions...</span>
                </div>
              ) : submissions.length === 0 ? (
                <div className="text-center py-12">
                  <FileText className="w-16 h-16 mx-auto mb-4" style={{color: '#000000'}} />
                  <h4 className="text-lg font-semibold mb-2" style={{color: '#000000'}}>
                    No submissions yet
                  </h4>
                  <p style={{color: '#000000'}}>
                    Students haven't submitted their assignments yet.
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {submissions.map((submission) => (
                    <div
                      key={submission.id}
                      className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-4 mb-2">
                            <h5 className="font-medium" style={{color: '#000000'}}>
                              {submission.student_name}
                            </h5>
                            <span className="text-sm" style={{color: '#000000'}}>
                              {submission.student_email}
                            </span>
                            <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                              submission.status === 'reviewed'
                                ? 'bg-green-100 text-green-700'
                                : submission.is_late_submission
                                ? 'bg-orange-100 text-orange-700'
                                : 'bg-blue-100 text-blue-700'
                            }`}>
                              {submission.is_late_submission && submission.status !== 'reviewed' ? 'Late' : submission.status}
                            </div>
                          </div>

                          <div className="flex items-center space-x-4 text-sm" style={{color: '#000000'}}>
                            <span>Submitted: {formatDate(submission.submitted_at)}</span>
                            {submission.score !== null && (
                              <span className="font-medium text-green-600">
                                Score: {submission.score}/{selectedAssignment.max_score}
                              </span>
                            )}
                          </div>

                          {submission.feedback && (
                            <div className="mt-2 p-2 bg-gray-100 rounded text-sm" style={{color: '#000000'}}>
                              <strong>Feedback:</strong> {submission.feedback}
                            </div>
                          )}
                        </div>

                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => handleDownloadFile('submission', submission.id)}
                            className="flex items-center space-x-1 px-3 py-2 text-blue-600 hover:text-blue-800 border border-blue-200 rounded-lg hover:bg-blue-50 transition-colors"
                          >
                            <Download className="w-4 h-4" />
                            <span>Download</span>
                          </button>

                          {submission.status !== 'reviewed' ? (
                            <div className="flex items-center space-x-2">
                              <input
                                type="number"
                                placeholder="Score"
                                min="0"
                                max={selectedAssignment.max_score}
                                className="w-20 px-2 py-1 border border-gray-300 rounded text-sm"
                                style={{color: '#000000', backgroundColor: '#ffffff'}}
                                onKeyDown={(e) => {
                                  if (e.key === 'Enter') {
                                    const score = parseInt(e.target.value);
                                    if (score >= 0 && score <= selectedAssignment.max_score) {
                                      handleGradeSubmission(submission.id, score);
                                      e.target.value = '';
                                    }
                                  }
                                }}
                              />
                              <button
                                onClick={(e) => {
                                  const scoreInput = e.target.parentElement.querySelector('input[type="number"]');
                                  const score = parseInt(scoreInput.value);
                                  if (score >= 0 && score <= selectedAssignment.max_score) {
                                    handleGradeSubmission(submission.id, score);
                                    scoreInput.value = '';
                                  }
                                }}
                                className="btn-primary px-3 py-1 rounded text-sm"
                              >
                                Grade
                              </button>
                            </div>
                          ) : (
                            <div className="flex items-center space-x-2">
                              {editingGrade === submission.id ? (
                                <div className="flex items-center space-x-2">
                                  <input
                                    type="number"
                                    defaultValue={submission.score}
                                    min="0"
                                    max={selectedAssignment.max_score}
                                    className="w-20 px-2 py-1 border border-gray-300 rounded text-sm"
                                    style={{color: '#000000', backgroundColor: '#ffffff'}}
                                    onKeyDown={(e) => {
                                      if (e.key === 'Enter') {
                                        const score = parseInt(e.target.value);
                                        if (score >= 0 && score <= selectedAssignment.max_score) {
                                          handleGradeSubmission(submission.id, score);
                                          setEditingGrade(null);
                                        }
                                      }
                                    }}
                                    autoFocus
                                  />
                                  <button
                                    onClick={(e) => {
                                      const scoreInput = e.target.parentElement.querySelector('input[type="number"]');
                                      const score = parseInt(scoreInput.value);
                                      if (score >= 0 && score <= selectedAssignment.max_score) {
                                        handleGradeSubmission(submission.id, score);
                                        setEditingGrade(null);
                                      }
                                    }}
                                    className="btn-primary px-3 py-1 rounded text-sm"
                                  >
                                    Save
                                  </button>
                                  <button
                                    onClick={() => setEditingGrade(null)}
                                    className="px-3 py-1 rounded text-sm border border-gray-300 hover:bg-gray-50"
                                  >
                                    Cancel
                                  </button>
                                </div>
                              ) : (
                                <button
                                  onClick={() => setEditingGrade(submission.id)}
                                  className="flex items-center space-x-1 px-3 py-1 text-orange-600 hover:text-orange-800 border border-orange-200 rounded text-sm hover:bg-orange-50 transition-colors"
                                >
                                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                  </svg>
                                  <span>Edit Grade</span>
                                </button>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </TeacherDashboardLayout>
  );
};

export default TeacherAssignments;
