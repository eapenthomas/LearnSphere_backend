import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Bell, Mail, Smartphone, Clock, Settings, Save, Check } from 'lucide-react';
import { toast } from 'react-hot-toast';

const NotificationSettings = () => {
  const [preferences, setPreferences] = useState({
    email_notifications: true,
    in_app_notifications: true,
    assignment_reminders: true,
    quiz_reminders: true,
    forum_notifications: true,
    course_updates: true,
    system_notifications: true,
    quiet_hours_start: null,
    quiet_hours_end: null
  });
  
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [quietHoursEnabled, setQuietHoursEnabled] = useState(false);

  useEffect(() => {
    fetchNotificationPreferences();
  }, []);

  const fetchNotificationPreferences = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/notifications/preferences', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setPreferences(data);
        setQuietHoursEnabled(!!(data.quiet_hours_start && data.quiet_hours_end));
      }
    } catch (error) {
      console.error('Error fetching notification preferences:', error);
      toast.error('Failed to load notification preferences');
    } finally {
      setLoading(false);
    }
  };

  const saveNotificationPreferences = async () => {
    try {
      setSaving(true);
      const token = localStorage.getItem('token');
      
      const preferencesToSave = {
        ...preferences,
        quiet_hours_start: quietHoursEnabled ? preferences.quiet_hours_start : null,
        quiet_hours_end: quietHoursEnabled ? preferences.quiet_hours_end : null
      };
      
      const response = await fetch('http://localhost:8000/api/notifications/preferences', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(preferencesToSave)
      });
      
      if (response.ok) {
        toast.success('Notification preferences saved successfully');
      } else {
        throw new Error('Failed to save preferences');
      }
    } catch (error) {
      console.error('Error saving notification preferences:', error);
      toast.error('Failed to save notification preferences');
    } finally {
      setSaving(false);
    }
  };

  const handlePreferenceChange = (key, value) => {
    setPreferences(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleQuietHoursToggle = () => {
    setQuietHoursEnabled(!quietHoursEnabled);
    if (!quietHoursEnabled) {
      setPreferences(prev => ({
        ...prev,
        quiet_hours_start: '22:00',
        quiet_hours_end: '08:00'
      }));
    }
  };

  const notificationCategories = [
    {
      title: "Assignment Notifications",
      description: "Get notified about assignments, deadlines, and grades",
      icon: "📝",
      settings: [
        { key: "assignment_reminders", label: "Assignment reminders", description: "Reminders for upcoming assignment deadlines" }
      ]
    },
    {
      title: "Quiz Notifications", 
      description: "Stay updated on quiz availability and results",
      icon: "🧠",
      settings: [
        { key: "quiz_reminders", label: "Quiz reminders", description: "Reminders for quiz deadlines and availability" }
      ]
    },
    {
      title: "Course Updates",
      description: "Notifications about course changes and new materials",
      icon: "📚",
      settings: [
        { key: "course_updates", label: "Course updates", description: "New materials, announcements, and course changes" }
      ]
    },
    {
      title: "Forum & Discussions",
      description: "Stay connected with course discussions",
      icon: "💬",
      settings: [
        { key: "forum_notifications", label: "Forum notifications", description: "New questions, answers, and discussions" }
      ]
    },
    {
      title: "System Notifications",
      description: "Account updates and system announcements",
      icon: "⚙️",
      settings: [
        { key: "system_notifications", label: "System notifications", description: "Account updates, security alerts, and announcements" }
      ]
    }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-background-primary flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background-primary">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-3 bg-primary-100 rounded-lg">
              <Bell className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-text-heading">Notification Settings</h1>
              <p className="text-text-secondary">Manage how and when you receive notifications</p>
            </div>
          </div>
        </motion.div>

        {/* Notification Channels */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-lg shadow-elegant p-6 mb-6 border border-border-primary"
        >
          <h2 className="text-xl font-semibold text-text-heading mb-4">Notification Channels</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-blue-100 rounded-lg">
                <Mail className="w-5 h-5 text-blue-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-medium text-text-heading">Email Notifications</h3>
                <p className="text-sm text-text-secondary">Receive notifications via email</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.email_notifications}
                  onChange={(e) => handlePreferenceChange('email_notifications', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>

            <div className="flex items-center space-x-4">
              <div className="p-3 bg-green-100 rounded-lg">
                <Smartphone className="w-5 h-5 text-green-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-medium text-text-heading">In-App Notifications</h3>
                <p className="text-sm text-text-secondary">Show notifications in the app</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={preferences.in_app_notifications}
                  onChange={(e) => handlePreferenceChange('in_app_notifications', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>
          </div>
        </motion.div>

        {/* Quiet Hours */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-lg shadow-elegant p-6 mb-6 border border-border-primary"
        >
          <div className="flex items-center space-x-3 mb-4">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Clock className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-text-heading">Quiet Hours</h2>
              <p className="text-text-secondary">Set times when you don't want to receive notifications</p>
            </div>
          </div>

          <div className="flex items-center space-x-4 mb-4">
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={quietHoursEnabled}
                onChange={handleQuietHoursToggle}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
            <span className="text-text-heading font-medium">Enable Quiet Hours</span>
          </div>

          {quietHoursEnabled && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-text-heading mb-2">
                  Start Time
                </label>
                <input
                  type="time"
                  value={preferences.quiet_hours_start || '22:00'}
                  onChange={(e) => handlePreferenceChange('quiet_hours_start', e.target.value)}
                  className="w-full px-3 py-2 border border-border-primary rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-text-heading mb-2">
                  End Time
                </label>
                <input
                  type="time"
                  value={preferences.quiet_hours_end || '08:00'}
                  onChange={(e) => handlePreferenceChange('quiet_hours_end', e.target.value)}
                  className="w-full px-3 py-2 border border-border-primary rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </div>
          )}
        </motion.div>

        {/* Notification Categories */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="space-y-6"
        >
          {notificationCategories.map((category, index) => (
            <motion.div
              key={category.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 + index * 0.1 }}
              className="bg-white rounded-lg shadow-elegant p-6 border border-border-primary"
            >
              <div className="flex items-center space-x-3 mb-4">
                <span className="text-2xl">{category.icon}</span>
                <div>
                  <h3 className="text-lg font-semibold text-text-heading">{category.title}</h3>
                  <p className="text-text-secondary">{category.description}</p>
                </div>
              </div>

              <div className="space-y-4">
                {category.settings.map((setting) => (
                  <div key={setting.key} className="flex items-center justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium text-text-heading">{setting.label}</h4>
                      <p className="text-sm text-text-secondary">{setting.description}</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={preferences[setting.key]}
                        onChange={(e) => handlePreferenceChange(setting.key, e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                    </label>
                  </div>
                ))}
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Save Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="mt-8 flex justify-end"
        >
          <button
            onClick={saveNotificationPreferences}
            disabled={saving}
            className="flex items-center space-x-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:ring-4 focus:ring-primary-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Saving...</span>
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                <span>Save Preferences</span>
              </>
            )}
          </button>
        </motion.div>
      </div>
    </div>
  );
};

export default NotificationSettings;
