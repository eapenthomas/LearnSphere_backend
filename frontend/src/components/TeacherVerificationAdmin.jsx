import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext.jsx';
import {
  CheckCircle,
  XCircle,
  Eye,
  FileText,
  User,
  Mail,
  Building,
  Clock,
  AlertTriangle,
  RefreshCw,
  Filter,
  Search
} from 'lucide-react';

const TeacherVerificationAdmin = () => {
  const { user } = useAuth();
  const [pendingRequests, setPendingRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);

  useEffect(() => {
    fetchPendingRequests();
  }, []);

  const fetchPendingRequests = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('learnsphere_access_token') || localStorage.getItem('learnsphere_token');
      
      if (!token) {
        toast.error('Authentication required');
        return;
      }

      const response = await fetch('http://localhost:8000/api/teacher-verification/admin/pending-requests', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setPendingRequests(data);
      } else if (response.status === 401) {
        toast.error('Authentication failed. Please login again.');
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Failed to fetch requests');
      }
    } catch (error) {
      console.error('Error fetching requests:', error);
      toast.error('Failed to fetch verification requests');
    } finally {
      setLoading(false);
    }
  };

  const handleApproval = async (userId, status, reason = '') => {
    try {
      setProcessing(userId);
      const token = localStorage.getItem('learnsphere_access_token') || localStorage.getItem('learnsphere_token');
      
      const response = await fetch('http://localhost:8000/api/teacher-verification/approve-reject', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          status: status,
          reason: reason || (status === 'approved' ? 'ID verification successful' : 'ID verification failed')
        }),
      });

      const result = await response.json();

      if (response.ok) {
        toast.success(`Teacher ${status} successfully`);
        fetchPendingRequests(); // Refresh the list
      } else {
        toast.error(result.detail || `Failed to ${status} teacher`);
      }
    } catch (error) {
      console.error('Error processing request:', error);
      toast.error(`Failed to ${status} teacher`);
    } finally {
      setProcessing(null);
    }
  };

  const openDetailsModal = (request) => {
    setSelectedRequest(request);
    setShowDetailsModal(true);
  };

  const closeDetailsModal = () => {
    setSelectedRequest(null);
    setShowDetailsModal(false);
  };

  const filteredRequests = pendingRequests.filter(request => {
    const matchesSearch = request.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         request.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         request.institution_name?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || 
                         (statusFilter === 'passed' && request.ocr_status === 'passed') ||
                         (statusFilter === 'failed' && request.ocr_status === 'failed') ||
                         (statusFilter === 'pending' && request.approval_status === 'pending');
    
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'passed': return 'text-green-600 bg-green-100';
      case 'failed': return 'text-red-600 bg-red-100';
      case 'pending': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return 'text-green-600';
    if (confidence >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading verification requests...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Teacher Verification</h1>
              <p className="text-gray-600 mt-1">Review and approve teacher registration requests</p>
            </div>
            <button
              onClick={fetchPendingRequests}
              disabled={loading}
              className="flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search by name, email, or institution..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Filter className="w-5 h-5 text-gray-400" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Status</option>
                <option value="passed">OCR Passed</option>
                <option value="failed">OCR Failed</option>
                <option value="pending">Pending Approval</option>
              </select>
            </div>
          </div>
        </div>

        {/* Requests List */}
        <div className="space-y-4">
          <AnimatePresence>
            {filteredRequests.length === 0 ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="bg-white rounded-lg shadow-sm p-12 text-center"
              >
                <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No verification requests</h3>
                <p className="text-gray-600">No teacher verification requests found matching your criteria.</p>
              </motion.div>
            ) : (
              filteredRequests.map((request) => (
                <motion.div
                  key={request.user_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow"
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center gap-4 mb-4">
                        <div className="flex items-center gap-2">
                          <User className="w-5 h-5 text-gray-400" />
                          <h3 className="text-lg font-semibold text-gray-900">{request.full_name}</h3>
                        </div>
                        <div className="flex gap-2">
                          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(request.ocr_status)}`}>
                            OCR: {request.ocr_status}
                          </span>
                          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(request.approval_status)}`}>
                            Status: {request.approval_status}
                          </span>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div className="flex items-center gap-2">
                          <Mail className="w-4 h-4 text-gray-400" />
                          <span className="text-gray-600">{request.email}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Building className="w-4 h-4 text-gray-400" />
                          <span className="text-gray-600">{request.institution_name}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Clock className="w-4 h-4 text-gray-400" />
                          <span className="text-gray-600">
                            Submitted: {new Date(request.created_at).toLocaleDateString()}
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <AlertTriangle className="w-4 h-4 text-gray-400" />
                          <span className={`font-medium ${getConfidenceColor(request.ai_confidence)}`}>
                            AI Confidence: {request.ai_confidence}%
                          </span>
                        </div>
                      </div>

                      {request.ai_reason && (
                        <div className="bg-gray-50 rounded-lg p-3 mb-4">
                          <p className="text-sm text-gray-700">
                            <strong>AI Analysis:</strong> {request.ai_reason}
                          </p>
                        </div>
                      )}
                    </div>
                    
                    <div className="flex flex-col gap-2 ml-6">
                      <button
                        onClick={() => openDetailsModal(request)}
                        className="flex items-center gap-2 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                      >
                        <Eye className="w-4 h-4" />
                        View Details
                      </button>
                      
                      {request.ocr_status === 'passed' && request.approval_status === 'pending' && (
                        <>
                          <button
                            onClick={() => handleApproval(request.user_id, 'approved')}
                            disabled={processing === request.user_id}
                            className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50 transition-colors"
                          >
                            {processing === request.user_id ? (
                              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                            ) : (
                              <CheckCircle className="w-4 h-4" />
                            )}
                            Approve
                          </button>
                          
                          <button
                            onClick={() => handleApproval(request.user_id, 'rejected', 'ID verification requirements not met')}
                            disabled={processing === request.user_id}
                            className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50 transition-colors"
                          >
                            {processing === request.user_id ? (
                              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                            ) : (
                              <XCircle className="w-4 h-4" />
                            )}
                            Reject
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Details Modal */}
      <AnimatePresence>
        {showDetailsModal && selectedRequest && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
            onClick={closeDetailsModal}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-bold text-gray-900">Verification Details</h2>
                  <button
                    onClick={closeDetailsModal}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <XCircle className="w-6 h-6" />
                  </button>
                </div>

                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">Teacher Information</h3>
                    <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                      <p><strong>Name:</strong> {selectedRequest.full_name}</p>
                      <p><strong>Email:</strong> {selectedRequest.email}</p>
                      <p><strong>Institution:</strong> {selectedRequest.institution_name}</p>
                      <p><strong>Submitted:</strong> {new Date(selectedRequest.created_at).toLocaleString()}</p>
                    </div>
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">Verification Results</h3>
                    <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                      <p><strong>OCR Status:</strong> 
                        <span className={`ml-2 px-2 py-1 rounded text-sm ${getStatusColor(selectedRequest.ocr_status)}`}>
                          {selectedRequest.ocr_status}
                        </span>
                      </p>
                      <p><strong>AI Confidence:</strong> 
                        <span className={`ml-2 font-medium ${getConfidenceColor(selectedRequest.ai_confidence)}`}>
                          {selectedRequest.ai_confidence}%
                        </span>
                      </p>
                      <p><strong>Approval Status:</strong> 
                        <span className={`ml-2 px-2 py-1 rounded text-sm ${getStatusColor(selectedRequest.approval_status)}`}>
                          {selectedRequest.approval_status}
                        </span>
                      </p>
                      {selectedRequest.ai_reason && (
                        <div>
                          <p><strong>AI Analysis:</strong></p>
                          <p className="mt-1 text-sm text-gray-700 bg-white p-2 rounded border">
                            {selectedRequest.ai_reason}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">ID Card</h3>
                    <div className="text-center">
                      <a
                        href={selectedRequest.id_card_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                      >
                        <Eye className="w-4 h-4" />
                        View ID Card
                      </a>
                    </div>
                  </div>

                  {selectedRequest.ocr_text && (
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-2">Extracted Text</h3>
                      <div className="bg-gray-50 rounded-lg p-4">
                        <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                          {selectedRequest.ocr_text}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default TeacherVerificationAdmin;

