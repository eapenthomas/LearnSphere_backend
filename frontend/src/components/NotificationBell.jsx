import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bell, X, Check, AlertTriangle, Clock, CheckCircle, FileText, GraduationCap, MessageSquare, User, Settings, Eye } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const NotificationBell = () => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showDropdown, setShowDropdown] = useState(false);
  const [loading, setLoading] = useState(false);
  const [markingRead, setMarkingRead] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchNotificationCount();
    
    // Poll for new notifications every 30 seconds
    const interval = setInterval(() => {
      fetchNotificationCount();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('learnsphere_access_token') || localStorage.getItem('learnsphere_token');
      const response = await fetch('http://localhost:8000/api/notifications/?limit=10', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setNotifications(data);
      }
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchNotificationCount = async () => {
    try {
      const token = localStorage.getItem('learnsphere_access_token') || localStorage.getItem('learnsphere_token');
      const response = await fetch('http://localhost:8000/api/notifications/count', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUnreadCount(data.total_unread || 0);
      }
    } catch (error) {
      console.error('Error fetching notification count:', error);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      setMarkingRead(true);
      const token = localStorage.getItem('learnsphere_access_token') || localStorage.getItem('learnsphere_token');
      const response = await fetch(`http://localhost:8000/api/notifications/${notificationId}/read`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        // Update local state
        setNotifications(prev => 
          prev.map(notif => 
            notif.id === notificationId 
              ? { ...notif, is_read: true, read_at: new Date().toISOString() }
              : notif
          )
        );
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
    } catch (error) {
      console.error('Error marking notification as read:', error);
    } finally {
      setMarkingRead(false);
    }
  };

  const markAllAsRead = async () => {
    try {
      setMarkingRead(true);
      const token = localStorage.getItem('learnsphere_access_token') || localStorage.getItem('learnsphere_token');
      const response = await fetch('http://localhost:8000/api/notifications/mark-all-read', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        setNotifications(prev => 
          prev.map(notif => ({ ...notif, is_read: true, read_at: new Date().toISOString() }))
        );
        setUnreadCount(0);
      }
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
    } finally {
      setMarkingRead(false);
    }
  };

  const deleteNotification = async (notificationId) => {
    try {
      const token = localStorage.getItem('learnsphere_access_token') || localStorage.getItem('learnsphere_token');
      const response = await fetch(`http://localhost:8000/api/notifications/${notificationId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        setNotifications(prev => prev.filter(notif => notif.id !== notificationId));
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
    } catch (error) {
      console.error('Error deleting notification:', error);
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'assignment_created':
      case 'assignment_due_soon':
      case 'assignment_due_today':
      case 'assignment_overdue':
      case 'assignment_submitted':
      case 'assignment_graded':
        return <FileText className="w-4 h-4 text-blue-500" />;
      case 'quiz_available':
      case 'quiz_due_soon':
      case 'quiz_due_today':
      case 'quiz_overdue':
      case 'quiz_completed':
      case 'quiz_graded':
        return <GraduationCap className="w-4 h-4 text-purple-500" />;
      case 'course_enrolled':
      case 'course_updated':
      case 'new_material':
      case 'course_completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'forum_question_answered':
      case 'forum_new_question':
      case 'forum_question_resolved':
        return <MessageSquare className="w-4 h-4 text-orange-500" />;
      case 'account_approved':
      case 'account_rejected':
      case 'password_changed':
      case 'login_alert':
        return <Settings className="w-4 h-4 text-gray-500" />;
      default:
        return <Bell className="w-4 h-4 text-gray-500" />;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent':
        return 'border-l-red-500 bg-red-50';
      case 'high':
        return 'border-l-orange-500 bg-orange-50';
      case 'medium':
        return 'border-l-blue-500 bg-blue-50';
      case 'low':
        return 'border-l-gray-500 bg-gray-50';
      default:
        return 'border-l-gray-500 bg-gray-50';
    }
  };

  const formatTimeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;
    
    return date.toLocaleDateString();
  };

  const handleNotificationClick = (notification) => {
    if (!notification.is_read) {
      markAsRead(notification.id);
    }

    // Navigate based on action_url or type
    if (notification.action_url) {
      navigate(notification.action_url);
    } else {
      // Default navigation based on type
      switch (notification.type) {
        case 'assignment_created':
        case 'assignment_due_soon':
        case 'assignment_due_today':
        case 'assignment_overdue':
        case 'assignment_graded':
          navigate('/assignments');
          break;
        case 'quiz_available':
        case 'quiz_due_soon':
        case 'quiz_due_today':
        case 'quiz_overdue':
        case 'quiz_graded':
          navigate('/student/quizzes');
          break;
        case 'course_enrolled':
        case 'course_updated':
        case 'new_material':
          navigate('/mycourses');
          break;
        case 'forum_question_answered':
        case 'forum_new_question':
        case 'forum_question_resolved':
          navigate('/forum');
          break;
        default:
          navigate('/dashboard');
      }
    }
    
    setShowDropdown(false);
  };

  return (
    <div className="relative">
      {/* Notification Bell */}
      <button
        onClick={() => {
          setShowDropdown(!showDropdown);
          if (!showDropdown) {
            fetchNotifications();
          }
        }}
        className="relative p-2 rounded-lg hover:bg-background-tertiary transition-colors duration-200"
      >
        <Bell className="w-5 h-5 text-text-secondary" />
        {unreadCount > 0 && (
          <motion.span
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="absolute -top-1 -right-1 bg-error-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-medium"
          >
            {unreadCount > 99 ? '99+' : unreadCount}
          </motion.span>
        )}
      </button>

      {/* Notification Dropdown */}
      <AnimatePresence>
        {showDropdown && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="absolute right-0 mt-2 w-96 bg-white rounded-lg shadow-lg border border-border-primary overflow-hidden z-50"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-border-primary bg-background-secondary">
              <h3 className="text-heading-sm font-semibold text-text-heading">Notifications</h3>
              <div className="flex items-center space-x-2">
                {unreadCount > 0 && (
                  <button
                    onClick={markAllAsRead}
                    disabled={markingRead}
                    className="text-xs text-primary-600 hover:text-primary-700 font-medium disabled:opacity-50"
                  >
                    Mark all read
                  </button>
                )}
                <button
                  onClick={() => setShowDropdown(false)}
                  className="p-1 rounded hover:bg-background-tertiary transition-colors"
                >
                  <X className="w-4 h-4 text-text-secondary" />
                </button>
              </div>
            </div>

            {/* Notifications List */}
            <div className="max-h-96 overflow-y-auto">
              {loading ? (
                <div className="p-4 text-center text-text-secondary">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-500 mx-auto"></div>
                  <p className="mt-2 text-sm">Loading notifications...</p>
                </div>
              ) : notifications.length === 0 ? (
                <div className="p-6 text-center text-text-secondary">
                  <Bell className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p className="text-sm">No notifications yet</p>
                  <p className="text-xs mt-1">You'll see updates here when they arrive</p>
                </div>
              ) : (
                notifications.map((notification) => (
                  <motion.div
                    key={notification.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className={`p-4 border-l-4 cursor-pointer transition-colors hover:bg-background-tertiary ${getPriorityColor(notification.priority)} ${
                      !notification.is_read ? 'bg-blue-50' : ''
                    }`}
                    onClick={() => handleNotificationClick(notification)}
                  >
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 mt-0.5">
                        {getNotificationIcon(notification.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <h4 className="text-sm font-medium text-text-heading truncate">
                            {notification.title}
                          </h4>
                          <div className="flex items-center space-x-1">
                            <span className="text-xs text-text-secondary">
                              {formatTimeAgo(notification.created_at)}
                            </span>
                            {!notification.is_read && (
                              <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                            )}
                          </div>
                        </div>
                        <p className="text-sm text-text-secondary mt-1 line-clamp-2">
                          {notification.message}
                        </p>
                        {notification.priority === 'urgent' && (
                          <div className="flex items-center mt-2 text-xs text-red-600">
                            <AlertTriangle className="w-3 h-3 mr-1" />
                            Urgent
                          </div>
                        )}
                      </div>
                      <div className="flex-shrink-0">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteNotification(notification.id);
                          }}
                          className="p-1 rounded hover:bg-background-primary transition-colors opacity-0 group-hover:opacity-100"
                        >
                          <X className="w-3 h-3 text-text-secondary" />
                        </button>
                      </div>
                    </div>
                  </motion.div>
                ))
              )}
            </div>

            {/* Footer */}
            {notifications.length > 0 && (
              <div className="p-3 border-t border-border-primary bg-background-secondary">
                <button
                  onClick={() => navigate('/notifications')}
                  className="w-full text-center text-sm text-primary-600 hover:text-primary-700 font-medium"
                >
                  View all notifications
                </button>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default NotificationBell;
