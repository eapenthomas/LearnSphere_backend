import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext.jsx';
import AdminDashboardLayout from '../../layouts/AdminDashboardLayout.jsx';
import { adminOperations } from '../../utils/supabaseClient.js';
import { toast } from 'react-hot-toast';
import {
  Users,
  UserCheck,
  BookOpen,
  GraduationCap,
  AlertTriangle,
  TrendingUp,
  Activity,
  CheckCircle,
  XCircle,
  Mail,
  Shield,
  BarChart3,
  ArrowRight,
  RefreshCw
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

const AdminDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [recentActivity, setRecentActivity] = useState([]);

  useEffect(() => {
    fetchDashboardData();

    // Set up auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchDashboardData();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  // Handle card navigation
  const handleCardClick = (card) => {
    if (card.route) {
      if (card.filter) {
        navigate(`${card.route}?filter=${card.filter}`);
      } else {
        navigate(card.route);
      }
    }
  };

  // Format large numbers
  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toLocaleString();
  };

  const fetchDashboardData = async () => {
    try {
      setLoading(true);

      // Fetch real-time dashboard statistics
      const statsResponse = await fetch('http://localhost:8000/api/admin/dashboard/stats');
      if (statsResponse.ok) {
        const dashboardStats = await statsResponse.json();
        setStats(dashboardStats);
      }

      // Fetch recent activity from new API
      const activityResponse = await fetch('http://localhost:8000/api/admin/dashboard/activity?limit=10');
      if (activityResponse.ok) {
        const activity = await activityResponse.json();
        setRecentActivity(activity);
      }

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: 'Active Students',
      value: stats?.active_students || 0,
      icon: Users,
      color: 'from-indigo-500 to-blue-500',
      bgColor: 'bg-blue-50',
      textColor: 'text-blue-700',
      route: '/admin/users',
      filter: 'students',
      description: 'Currently enrolled students'
    },
    {
      title: 'Active Teachers',
      value: stats?.active_teachers || 0,
      icon: UserCheck,
      color: 'from-emerald-500 to-green-500',
      bgColor: 'bg-green-50',
      textColor: 'text-green-700',
      route: '/admin/users',
      filter: 'teachers',
      description: 'Approved teaching staff'
    },
    {
      title: 'Pending Approvals',
      value: stats?.pending_approvals || 0,
      icon: AlertTriangle,
      color: 'from-amber-500 to-yellow-500',
      bgColor: 'bg-yellow-50',
      textColor: 'text-yellow-700',
      route: '/admin/approvals',
      filter: null,
      description: 'Teachers awaiting approval',
      actionRequired: true
    },
    {
      title: 'Active Courses',
      value: stats?.active_courses || 0,
      icon: BookOpen,
      color: 'from-purple-500 to-violet-500',
      bgColor: 'bg-purple-50',
      textColor: 'text-purple-700',
      route: '/admin/courses',
      filter: null,
      description: 'Published courses'
    },
    {
      title: 'Total Quizzes',
      value: stats?.total_quizzes || 0,
      icon: CheckCircle,
      color: 'from-green-500 to-emerald-500',
      bgColor: 'bg-emerald-50',
      textColor: 'text-emerald-700',
      route: '/admin/quizzes',
      filter: null,
      description: 'Quiz assessments created'
    },
    {
      title: 'AI Tokens Used',
      value: stats?.ai_tokens_used || 0,
      icon: BarChart3,
      color: 'from-purple-500 to-violet-500',
      bgColor: 'bg-purple-50',
      textColor: 'text-purple-700',
      route: '/admin/ai-usage',
      filter: null,
      description: 'AI API tokens consumed',
      isLarge: true
    }
  ];

  // Sample data for charts
  const userGrowthData = [
    { name: 'Jan', students: 45, teachers: 8 },
    { name: 'Feb', students: 52, teachers: 12 },
    { name: 'Mar', students: 68, teachers: 15 },
    { name: 'Apr', students: 78, teachers: 18 },
    { name: 'May', students: 89, teachers: 22 },
    { name: 'Jun', students: 95, teachers: 25 }
  ];

  const userDistributionData = [
    { name: 'Students', value: stats?.active_students || 0, color: '#3b82f6' },
    { name: 'Teachers', value: stats?.active_teachers || 0, color: '#10b981' },
    { name: 'Disabled', value: stats?.disabled_users || 0, color: '#ef4444' }
  ];

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getActivityIcon = (action) => {
    switch (action) {
      case 'user_enabled':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'user_disabled':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'teacher_approved':
        return <UserCheck className="w-4 h-4 text-blue-500" />;
      case 'teacher_rejected':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      default:
        return <Activity className="w-4 h-4 text-gray-500" />;
    }
  };



  return (
    <AdminDashboardLayout>
      <div className="p-6 space-y-8">
        {/* Welcome Banner */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative overflow-hidden bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 p-8"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-indigo-500 to-blue-500 opacity-5"></div>
          <div className="relative z-10">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-semibold text-gray-900 mb-3">
                  Welcome back, {user?.fullName?.split(' ')[0] || 'Admin'}! 🛡️
                </h1>
                <p className="text-base text-gray-600 mb-6">
                  Monitor and manage the LearnSphere platform. Keep everything running smoothly!
                </p>
                <div className="flex flex-wrap items-center gap-6">
                  <div className="flex items-center space-x-2 bg-blue-50 px-4 py-2 rounded-lg">
                    <Users className="w-5 h-5 text-blue-600" />
                    <span className="font-semibold text-blue-700">
                      {(stats?.active_students || 0) + (stats?.active_teachers || 0)} Total Users
                    </span>
                  </div>
                  <div className="flex items-center space-x-2 bg-yellow-50 px-4 py-2 rounded-lg">
                    <AlertTriangle className="w-5 h-5 text-yellow-600" />
                    <span className="font-semibold text-yellow-700">
                      {stats?.pending_approvals || 0} Pending Approvals
                    </span>
                  </div>
                  <div className="flex items-center space-x-2 bg-green-50 px-4 py-2 rounded-lg">
                    <BookOpen className="w-5 h-5 text-green-600" />
                    <span className="font-semibold text-green-700">
                      {stats?.active_courses || 0} Active Courses
                    </span>
                  </div>
                </div>
              </div>
              <div className="hidden md:flex items-center space-x-4">
                <button
                  onClick={fetchDashboardData}
                  className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  disabled={loading}
                >
                  <RefreshCw className={`w-4 h-4 text-gray-600 ${loading ? 'animate-spin' : ''}`} />
                  <span className="text-sm font-medium text-gray-700">
                    {loading ? 'Refreshing...' : 'Refresh'}
                  </span>
                </button>
                <div className="w-24 h-24 bg-gradient-to-r from-indigo-500 to-blue-500 rounded-full flex items-center justify-center shadow-lg">
                  <Shield className="w-12 h-12 text-white" />
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {statCards.map((stat, index) => (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white shadow rounded-xl p-4 border border-gray-200 hover:shadow-lg transition-all duration-300 group cursor-pointer"
              onClick={() => handleCardClick(stat)}
            >
              <div className="p-4">
                <div className="flex items-center justify-between mb-4">
                  <div className={`p-3 ${stat.bgColor} rounded-xl group-hover:scale-110 transition-transform duration-300`}>
                    <stat.icon className={`w-6 h-6 ${stat.textColor}`} />
                  </div>
                  {stat.title === 'Pending Approvals' && stat.value > 0 && (
                    <span className="px-3 py-1 bg-red-100 text-red-700 text-xs font-semibold rounded-full animate-pulse">
                      Action Required
                    </span>
                  )}
                  <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-gray-600 group-hover:translate-x-1 transition-all duration-300" />
                </div>
                <h3 className="text-3xl font-extrabold text-gray-800 mb-2">
                  {stat.isLarge ? formatNumber(stat.value) : stat.value.toLocaleString()}
                  {stat.isPercentage && '%'}
                </h3>
                <p className="text-sm text-gray-600 font-medium">{stat.title}</p>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 p-6"
        >
          <h2 className="text-xl font-bold text-gray-800 mb-6">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link
              to="/admin/approvals"
              className="flex items-center space-x-3 p-4 bg-gradient-to-r from-indigo-500 to-blue-500 text-white font-semibold rounded-xl shadow-md hover:shadow-lg transition-all duration-300 hover:scale-105"
            >
              <UserCheck className="w-5 h-5" />
              <span>Review Approvals</span>
            </Link>
            <Link
              to="/admin/users"
              className="flex items-center space-x-3 p-4 bg-gradient-to-r from-emerald-500 to-green-500 text-white font-semibold rounded-xl shadow-md hover:shadow-lg transition-all duration-300 hover:scale-105"
            >
              <Users className="w-5 h-5" />
              <span>Manage Users</span>
            </Link>
            <Link
              to="/admin/ai-usage"
              className="flex items-center space-x-3 p-4 bg-gradient-to-r from-purple-500 to-violet-500 text-white font-semibold rounded-xl shadow-md hover:shadow-lg transition-all duration-300 hover:scale-105"
            >
              <BarChart3 className="w-5 h-5" />
              <span>AI Usage Analytics</span>
            </Link>
          </div>
        </motion.div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* User Growth Chart */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-800">User Growth Over Time</h2>
              <div className="p-2 bg-blue-50 rounded-lg">
                <TrendingUp className="w-5 h-5 text-blue-600" />
              </div>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={userGrowthData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis
                    dataKey="name"
                    stroke="#64748b"
                    fontSize={12}
                    tickLine={false}
                  />
                  <YAxis
                    stroke="#64748b"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: 'none',
                      borderRadius: '12px',
                      boxShadow: '0 10px 25px rgba(0,0,0,0.1)',
                      fontSize: '14px'
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="students"
                    stroke="#3b82f6"
                    strokeWidth={3}
                    dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6, stroke: '#3b82f6', strokeWidth: 2 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="teachers"
                    stroke="#10b981"
                    strokeWidth={3}
                    dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6, stroke: '#10b981', strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="flex items-center justify-center space-x-6 mt-4">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <span className="text-sm text-gray-600 font-medium">Students</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="text-sm text-gray-600 font-medium">Teachers</span>
              </div>
            </div>
          </motion.div>

          {/* User Distribution Chart */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-800">User Distribution by Role</h2>
              <div className="p-2 bg-purple-50 rounded-lg">
                <BarChart3 className="w-5 h-5 text-purple-600" />
              </div>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={userDistributionData}
                    cx="50%"
                    cy="50%"
                    outerRadius={90}
                    innerRadius={40}
                    dataKey="value"
                    paddingAngle={5}
                  >
                    {userDistributionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: 'none',
                      borderRadius: '12px',
                      boxShadow: '0 10px 25px rgba(0,0,0,0.1)',
                      fontSize: '14px'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="flex flex-wrap items-center justify-center gap-4 mt-4">
              {userDistributionData.map((entry, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: entry.color }}
                  ></div>
                  <span className="text-sm text-gray-600 font-medium">
                    {entry.name}: {entry.value}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 p-6"
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-800">Recent Activity Feed</h2>
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-green-50 rounded-lg">
                <Activity className="w-5 h-5 text-green-600" />
              </div>
              <Link
                to="/admin/activity"
                className="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
              >
                View All
              </Link>
            </div>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
            </div>
          ) : recentActivity.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <Activity className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-lg font-medium">No recent activity</p>
              <p className="text-sm">Activity will appear here as users interact with the system</p>
            </div>
          ) : (
            <div className="space-y-3">
              {recentActivity.slice(0, 5).map((activity, index) => (
                <motion.div
                  key={activity.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center space-x-4 p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-all duration-200 border border-gray-100"
                >
                  <div className="flex-shrink-0">
                    {getActivityIcon(activity.action)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-gray-900">
                      {activity.profiles?.full_name || 'Unknown User'}
                    </p>
                    <p className="text-sm text-gray-600 capitalize">
                      {activity.action.replace('_', ' ')} • {activity.profiles?.role}
                    </p>
                  </div>
                  <div className="flex-shrink-0 text-right">
                    <p className="text-xs text-gray-500 font-medium">
                      {formatDate(activity.created_at)}
                    </p>
                    <div className="w-2 h-2 bg-green-400 rounded-full mt-1 ml-auto"></div>
                  </div>
                </motion.div>
              ))}
              {recentActivity.length > 5 && (
                <div className="text-center pt-4">
                  <Link
                    to="/admin/activity"
                    className="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
                  >
                    View {recentActivity.length - 5} more activities →
                  </Link>
                </div>
              )}
            </div>
          )}
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl shadow-lg p-6 hover:shadow-xl transition-all duration-300"
        >
          <h2 className="text-xl font-extrabold text-gray-800 mb-6">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <button
              onClick={() => window.location.href = '/admin/approvals'}
              className="p-4 bg-yellow-50 hover:bg-yellow-100 rounded-xl border border-yellow-200 transition-colors group"
            >
              <UserCheck className="w-8 h-8 text-yellow-600 mb-2 group-hover:scale-110 transition-transform" />
              <h3 className="font-semibold text-yellow-800">Review Approvals</h3>
              <p className="text-sm text-yellow-600">{stats?.pending_approvals || 0} pending</p>
            </button>
            
            <button
              onClick={() => window.location.href = '/admin/users'}
              className="p-4 bg-blue-50 hover:bg-blue-100 rounded-xl border border-blue-200 transition-colors group"
            >
              <Users className="w-8 h-8 text-blue-600 mb-2 group-hover:scale-110 transition-transform" />
              <h3 className="font-semibold text-blue-800">Manage Users</h3>
              <p className="text-sm text-blue-600">Enable/disable accounts</p>
            </button>
            
            <button
              onClick={() => window.location.href = '/admin/activity'}
              className="p-4 bg-green-50 hover:bg-green-100 rounded-xl border border-green-200 transition-colors group"
            >
              <Activity className="w-8 h-8 text-green-600 mb-2 group-hover:scale-110 transition-transform" />
              <h3 className="font-semibold text-green-800">View Activity</h3>
              <p className="text-sm text-green-600">Monitor system logs</p>
            </button>
            
            <button
              onClick={() => window.location.href = '/admin/emails'}
              className="p-4 bg-purple-50 hover:bg-purple-100 rounded-xl border border-purple-200 transition-colors group"
            >
              <Mail className="w-8 h-8 text-purple-600 mb-2 group-hover:scale-110 transition-transform" />
              <h3 className="font-semibold text-purple-800">Email Logs</h3>
              <p className="text-sm text-purple-600">Check notifications</p>
            </button>
          </div>
        </motion.div>
      </div>
    </AdminDashboardLayout>
  );
};

export default AdminDashboard;
