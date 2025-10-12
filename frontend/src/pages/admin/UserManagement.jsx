import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext.jsx';
import AdminDashboardLayout from '../../layouts/AdminDashboardLayout.jsx';
import { adminOperations } from '../../utils/supabaseClient.js';
import { toast } from 'react-hot-toast';
import { useSearchParams } from 'react-router-dom';
import {
  Users,
  Search,
  Filter,
  MoreVertical,
  UserCheck,
  UserX,
  Mail,
  Calendar,
  Shield,
  GraduationCap,
  BookOpen,
  Loader,
  Eye,
  Settings,
  AlertTriangle,
  CheckCircle,
  XCircle,
  User,
  Crown,
  ToggleLeft,
  ToggleRight,
  X,
  Phone,
  Award,
  Activity,
  MapPin,
  Clock
} from 'lucide-react';

const UserManagement = () => {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showActionModal, setShowActionModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [actionType, setActionType] = useState('');
  const [processing, setProcessing] = useState(false);
  const [showUserModal, setShowUserModal] = useState(false);
  const [viewingUser, setViewingUser] = useState(null);

  useEffect(() => {
    // Read URL parameters and set initial filter
    const filterParam = searchParams.get('filter');
    if (filterParam && ['students', 'teachers', 'admins'].includes(filterParam)) {
      setRoleFilter(filterParam);
    }

    fetchUsers();

    // Set up real-time subscription for user updates
    const subscription = adminOperations.subscribeToAdminUpdates((payload) => {
      console.log('Real-time user update:', payload);
      if (payload.table === 'profiles') {
        // Update the specific user in the list
        if (payload.eventType === 'UPDATE') {
          setUsers(prev => prev.map(u =>
            u.id === payload.new.id ? { ...u, ...payload.new } : u
          ));
        } else if (payload.eventType === 'INSERT') {
          // New user added, refresh the list
          fetchUsers();
        } else if (payload.eventType === 'DELETE') {
          // User deleted, remove from list
          setUsers(prev => prev.filter(u => u.id !== payload.old.id));
        }
      }
    });

    // Cleanup subscription on unmount
    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const allUsers = await adminOperations.getAllUsers();
      setUsers(allUsers);
    } catch (error) {
      console.error('Error fetching users:', error);
      toast.error('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleUserStatus = async (userId, currentStatus) => {
    const newStatus = !currentStatus;
    const action = newStatus ? 'enable' : 'disable';
    
    try {
      setProcessing(true);
      await adminOperations.toggleUserStatus(userId, newStatus, user.id);
      
      // Update local state
      setUsers(prev => prev.map(u => 
        u.id === userId ? { ...u, is_active: newStatus } : u
      ));
      
      setShowActionModal(false);
      setSelectedUser(null);
      toast.success(`User ${action}d successfully!`);
    } catch (error) {
      console.error(`Error ${action}ing user:`, error);
      toast.error(`Failed to ${action} user`);
    } finally {
      setProcessing(false);
    }
  };

  const openActionModal = (user, action) => {
    setSelectedUser(user);
    setActionType(action);
    setShowActionModal(true);
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = 
      user.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesRole = roleFilter === 'all' || user.role === roleFilter;
    const matchesStatus = statusFilter === 'all' || 
      (statusFilter === 'active' && user.is_active) ||
      (statusFilter === 'inactive' && !user.is_active);
    
    return matchesSearch && matchesRole && matchesStatus;
  });

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getRoleIcon = (role) => {
    switch (role) {
      case 'admin':
        return <Shield className="w-4 h-4 text-red-500" />;
      case 'teacher':
        return <GraduationCap className="w-4 h-4 text-blue-500" />;
      case 'student':
        return <BookOpen className="w-4 h-4 text-green-500" />;
      default:
        return <Users className="w-4 h-4 text-gray-500" />;
    }
  };

  const getRoleBadge = (role) => {
    const colors = {
      admin: 'bg-red-100 text-red-700',
      teacher: 'bg-blue-100 text-blue-700',
      student: 'bg-green-100 text-green-700'
    };

    return `px-3 py-1.5 rounded-full text-xs font-semibold ${colors[role] || 'bg-gray-100 text-gray-700'}`;
  };

  const getStatusBadge = (isActive, approvalStatus) => {
    if (!isActive) {
      return 'px-3 py-1.5 rounded-full text-xs font-semibold bg-red-100 text-red-700';
    }
    if (approvalStatus === 'pending') {
      return 'px-3 py-1.5 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-700';
    }
    return 'px-3 py-1.5 rounded-full text-xs font-semibold bg-green-100 text-green-700';
  };

  const getStatusText = (isActive, approvalStatus) => {
    if (!isActive) return 'Disabled';
    if (approvalStatus === 'pending') return 'Pending';
    return 'Active';
  };

  const UserCard = ({ user }) => (
    <div className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 border border-gray-100 group">
      <div className="flex items-start justify-between mb-6 gap-4">
        <div className="flex items-center space-x-4 flex-1 min-w-0">
          <div className="w-14 h-14 bg-gradient-to-r from-indigo-500 to-blue-500 rounded-full flex items-center justify-center shadow-lg flex-shrink-0">
            {getRoleIcon(user.role)}
          </div>
          <div className="min-w-0 flex-1">
            <h3 className="text-xl font-bold text-gray-800 mb-1 truncate">
              {user.full_name}
            </h3>
            <p className="text-sm text-gray-600 flex items-center space-x-2 truncate">
              <Mail className="w-4 h-4 flex-shrink-0" />
              <span className="truncate">{user.email}</span>
            </p>
          </div>
        </div>

        <div className="flex flex-col items-end space-y-3 min-w-0 flex-shrink-0">
          <span className={`${getRoleBadge(user.role)} whitespace-nowrap`}>
            {user.role}
          </span>
          <span className={`${getStatusBadge(user.is_active, user.approval_status)} whitespace-nowrap`}>
            {user.is_active ? (
              <div className="flex items-center space-x-1">
                <ToggleRight className="w-3 h-3 flex-shrink-0" />
                <span>{getStatusText(user.is_active, user.approval_status)}</span>
              </div>
            ) : (
              <div className="flex items-center space-x-1">
                <ToggleLeft className="w-3 h-3 flex-shrink-0" />
                <span>{getStatusText(user.is_active, user.approval_status)}</span>
              </div>
            )}
          </span>
        </div>
      </div>

      <div className="space-y-3 mb-6 bg-gray-50 rounded-lg p-4">
        <div className="flex items-center space-x-3 text-sm text-gray-700">
          <div className="p-1 bg-blue-100 rounded">
            <Calendar className="w-4 h-4 text-blue-600" />
          </div>
          <span className="font-medium">Joined: {formatDate(user.created_at)}</span>
        </div>
        {user.approved_at && (
          <div className="flex items-center space-x-3 text-sm text-gray-700">
            <div className="p-1 bg-green-100 rounded">
              <CheckCircle className="w-4 h-4 text-green-600" />
            </div>
            <span className="font-medium">Approved: {formatDate(user.approved_at)}</span>
          </div>
        )}
      </div>

      <div className="flex items-center space-x-3">
        {user.role !== 'admin' && (
          <>
            {user.is_active ? (
              <button
                onClick={() => openActionModal(user, 'disable')}
                className="flex-1 bg-gradient-to-r from-rose-500 to-red-500 text-white font-semibold rounded-xl shadow-md hover:shadow-lg px-4 py-3 transition-all duration-300 hover:scale-105 flex items-center justify-center space-x-2"
              >
                <UserX className="w-4 h-4" />
                <span>Disable</span>
              </button>
            ) : (
              <button
                onClick={() => openActionModal(user, 'enable')}
                className="flex-1 bg-gradient-to-r from-emerald-500 to-green-500 text-white font-semibold rounded-xl shadow-md hover:shadow-lg px-4 py-3 transition-all duration-300 hover:scale-105 flex items-center justify-center space-x-2"
              >
                <UserCheck className="w-4 h-4" />
                <span>Enable</span>
              </button>
            )}
          </>
        )}

        <button
          onClick={() => {
            setViewingUser(user);
            setShowUserModal(true);
          }}
          className="px-4 py-3 text-gray-600 hover:text-gray-800 border border-gray-300 rounded-xl hover:bg-gray-50 transition-all duration-300 hover:scale-105"
          title="View user details"
        >
          <Eye className="w-4 h-4" />
        </button>
      </div>
    </div>
  );

  return (
    <AdminDashboardLayout>
      <div className="p-6 space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 p-8"
        >
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
            <div>
              <div className="flex items-center space-x-4 mb-4">
                <div className="p-3 bg-gradient-to-r from-indigo-500 to-blue-500 rounded-xl">
                  <Users className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-extrabold text-gray-800 tracking-tight">User Management</h1>
                  <p className="text-lg text-gray-600 font-medium">
                    Manage user accounts and permissions
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-2 bg-blue-50 px-4 py-2 rounded-lg">
                  <Users className="w-5 h-5 text-blue-600" />
                  <span className="font-semibold text-blue-700">
                    {filteredUsers.length} User{filteredUsers.length !== 1 ? 's' : ''} Found
                  </span>
                </div>
                <div className="flex items-center space-x-2 bg-green-50 px-4 py-2 rounded-lg">
                  <UserCheck className="w-5 h-5 text-green-600" />
                  <span className="font-semibold text-green-700">
                    {filteredUsers.filter(u => u.is_active).length} Active
                  </span>
                </div>
                <div className="flex items-center space-x-2 bg-red-50 px-4 py-2 rounded-lg">
                  <UserX className="w-5 h-5 text-red-600" />
                  <span className="font-semibold text-red-700">
                    {filteredUsers.filter(u => !u.is_active).length} Disabled
                  </span>
                </div>
              </div>
            </div>

            <button
              onClick={fetchUsers}
              disabled={loading}
              className="mt-4 lg:mt-0 bg-gradient-to-r from-indigo-500 to-blue-500 text-white font-semibold rounded-xl shadow-md hover:shadow-lg px-6 py-3 transition-all duration-300 hover:scale-105 flex items-center space-x-2 disabled:opacity-50"
            >
              <Loader className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>
        </motion.div>

        {/* Search and Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 p-6"
        >
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative md:col-span-2">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by name or email..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-400 focus:border-transparent transition-all duration-200 text-gray-900 placeholder-gray-500"
              />
            </div>

            {/* Role Filter */}
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <select
                value={roleFilter}
                onChange={(e) => setRoleFilter(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-400 focus:border-transparent transition-all duration-200 text-gray-900 appearance-none bg-white"
              >
                <option value="all">All Roles</option>
                <option value="student">Students</option>
                <option value="teacher">Teachers</option>
                <option value="admin">Admins</option>
              </select>
            </div>

            {/* Status Filter */}
            <div className="relative">
              <Settings className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-400 focus:border-transparent transition-all duration-200 text-gray-900 appearance-none bg-white"
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Disabled</option>
              </select>
            </div>
          </div>

          <div className="mt-4 flex items-center justify-between text-sm text-gray-600">
            <span>
              Showing {filteredUsers.length} of {users.length} users
            </span>
            <div className="flex items-center space-x-4">
              <span className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Active</span>
              </span>
              <span className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                <span>Disabled</span>
              </span>
            </div>
          </div>
        </motion.div>

        {/* Content */}
        {loading ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-white rounded-2xl shadow-lg p-12 text-center"
          >
            <Loader className="w-8 h-8 text-indigo-500 animate-spin mx-auto mb-4" />
            <span className="text-gray-600 font-medium">Loading users...</span>
          </motion.div>
        ) : filteredUsers.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 p-12 text-center"
          >
            <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Users className="w-10 h-10 text-gray-400" />
            </div>
            <h3 className="text-2xl font-bold text-gray-800 mb-3">
              No users found
            </h3>
            <p className="text-gray-600 text-lg">
              Try adjusting your search or filter criteria
            </p>
            <button
              onClick={() => {
                setSearchTerm('');
                setRoleFilter('all');
                setStatusFilter('all');
              }}
              className="mt-4 text-indigo-600 hover:text-indigo-700 font-medium"
            >
              Clear all filters
            </button>
          </motion.div>
        ) : (
          <div className="grid gap-6 grid-cols-1 lg:grid-cols-2 xl:grid-cols-3">
            {filteredUsers.map((user, index) => (
              <motion.div
                key={user.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + index * 0.1 }}
              >
                <UserCard user={user} />
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* Action Confirmation Modal */}
      <AnimatePresence>
        {showActionModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6"
            >
              <div className={`flex items-center justify-center w-12 h-12 rounded-full mx-auto mb-4 ${
                actionType === 'enable' ? 'bg-green-100' : 'bg-red-100'
              }`}>
                {actionType === 'enable' ? (
                  <UserCheck className="w-6 h-6 text-green-600" />
                ) : (
                  <UserX className="w-6 h-6 text-red-600" />
                )}
              </div>
              
              <h3 className="text-lg font-semibold text-gray-800 text-center mb-2">
                {actionType === 'enable' ? 'Enable User' : 'Disable User'}
              </h3>
              
              <p className="text-gray-600 text-center mb-6">
                {actionType === 'enable' 
                  ? `Enable "${selectedUser?.full_name}"? They will be able to access their account and receive an email notification.`
                  : `Disable "${selectedUser?.full_name}"? They will not be able to access their account and will receive an email notification.`
                }
              </p>
              
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => {
                    setShowActionModal(false);
                    setSelectedUser(null);
                  }}
                  className="flex-1 px-4 py-2 text-gray-600 hover:text-gray-800 font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleToggleUserStatus(selectedUser.id, selectedUser.is_active)}
                  disabled={processing}
                  className={`flex-1 px-4 py-2 text-white font-semibold rounded-xl transition-colors flex items-center justify-center space-x-2 ${
                    actionType === 'enable' 
                      ? 'bg-green-600 hover:bg-green-700' 
                      : 'bg-red-600 hover:bg-red-700'
                  }`}
                >
                  {processing ? (
                    <Loader className="w-4 h-4 animate-spin" />
                  ) : actionType === 'enable' ? (
                    <UserCheck className="w-4 h-4" />
                  ) : (
                    <UserX className="w-4 h-4" />
                  )}
                  <span>{actionType === 'enable' ? 'Enable' : 'Disable'}</span>
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* User View Modal */}
      <AnimatePresence>
        {showUserModal && viewingUser && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b border-gray-200">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full flex items-center justify-center">
                    <User className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">User Details</h2>
                    <p className="text-sm text-gray-500">Complete user information</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowUserModal(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-gray-500" />
                </button>
              </div>

              {/* Content */}
              <div className="p-6 space-y-6">
                {/* Basic Information */}
                <div className="bg-gray-50 rounded-xl p-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <User className="w-5 h-5 mr-2 text-indigo-600" />
                    Basic Information
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-500">Full Name</label>
                      <p className="text-gray-900 font-medium">{viewingUser.full_name}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">Email</label>
                      <p className="text-gray-900 font-medium">{viewingUser.email}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">Role</label>
                      <div className="flex items-center space-x-2">
                        {viewingUser.role === 'admin' && <Crown className="w-4 h-4 text-yellow-500" />}
                        {viewingUser.role === 'teacher' && <GraduationCap className="w-4 h-4 text-blue-500" />}
                        {viewingUser.role === 'student' && <BookOpen className="w-4 h-4 text-green-500" />}
                        <span className="capitalize font-medium text-gray-900">{viewingUser.role}</span>
                      </div>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">User ID</label>
                      <p className="text-gray-900 font-mono text-sm">{viewingUser.id}</p>
                    </div>
                  </div>
                </div>

                {/* Account Status */}
                <div className="bg-gray-50 rounded-xl p-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <Activity className="w-5 h-5 mr-2 text-indigo-600" />
                    Account Status
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-500">Status</label>
                      <div className="flex items-center space-x-2">
                        {viewingUser.is_active ? (
                          <CheckCircle className="w-4 h-4 text-green-500" />
                        ) : (
                          <XCircle className="w-4 h-4 text-red-500" />
                        )}
                        <span className={`font-medium ${viewingUser.is_active ? 'text-green-700' : 'text-red-700'}`}>
                          {viewingUser.is_active ? 'Active' : 'Disabled'}
                        </span>
                      </div>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">Approval Status</label>
                      <div className="flex items-center space-x-2">
                        {viewingUser.approval_status === 'approved' && <CheckCircle className="w-4 h-4 text-green-500" />}
                        {viewingUser.approval_status === 'pending' && <Clock className="w-4 h-4 text-yellow-500" />}
                        {viewingUser.approval_status === 'rejected' && <XCircle className="w-4 h-4 text-red-500" />}
                        <span className={`font-medium capitalize ${
                          viewingUser.approval_status === 'approved' ? 'text-green-700' :
                          viewingUser.approval_status === 'pending' ? 'text-yellow-700' : 'text-red-700'
                        }`}>
                          {viewingUser.approval_status || 'Approved'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Timestamps */}
                <div className="bg-gray-50 rounded-xl p-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <Calendar className="w-5 h-5 mr-2 text-indigo-600" />
                    Timeline
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-500">Created At</label>
                      <p className="text-gray-900 font-medium">
                        {viewingUser.created_at ? new Date(viewingUser.created_at).toLocaleDateString() : 'N/A'}
                      </p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-500">Last Updated</label>
                      <p className="text-gray-900 font-medium">
                        {viewingUser.updated_at ? new Date(viewingUser.updated_at).toLocaleDateString() : 'N/A'}
                      </p>
                    </div>
                    {viewingUser.approved_at && (
                      <div>
                        <label className="text-sm font-medium text-gray-500">Approved At</label>
                        <p className="text-gray-900 font-medium">
                          {new Date(viewingUser.approved_at).toLocaleDateString()}
                        </p>
                      </div>
                    )}
                    {viewingUser.approved_by && (
                      <div>
                        <label className="text-sm font-medium text-gray-500">Approved By</label>
                        <p className="text-gray-900 font-medium">{viewingUser.approved_by}</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Additional Information */}
                {(viewingUser.phone || viewingUser.bio || viewingUser.location) && (
                  <div className="bg-gray-50 rounded-xl p-4">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                      <Award className="w-5 h-5 mr-2 text-indigo-600" />
                      Additional Information
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {viewingUser.phone && (
                        <div>
                          <label className="text-sm font-medium text-gray-500">Phone</label>
                          <div className="flex items-center space-x-2">
                            <Phone className="w-4 h-4 text-gray-400" />
                            <p className="text-gray-900 font-medium">{viewingUser.phone}</p>
                          </div>
                        </div>
                      )}
                      {viewingUser.location && (
                        <div>
                          <label className="text-sm font-medium text-gray-500">Location</label>
                          <div className="flex items-center space-x-2">
                            <MapPin className="w-4 h-4 text-gray-400" />
                            <p className="text-gray-900 font-medium">{viewingUser.location}</p>
                          </div>
                        </div>
                      )}
                      {viewingUser.bio && (
                        <div className="md:col-span-2">
                          <label className="text-sm font-medium text-gray-500">Bio</label>
                          <p className="text-gray-900 mt-1">{viewingUser.bio}</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              {/* Footer */}
              <div className="flex justify-end space-x-3 p-6 border-t border-gray-200">
                <button
                  onClick={() => setShowUserModal(false)}
                  className="px-6 py-2 text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Close
                </button>
                <button
                  onClick={() => {
                    setSelectedUser(viewingUser);
                    setActionType(viewingUser.is_active ? 'disable' : 'enable');
                    setShowUserModal(false);
                    setShowActionModal(true);
                  }}
                  className={`px-6 py-2 text-white rounded-lg transition-colors ${
                    viewingUser.is_active
                      ? 'bg-red-600 hover:bg-red-700'
                      : 'bg-green-600 hover:bg-green-700'
                  }`}
                >
                  {viewingUser.is_active ? 'Disable User' : 'Enable User'}
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </AdminDashboardLayout>
  );
};

export default UserManagement;
