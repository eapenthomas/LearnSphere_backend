import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext.jsx';
import ProfilePictureUpload from './ProfilePictureUpload.jsx';
import LearnSphereLogo from './LearnSphereLogo.jsx';
import VoiceNavigation from './VoiceNavigation.jsx';
import NotificationBell from './NotificationBell.jsx';
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
  Bot,
  BookOpenCheck,
  Library,
  ClipboardList,
  Brain,
  MessageSquare,
  CalendarDays,
  UserCog
} from 'lucide-react';

const DashboardLayout = ({ children }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const [profilePictureUrl, setProfilePictureUrl] = useState(null);
  const [loggingOut, setLoggingOut] = useState(false);

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: Home },
    { name: 'My Courses', href: '/mycourses', icon: BookOpenCheck },
    { name: 'All Courses', href: '/allcourses', icon: Library },
    { name: 'Assignments', href: '/assignments', icon: ClipboardList },
    { name: 'Quizzes', href: '/student/quizzes', icon: Target },

    { name: 'Notes Summarizer', href: '/student/notes-summarizer', icon: FileText },
    { name: 'AI Tutor', href: '/student/ai-tutor', icon: Bot },
    { name: 'Doubt Forum', href: '/forum', icon: MessageSquare },
    { name: 'Calendar', href: '/calendar', icon: CalendarDays },
    { name: 'Profile & Settings', href: '/profile', icon: UserCog },
  ];

  const handleLogoutClick = () => {
    setShowLogoutConfirm(true);
    setUserMenuOpen(false);
  };

  const handleLogoutConfirm = async () => {
    setLoggingOut(true);
    try {
      const result = await logout();
      if (result.success) {
        console.log('Logout successful, redirecting to login...');
        navigate('/login', { replace: true });
      } else {
        console.error('Logout failed:', result.error);
        // Still redirect even if logout had issues
        navigate('/login', { replace: true });
      }
    } catch (error) {
      console.error('Logout error:', error);
      // Still redirect to login page
      navigate('/login', { replace: true });
    } finally {
      setLoggingOut(false);
      setShowLogoutConfirm(false);
    }
  };

  const handleLogoutCancel = () => {
    setShowLogoutConfirm(false);
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event) => {
      // Ctrl+Shift+L or Cmd+Shift+L for logout
      if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'L') {
        event.preventDefault();
        handleLogoutClick();
      }
      // Escape to close logout modal
      if (event.key === 'Escape' && showLogoutConfirm) {
        handleLogoutCancel();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [showLogoutConfirm]);

  // Initialize profile picture from user data
  useEffect(() => {
    if (user?.profile_picture) {
      setProfilePictureUrl(user.profile_picture);
    }
  }, [user]);

  // Listen for profile picture updates
  useEffect(() => {
    const handleProfilePictureUpdate = (event) => {
      setProfilePictureUrl(event.detail.profilePictureUrl);
    };

    window.addEventListener('profilePictureUpdated', handleProfilePictureUpdate);
    return () => window.removeEventListener('profilePictureUpdated', handleProfilePictureUpdate);
  }, []);

  return (
    <div className="flex h-screen bg-background-primary">
      {/* Mobile sidebar overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-navy-900/50 z-40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-72 bg-navy-900 border-r border-navy-800 lg:static lg:z-auto shadow-elegant ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}>
        <div className="flex items-center justify-between h-16 px-6 border-b border-navy-800">
          <LearnSphereLogo size="md" showText={true} className="text-white" />
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-2 rounded-lg hover:bg-navy-800 transition-colors"
          >
            <X className="w-5 h-5 text-white" />
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
                  className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-300 relative group ${
                    isActive
                      ? 'bg-secondary-600 text-white shadow-elegant'
                      : 'text-navy-200 hover:text-white hover:bg-navy-800'
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                  <span className="font-medium">{item.name}</span>
                  {isActive && (
                    <motion.div
                      layoutId="activeTab"
                      className="absolute right-0 w-1 h-8 bg-gradient-to-b from-secondary-500 to-secondary-600 rounded-l-full"
                    />
                  )}
                </Link>
              );
            })}
          </div>
        </nav>

        {/* User Profile Section */}
        <div className="absolute bottom-0 left-0 right-0 p-6 border-t border-gray-200">
          <div className="relative">
            <button
              onClick={() => setUserMenuOpen(!userMenuOpen)}
              className="flex items-center space-x-3 w-full p-3 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <ProfilePictureUpload
                currentPictureUrl={profilePictureUrl}
                onPictureUpdate={setProfilePictureUrl}
                size="small"
              />
              <div className="flex-1 text-left">
                <p className="text-sm font-bold text-white truncate">
                  {user?.fullName || user?.email || 'User'}
                </p>
                <p className="text-xs text-gray-300 capitalize font-medium">
                  {user?.role || 'Student'}
                </p>
              </div>
              <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${userMenuOpen ? 'rotate-180' : ''
                }`} />
            </button>

            <AnimatePresence>
              {userMenuOpen && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  className="absolute bottom-full left-0 right-0 mb-2 bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden"
                >
                  <button
                    onClick={handleLogoutClick}
                    className="flex items-center space-x-3 w-full p-3 hover:bg-gray-50 transition-colors text-left"
                  >
                    <LogOut className="w-4 h-4 text-gray-600" />
                    <span className="text-sm font-bold text-gray-700">Logout</span>
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Navigation */}
        <header className="bg-background-secondary border-b border-border-primary sticky top-0 z-30 shadow-elegant">
          <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden p-2 rounded-lg hover:bg-background-tertiary transition-colors"
              >
                <Menu className="w-5 h-5 text-text-secondary" />
              </button>
              <h1 className="text-heading-md font-bold text-text-heading tracking-tight font-serif">
                {navigation.find(item => item.href === location.pathname)?.name || 'Dashboard'}
              </h1>
            </div>

            <div className="flex items-center space-x-4">
              {/* Welcome Message */}
              <div className="hidden md:block">
                <p className="text-body-md text-text-secondary">
                  Welcome back, <span className="font-semibold text-text-heading">
                    {user?.fullName?.split(' ')[0] || user?.email?.split('@')[0] || 'Student'}
                  </span>!
                </p>
              </div>


              {/* Notifications */}
              <NotificationBell />

              {/* User Profile Picture/Initials */}
              <div className="flex items-center space-x-3">
                <ProfilePictureUpload
                  currentPictureUrl={profilePictureUrl}
                  onPictureUpdate={setProfilePictureUrl}
                  size="small"
                />
                <div className="hidden md:block">
                  <p className="text-body-sm font-semibold text-text-heading">
                    {user?.fullName || user?.email || 'User'}
                  </p>
                </div>
              </div>

              {/* Quick Logout Button (Desktop) */}
              <button
                onClick={handleLogoutClick}
                className="hidden lg:flex items-center space-x-2 px-3 py-2 text-text-secondary hover:text-error-600 hover:bg-error-50 rounded-lg transition-all duration-200 group"
                title="Logout"
              >
                <LogOut className="w-4 h-4" />
                <span className="text-body-sm font-medium">Logout</span>
              </button>

              {/* User Menu (Mobile) */}
              <div className="lg:hidden relative">
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${userMenuOpen ? 'rotate-180' : ''
                    }`} />
                </button>

                <AnimatePresence>
                  {userMenuOpen && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: 10 }}
                      className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden z-50"
                    >
                      <div className="p-3 border-b border-gray-200">
                        <p className="text-sm font-bold text-gray-800">
                          {user?.fullName || user?.email || 'User'}
                        </p>
                        <p className="text-xs text-gray-500 capitalize font-medium">
                          {user?.role || 'Student'}
                        </p>
                      </div>
                      <button
                        onClick={handleLogoutClick}
                        className="flex items-center space-x-3 w-full p-3 hover:bg-gray-50 transition-colors text-left"
                      >
                        <LogOut className="w-4 h-4 text-gray-600" />
                        <span className="text-sm font-bold text-gray-700">Logout</span>
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

      {/* Logout Confirmation Modal */}
      <AnimatePresence>
        {showLogoutConfirm && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={handleLogoutCancel}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2 bg-red-100 rounded-full">
                  <AlertTriangle className="w-6 h-6 text-red-600" />
                </div>
                <h3 className="text-lg font-bold text-gray-800">Confirm Logout</h3>
              </div>

              <p className="text-gray-600 mb-6">
                Are you sure you want to logout? You'll need to sign in again to access your dashboard.
              </p>

              <div className="flex space-x-3">
                <button
                  onClick={handleLogoutCancel}
                  disabled={loggingOut}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleLogoutConfirm}
                  disabled={loggingOut}
                  className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium disabled:opacity-50 flex items-center justify-center space-x-2"
                >
                  {loggingOut ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span>Logging out...</span>
                    </>
                  ) : (
                    <>
                      <LogOut className="w-4 h-4" />
                      <span>Logout</span>
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Voice Navigation Component */}
      <VoiceNavigation />
    </div>
  );
};

export default DashboardLayout; 