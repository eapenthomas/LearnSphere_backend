import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import AdminDashboardLayout from '../../layouts/AdminDashboardLayout';
import {
  Activity,
  Download,
  Filter,
  Search,
  Calendar,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  FileText,
  Mail,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  UserCheck,
  GraduationCap,
  BookOpen,
  Users,
  Eye,
  EyeOff
} from 'lucide-react';

const ActivityLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 50,
    total: 0,
    pages: 0
  });
  const [filters, setFilters] = useState({
    search: '',
    start_date: '',
    end_date: '',
    action_type: '',
    status: ''
  });
  const [showFilters, setShowFilters] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);

  useEffect(() => {
    fetchActivityLogs();
  }, [pagination.page, filters]);

  const fetchActivityLogs = async () => {
    try {
      setLoading(true);
      
      const params = new URLSearchParams({
        page: pagination.page.toString(),
        limit: pagination.limit.toString()
      });

      if (filters.start_date) params.append('start_date', filters.start_date);
      if (filters.end_date) params.append('end_date', filters.end_date);
      if (filters.action_type) params.append('action_type', filters.action_type);

      const response = await fetch(`http://localhost:8000/api/admin/dashboard/activity-logs?${params}`);
      
      if (response.ok) {
        const result = await response.json();
        setLogs(result.data || []);
        setPagination(prev => ({
          ...prev,
          ...result.pagination
        }));
      } else {
        toast.error('Failed to fetch activity logs');
      }
    } catch (error) {
      console.error('Error fetching activity logs:', error);
      toast.error('Failed to fetch activity logs');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
    setPagination(prev => ({ ...prev, page: 1 })); // Reset to first page
  };

  const clearFilters = () => {
    setFilters({
      search: '',
      start_date: '',
      end_date: '',
      action_type: '',
      status: ''
    });
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  const exportLogs = async (format) => {
    try {
      setExportLoading(true);
      
      const params = new URLSearchParams({
        format: format
      });

      if (filters.start_date) params.append('start_date', filters.start_date);
      if (filters.end_date) params.append('end_date', filters.end_date);
      if (filters.action_type) params.append('action_type', filters.action_type);

      const response = await fetch(`http://localhost:8000/api/admin/dashboard/activity-logs/export?${params}`);
      
      if (response.ok) {
        const result = await response.json();
        
        // Create and download file
        const blob = new Blob([result.data], { type: result.content_type });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = result.filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        toast.success(`Activity logs exported as ${format.toUpperCase()}`);
      } else {
        toast.error('Failed to export activity logs');
      }
    } catch (error) {
      console.error('Error exporting activity logs:', error);
      toast.error('Failed to export activity logs');
    } finally {
      setExportLoading(false);
    }
  };

  const getActivityIcon = (notificationType) => {
    switch (notificationType) {
      case 'teacher_verification_success_teacher':
      case 'teacher_verification_success':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'teacher_verification_failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'teacher_manual_review_teacher':
      case 'teacher_manual_review':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'teacher_approved':
        return <UserCheck className="w-4 h-4 text-blue-500" />;
      case 'teacher_rejected':
        return <AlertTriangle className="w-4 h-4 text-orange-500" />;
      case 'course_created':
        return <BookOpen className="w-4 h-4 text-purple-500" />;
      case 'enrollment_created':
        return <Users className="w-4 h-4 text-indigo-500" />;
      case 'user_registration':
        return <GraduationCap className="w-4 h-4 text-cyan-500" />;
      default:
        return <Activity className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'sent':
        return <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">Sent</span>;
      case 'failed':
        return <span className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full">Failed</span>;
      case 'pending':
        return <span className="px-2 py-1 bg-yellow-100 text-yellow-700 text-xs rounded-full">Pending</span>;
      default:
        return <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">Unknown</span>;
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    
    try {
      const date = new Date(dateString);
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (error) {
      return 'Invalid Date';
    }
  };

  const filteredLogs = logs.filter(log => {
    if (filters.search) {
      const searchTerm = filters.search.toLowerCase();
      return (
        log.description.toLowerCase().includes(searchTerm) ||
        log.recipient_email.toLowerCase().includes(searchTerm) ||
        log.event_type.toLowerCase().includes(searchTerm)
      );
    }
    return true;
  });

  return (
    <AdminDashboardLayout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 p-6"
        >
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
            <div className="flex items-center space-x-4 mb-4 lg:mb-0">
              <div className="p-3 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl">
                <FileText className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-extrabold text-gray-800 tracking-tight">Activity Logs</h1>
                <p className="text-lg text-gray-600 font-medium">
                  Monitor all system activities and user actions
                </p>
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="bg-gradient-to-r from-gray-500 to-gray-600 text-white font-semibold rounded-xl shadow-md hover:shadow-lg px-6 py-3 transition-all duration-300 hover:scale-105 flex items-center space-x-2"
              >
                <Filter className="w-5 h-5" />
                <span>Filters</span>
              </button>

              <button
                onClick={fetchActivityLogs}
                disabled={loading}
                className="bg-gradient-to-r from-blue-500 to-indigo-500 text-white font-semibold rounded-xl shadow-md hover:shadow-lg px-6 py-3 transition-all duration-300 hover:scale-105 flex items-center space-x-2 disabled:opacity-50"
              >
                <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>

              <div className="relative">
                <button
                  onClick={() => exportLogs('csv')}
                  disabled={exportLoading}
                  className="bg-gradient-to-r from-green-500 to-emerald-500 text-white font-semibold rounded-xl shadow-md hover:shadow-lg px-6 py-3 transition-all duration-300 hover:scale-105 flex items-center space-x-2 disabled:opacity-50"
                >
                  <Download className="w-5 h-5" />
                  <span>Export CSV</span>
                </button>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Filters */}
        {showFilters && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-white rounded-2xl shadow-lg p-6"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    value={filters.search}
                    onChange={(e) => handleFilterChange('search', e.target.value)}
                    placeholder="Search logs..."
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Start Date</label>
                <input
                  type="date"
                  value={filters.start_date}
                  onChange={(e) => handleFilterChange('start_date', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">End Date</label>
                <input
                  type="date"
                  value={filters.end_date}
                  onChange={(e) => handleFilterChange('end_date', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Action Type</label>
                <select
                  value={filters.action_type}
                  onChange={(e) => handleFilterChange('action_type', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Actions</option>
                  <option value="teacher_verification_success_teacher">Teacher Approved</option>
                  <option value="teacher_verification_failed">Teacher Verification Failed</option>
                  <option value="teacher_manual_review_teacher">Manual Review</option>
                  <option value="course_created">Course Created</option>
                  <option value="user_registration">User Registration</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end mt-4">
              <button
                onClick={clearFilters}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Clear Filters
              </button>
            </div>
          </motion.div>
        )}

        {/* Activity Logs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300"
        >
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-800">Activity Logs</h2>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-600">
                  Showing {filteredLogs.length} of {pagination.total} logs
                </span>
              </div>
            </div>
          </div>

          <div className="overflow-x-auto">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <RefreshCw className="w-8 h-8 text-blue-500 animate-spin" />
                <span className="ml-3 text-gray-600">Loading activity logs...</span>
              </div>
            ) : filteredLogs.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12">
                <Activity className="w-16 h-16 text-gray-300 mb-4" />
                <h3 className="text-lg font-semibold text-gray-600 mb-2">No Activity Logs Found</h3>
                <p className="text-gray-500 text-center">
                  {filters.search || filters.start_date || filters.end_date || filters.action_type
                    ? 'Try adjusting your filters to see more results.'
                    : 'No activity logs have been recorded yet.'}
                </p>
              </div>
            ) : (
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Activity
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Recipient
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Timestamp
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredLogs.map((log) => (
                    <motion.tr
                      key={log.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="hover:bg-gray-50 transition-colors"
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center space-x-3">
                          {getActivityIcon(log.event_type)}
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {log.description}
                            </div>
                            <div className="text-sm text-gray-500">
                              {log.event_type}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center space-x-2">
                          <Mail className="w-4 h-4 text-gray-400" />
                          <span className="text-sm text-gray-900">{log.recipient_email}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(log.status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(log.timestamp)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button
                          onClick={() => console.log('View details:', log)}
                          className="text-blue-600 hover:text-blue-900 transition-colors"
                        >
                          View Details
                        </button>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* Pagination */}
          {pagination.pages > 1 && (
            <div className="px-6 py-4 border-t border-gray-200">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-700">
                  Showing page {pagination.page} of {pagination.pages}
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
                    disabled={pagination.page === 1}
                    className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  <span className="px-4 py-2 text-sm font-medium text-gray-700">
                    {pagination.page}
                  </span>
                  <button
                    onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
                    disabled={pagination.page === pagination.pages}
                    className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </AdminDashboardLayout>
  );
};

export default ActivityLogs;