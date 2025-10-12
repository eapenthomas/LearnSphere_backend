import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext.jsx';
import DashboardLayout from '../../components/DashboardLayout.jsx';
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
  BookOpen,
  User,
  Timer
} from 'lucide-react';

const StudentAssignments = () => {
  const { user } = useAuth();
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedAssignment, setSelectedAssignment] = useState(null);
  const [showSubmissionModal, setShowSubmissionModal] = useState(false);
  const [submissionFile, setSubmissionFile] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (user?.id) {
      fetchAssignments();
    }
  }, [user]);

  const fetchAssignments = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/assignments/student/${user.id}`, {
        headers: {
          'Authorization': `Bearer ${user.accessToken}`
        }
      });
      
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

  const handleSubmitAssignment = async () => {
    if (!submissionFile || !selectedAssignment) return;

    try {
      setSubmitting(true);
      
      const formData = new FormData();
      formData.append('assignment_id', selectedAssignment.id);
      formData.append('student_id', user.id);
      formData.append('file', submissionFile);

      const response = await fetch('http://localhost:8000/api/assignments/submit', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${user.accessToken}`
        },
        body: formData
      });

      if (response.ok) {
        toast.success('Assignment submitted successfully!');
        setShowSubmissionModal(false);
        setSubmissionFile(null);
        setSelectedAssignment(null);
        fetchAssignments(); // Refresh assignments
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to submit assignment');
      }
    } catch (error) {
      console.error('Error submitting assignment:', error);
      toast.error(error.message || 'Failed to submit assignment');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDownloadAssignment = async (assignmentId) => {
    try {
      // Use backend download API directly
      const response = await fetch(`http://localhost:8000/api/files/download/assignment/${assignmentId}`, {
        headers: {
          'Authorization': `Bearer ${user.accessToken}`
        }
      });
      
      if (response.ok) {
        // Get filename from response headers
        const contentDisposition = response.headers.get('content-disposition');
        let filename = 'assignment.pdf';
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
        throw new Error('Failed to download assignment');
      }
    } catch (error) {
      console.error('Error downloading assignment:', error);
      toast.error('Failed to download assignment file');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'submitted': return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'reviewed': return 'bg-green-100 text-green-700 border-green-200';
      case 'late': return 'bg-orange-100 text-orange-700 border-orange-200';
      case 'not_submitted': return 'bg-gray-100 text-gray-700 border-gray-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'submitted': return <Clock className="w-4 h-4" />;
      case 'reviewed': return <CheckCircle className="w-4 h-4" />;
      case 'late': return <AlertTriangle className="w-4 h-4" />;
      case 'not_submitted': return <FileText className="w-4 h-4" />;
      default: return <FileText className="w-4 h-4" />;
    }
  };

  const isOverdue = (dueDate) => {
    return new Date() > new Date(dueDate);
  };

  const getTimeRemaining = (dueDate) => {
    const now = new Date();
    const due = new Date(dueDate);
    const diff = due - now;

    if (diff <= 0) return 'Overdue';

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));

    if (days > 0) return `${days} day${days > 1 ? 's' : ''} left`;
    if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} left`;
    return 'Due soon';
  };

  const filteredAssignments = assignments.filter(assignment => {
    const matchesSearch = assignment.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         assignment.course_title?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || assignment.submission_status === statusFilter;
    return matchesSearch && matchesStatus;
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

  return (
    <DashboardLayout>
      <div className="min-h-screen student-page-bg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-8">
            <div className="mb-4 lg:mb-0">
              <h1 className="text-heading-xl font-bold mb-2 font-serif" style={{color: '#000000'}}>
                My Assignments
              </h1>
              <p className="text-body-lg" style={{color: '#000000'}}>
                View and submit assignments for your enrolled courses. {filteredAssignments.length} assignment{filteredAssignments.length !== 1 ? 's' : ''} found.
              </p>
            </div>
            
            <button
              onClick={fetchAssignments}
              disabled={loading}
              className="btn-primary px-4 py-3 rounded-lg transition-all duration-300 flex items-center space-x-2 font-medium"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>

          {/* Search and Filters */}
          <div className="student-card-bg rounded-lg shadow-elegant p-6 mb-8 border border-border-primary">
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

              {/* Status Filter */}
              <div className="flex items-center space-x-4">
                <label className="text-sm font-medium" style={{color: '#000000'}}>Filter by status:</label>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-400 focus:border-transparent"
                  style={{color: '#000000', backgroundColor: '#ffffff'}}
                >
                  <option value="all">All Assignments</option>
                  <option value="not_submitted">Not Submitted</option>
                  <option value="submitted">Submitted</option>
                  <option value="reviewed">Reviewed</option>
                  <option value="late">Late Submissions</option>
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
                {searchTerm || statusFilter !== 'all' ? 'No assignments found' : 'No assignments available'}
              </h3>
              <p className="text-body-lg mb-6" style={{color: '#000000'}}>
                {searchTerm || statusFilter !== 'all'
                  ? 'Try adjusting your search or filter criteria'
                  : 'Check back later for new assignments from your teachers'
                }
              </p>
            </motion.div>
          ) : (
            <div className="grid gap-6">
              {filteredAssignments.map((assignment, index) => (
                <motion.div
                  key={assignment.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="course-card rounded-xl p-6 transition-all duration-300"
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
                        
                        {/* Status Badge */}
                        <div className={`flex items-center space-x-1 px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(assignment.submission_status)}`}>
                          {getStatusIcon(assignment.submission_status)}
                          <span className="capitalize">
                            {assignment.submission_status?.replace('_', ' ') || 'Not Submitted'}
                          </span>
                        </div>
                      </div>

                      {/* Description */}
                      {assignment.description && (
                        <p className="text-sm mb-3 line-clamp-2" style={{color: '#000000'}}>
                          {assignment.description}
                        </p>
                      )}

                      {/* Due Date and Time Remaining */}
                      <div className="flex items-center space-x-4 text-sm">
                        <div className="flex items-center space-x-1" style={{color: '#000000'}}>
                          <Calendar className="w-4 h-4" />
                          <span>Due: {formatDate(assignment.due_date)}</span>
                        </div>
                        <div className={`flex items-center space-x-1 ${isOverdue(assignment.due_date) ? 'text-red-600' : 'text-orange-600'}`}>
                          <Timer className="w-4 h-4" />
                          <span className="font-medium">{getTimeRemaining(assignment.due_date)}</span>
                        </div>
                        {assignment.submission_score !== undefined && (
                          <div className="flex items-center space-x-1 text-green-600">
                            <CheckCircle className="w-4 h-4" />
                            <span className="font-medium">Score: {assignment.submission_score}/{assignment.max_score}</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex items-center space-x-3">
                      {assignment.file_url && (
                        <button
                          onClick={() => handleDownloadAssignment(assignment.id)}
                          className="flex items-center space-x-2 px-4 py-2 text-blue-600 hover:text-blue-800 border border-blue-200 rounded-lg hover:bg-blue-50 transition-colors"
                        >
                          <Download className="w-4 h-4" />
                          <span>Download</span>
                        </button>
                      )}
                      
                      {assignment.submission_status === 'not_submitted' && !isOverdue(assignment.due_date) && (
                        <button
                          onClick={() => {
                            setSelectedAssignment(assignment);
                            setShowSubmissionModal(true);
                          }}
                          className="btn-primary px-4 py-2 rounded-lg flex items-center space-x-2"
                        >
                          <Upload className="w-4 h-4" />
                          <span>Submit</span>
                        </button>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Submission Modal */}
      <AnimatePresence>
        {showSubmissionModal && selectedAssignment && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowSubmissionModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold" style={{color: '#000000'}}>
                  Submit Assignment
                </h3>
                <button
                  onClick={() => setShowSubmissionModal(false)}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="mb-4">
                <h4 className="font-medium mb-2" style={{color: '#000000'}}>
                  {selectedAssignment.title}
                </h4>
                <p className="text-sm" style={{color: '#000000'}}>
                  Course: {selectedAssignment.course_title}
                </p>
                <p className="text-sm" style={{color: '#000000'}}>
                  Due: {formatDate(selectedAssignment.due_date)}
                </p>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium mb-2" style={{color: '#000000'}}>
                  Upload File (PDF or DOCX, max 10MB)
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                  <input
                    type="file"
                    accept=".pdf,.docx,.doc"
                    onChange={(e) => setSubmissionFile(e.target.files[0])}
                    className="hidden"
                    id="submission-file"
                  />
                  <label
                    htmlFor="submission-file"
                    className="cursor-pointer flex flex-col items-center space-y-2"
                  >
                    <Upload className="w-8 h-8 text-gray-400" />
                    <span className="text-sm" style={{color: '#000000'}}>
                      {submissionFile ? submissionFile.name : 'Click to upload file'}
                    </span>
                  </label>
                </div>
              </div>

              <div className="flex items-center justify-end space-x-3">
                <button
                  onClick={() => setShowSubmissionModal(false)}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSubmitAssignment}
                  disabled={!submissionFile || submitting}
                  className="btn-primary px-6 py-2 rounded-lg flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {submitting ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>Submitting...</span>
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4" />
                      <span>Submit Assignment</span>
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </DashboardLayout>
  );
};

export default StudentAssignments;
