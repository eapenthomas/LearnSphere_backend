import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext.jsx';
import TeacherNotificationBell from '../components/TeacherNotificationBell.jsx';
import {
  BookOpen,
  Home,
  GraduationCap,
  Calendar,
  BarChart3,
  Settings,
  Bell,
  Menu,
  X,
  User,
  LogOut,
  ChevronDown,
  FileText,
  HelpCircle,
  Target,
  UserCheck,
  AlertTriangle,
  CheckCircle,
  Users,
  ClipboardList,
  MessageSquare,
  PieChart
} from 'lucide-react';

const TeacherDashboardLayout = ({ children }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  const [profilePictureUrl, setProfilePictureUrl] = useState(null);
  const [notifications] = useState([
    { id: 1, message: 'New assignment submission from John Doe', time: '5 min ago', type: 'submission' },
    { id: 2, message: 'Quiz deadline approaching: JavaScript Basics', time: '1 hour ago', type: 'deadline' },
    { id: 3, message: 'New question in doubt forum', time: '2 hours ago', type: 'question' }
  ]);

  // Fetch profile picture
  useEffect(() => {
    const fetchProfilePicture = async () => {
      if (user?.id) {
        try {
          const response = await fetch(`http://localhost:8000/api/profile-picture/${user.id}`);
          if (response.ok) {
            const data = await response.json();
            setProfilePictureUrl(data.profile_picture_url);
          }
        } catch (error) {
          console.log('Profile picture not available:', error);
        }
      }
    };

    fetchProfilePicture();
  }, [user]);

  const navigation = [
    { name: 'Dashboard', href: '/teacher/dashboard', icon: Home },
    { name: 'My Courses', href: '/teacher/courses', icon: BookOpen },
    { name: 'Quizzes', href: '/teacher/quizzes', icon: FileText },
    { name: 'Assignments', href: '/teacher/assignments', icon: ClipboardList },
    { name: 'Student Progress', href: '/teacher/progress', icon: Users },
    { name: 'Doubt Forum', href: '/teacher/forum', icon: MessageSquare },
    { name: 'Calendar', href: '/teacher/calendar', icon: Calendar },
    { name: 'Reports', href: '/teacher/reports', icon: PieChart },
    { name: 'Profile & Settings', href: '/teacher/profile', icon: Settings }
  ];

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = () => {
      setProfileDropdownOpen(false);
    };
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Mobile sidebar overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-gray-600/50 z-40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-72 bg-background-secondary border-r border-border-primary lg:static lg:z-auto shadow-elegant ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      }`}>
        <div className="flex items-center justify-between h-16 px-6 border-b border-border-primary">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-r from-navy-900 to-navy-800 rounded-lg shadow-elegant">
              <BookOpen className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-text-heading tracking-tight font-serif">LearnSphere</span>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-2 rounded-lg hover:bg-background-tertiary transition-colors"
          >
            <X className="w-5 h-5 text-text-secondary" />
          </button>
        </div>

        <nav className="mt-8 px-6 flex-1">
          <div className="space-y-2">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={`sidebar-item group ${
                    isActive ? 'active' : ''
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                  <span className="font-medium">{item.name}</span>
                  {isActive && (
                    <motion.div
                      layoutId="activeTab"
                      className="absolute right-0 w-1 h-8 bg-gradient-to-b from-navy-600 to-navy-700 rounded-l-full"
                    />
                  )}
                </Link>
              );
            })}
          </div>
        </nav>

        {/* Logout Button */}
        <div className="p-6 border-t border-gray-200">
          <button
            onClick={handleLogout}
            className="sidebar-item group text-red-600 hover:text-red-700 hover:bg-red-50 w-full"
          >
            <LogOut className="w-5 h-5" />
            <span className="font-bold">Logout</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Navigation */}
        <header className="bg-background-secondary border-b border-border-primary px-6 py-4 shadow-elegant">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {/* Mobile menu button */}
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden p-2 rounded-lg hover:bg-background-tertiary transition-colors"
              >
                <Menu className="w-5 h-5 text-text-secondary" />
              </button>

              {/* Welcome Message */}
              <div className="hidden md:block">
                <h1 className="text-heading-md font-semibold text-text-heading font-serif">
                  Welcome back, {user?.fullName?.split(' ')[0] || 'Teacher'}!
                </h1>
                <p className="text-body-md text-text-secondary">
                  Ready to inspire and educate your students today?
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-4">

              {/* Notifications */}
              <TeacherNotificationBell />

              {/* Profile Dropdown */}
              <div className="relative">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setProfileDropdownOpen(!profileDropdownOpen);
                  }}
                  className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  {profilePictureUrl ? (
                    <img
                      src={profilePictureUrl}
                      alt="Profile"
                      className="w-8 h-8 rounded-full object-cover border-2 border-white shadow-sm"
                      onError={() => setProfilePictureUrl(null)}
                    />
                  ) : (
                    <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                      {user?.fullName?.charAt(0) || user?.email?.charAt(0) || 'T'}
                    </div>
                  )}
                  <ChevronDown className="w-4 h-4 text-gray-600" />
                </button>

                <AnimatePresence>
                  {profileDropdownOpen && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50"
                    >
                      <Link
                        to="/teacher/profile"
                        className="flex items-center space-x-3 px-4 py-2 text-gray-700 hover:bg-gray-100 transition-colors"
                      >
                        <User className="w-4 h-4" />
                        <span className="font-medium">Profile</span>
                      </Link>
                      <Link
                        to="/teacher/settings"
                        className="flex items-center space-x-3 px-4 py-2 text-gray-700 hover:bg-gray-100 transition-colors"
                      >
                        <Settings className="w-4 h-4" />
                        <span className="font-medium">Settings</span>
                      </Link>
                      <hr className="my-2 border-gray-200" />
                      <button
                        onClick={handleLogout}
                        className="flex items-center space-x-3 px-4 py-2 text-red-600 hover:bg-red-50 transition-colors w-full text-left"
                      >
                        <LogOut className="w-4 h-4" />
                        <span className="font-medium">Logout</span>
                      </button>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 page-container bg-background-primary overflow-y-auto h-screen">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="dashboard-container"
          >
            {children}
          </motion.div>
        </main>
      </div>
    </div>
  );
};

export default TeacherDashboardLayout;
