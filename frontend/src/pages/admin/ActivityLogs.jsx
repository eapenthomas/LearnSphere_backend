import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext.jsx';
import AdminDashboardLayout from '../../layouts/AdminDashboardLayout.jsx';
import { adminOperations } from '../../utils/supabaseClient.js';
import { toast } from 'react-hot-toast';
import {
  Activity,
  Search,
  Filter,
  Calendar,
  User,
  CheckCircle,
  XCircle,
  UserCheck,
  UserX,
  AlertTriangle,
  Clock,
  Loader,
  Download,
  Eye
} from 'lucide-react';

const ActivityLogs = () => {
  const { user } = useAuth();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [actionFilter, setActionFilter] = useState('all');
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    fetchActivityLogs();
  }, []);

  const fetchActivityLogs = async () => {
    try {
      setLoading(true);
      const activityLogs = await adminOperations.getUserActivityLogs(100);
      setLogs(activityLogs);
    } catch (error) {
      console.error('Error fetching activity logs:', error);
      toast.error('Failed to load activity logs');
    } finally {
      setLoading(false);
    }
  };

  const handleExportLogs = async () => {
    try {
      setExporting(true);

      // Create download link for PDF export
      const exportUrl = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/export-activity-logs?days=30&format=pdf`;

      // Create a temporary link and trigger download
      const link = document.createElement('a');
      link.href = exportUrl;
      link.download = `learnsphere_activity_report_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      toast.success('Activity logs exported successfully');
    } catch (error) {
      console.error('Error exporting activity logs:', error);
    } finally {
      setExporting(false);
    }
  };

  const filteredLogs = logs.filter(log => {
    const matchesSearch = 
      log.profiles?.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.profiles?.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.action?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesAction = actionFilter === 'all' || log.action === actionFilter;
    
    return matchesSearch && matchesAction;
  });

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const getActionIcon = (action) => {
    switch (action) {
      case 'user_enabled':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'user_disabled':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'teacher_approved':
        return <UserCheck className="w-5 h-5 text-blue-500" />;
      case 'teacher_rejected':
        return <UserX className="w-5 h-5 text-yellow-500" />;
      default:
        return <Activity className="w-5 h-5 text-gray-500" />;
    }
  };

  const getActionColor = (action) => {
    switch (action) {
      case 'user_enabled':
      case 'teacher_approved':
        return 'bg-green-50 text-green-700 border-green-200';
      case 'user_disabled':
      case 'teacher_rejected':
        return 'bg-red-50 text-red-700 border-red-200';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200';
    }
  };

  const getActionText = (action) => {
    return action.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  const LogCard = ({ log }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl shadow-lg p-6 hover:shadow-xl transition-all duration-300 border border-gray-100"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-4">
          <div className="flex-shrink-0">
            {getActionIcon(log.action)}
          </div>
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-2">
              <h3 className="text-lg font-semibold text-gray-800">
                {log.profiles?.full_name || 'Unknown User'}
              </h3>
              <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getActionColor(log.action)}`}>
                {getActionText(log.action)}
              </span>
            </div>
            <p className="text-sm text-gray-600 flex items-center space-x-2">
              <User className="w-4 h-4" />
              <span>{log.profiles?.email}</span>
              <span>•</span>
              <span className="capitalize">{log.profiles?.role}</span>
            </p>
          </div>
        </div>
        
        <div className="text-right">
          <p className="text-sm text-gray-500 flex items-center space-x-1">
            <Clock className="w-4 h-4" />
            <span>{formatDate(log.created_at)}</span>
          </p>
          {log.admin && (
            <p className="text-xs text-gray-400 mt-1">
              by {log.admin.full_name}
            </p>
          )}
        </div>
      </div>

      {log.details && (
        <div className="bg-gray-50 rounded-xl p-4 mt-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Details:</h4>
          <pre className="text-xs text-gray-600 whitespace-pre-wrap">
            {JSON.stringify(log.details, null, 2)}
          </pre>
        </div>
      )}
    </motion.div>
  );

  const uniqueActions = [...new Set(logs.map(log => log.action))];

  return (
    <AdminDashboardLayout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Activity Logs</h1>
            <p className="text-gray-600">
              Monitor system activities and user actions. {filteredLogs.length} log{filteredLogs.length !== 1 ? 's' : ''} found.
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={fetchActivityLogs}
              disabled={loading}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50 transition-all duration-200 flex items-center space-x-2"
            >
              <Loader className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
            
            <button
              onClick={handleExportLogs}
              disabled={exporting}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Download className={`w-4 h-4 ${exporting ? 'animate-pulse' : ''}`} />
              <span>{exporting ? 'Exporting...' : 'Export PDF'}</span>
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by user, email, or action..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-red-400 focus:border-transparent transition-all duration-200 text-gray-900 placeholder-gray-500"
              />
            </div>

            {/* Action Filter */}
            <select
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              className="px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-red-400 focus:border-transparent transition-all duration-200 text-gray-900"
            >
              <option value="all">All Actions</option>
              {uniqueActions.map(action => (
                <option key={action} value={action}>
                  {getActionText(action)}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader className="w-8 h-8 text-red-500 animate-spin" />
            <span className="ml-3 text-gray-600">Loading activity logs...</span>
          </div>
        ) : filteredLogs.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-12"
          >
            <Activity className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-600 mb-2">
              {searchTerm || actionFilter !== 'all' ? 'No logs found' : 'No activity logs yet'}
            </h3>
            <p className="text-gray-500">
              {searchTerm || actionFilter !== 'all' 
                ? 'Try adjusting your search or filter criteria'
                : 'User activities will appear here'
              }
            </p>
          </motion.div>
        ) : (
          <div className="space-y-4">
            {filteredLogs.map((log, index) => (
              <motion.div
                key={log.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <LogCard log={log} />
              </motion.div>
            ))}
          </div>
        )}

        {/* Summary Stats */}
        {!loading && logs.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl shadow-lg p-6"
          >
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Activity Summary</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {uniqueActions.map(action => {
                const count = logs.filter(log => log.action === action).length;
                return (
                  <div key={action} className="text-center">
                    <div className="flex items-center justify-center mb-2">
                      {getActionIcon(action)}
                    </div>
                    <p className="text-2xl font-bold text-gray-800">{count}</p>
                    <p className="text-sm text-gray-600">{getActionText(action)}</p>
                  </div>
                );
              })}
            </div>
          </motion.div>
        )}
      </div>
    </AdminDashboardLayout>
  );
};

export default ActivityLogs;
