import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext.jsx';
import { toast } from 'react-hot-toast';
import ProfilePictureUpload from '../../components/ProfilePictureUpload.jsx';
import TeacherDashboardLayout from '../../layouts/TeacherDashboardLayout.jsx';
import {
  User,
  Mail,
  Phone,
  MapPin,
  Calendar,
  BookOpen,
  Award,
  Settings,
  Camera,
  Save,
  Edit3,
  Shield,
  Bell,
  Globe,
  Lock,
  Eye,
  EyeOff,
  Check,
  X,
  Star,
  FileText
} from 'lucide-react';

const TeacherProfile = () => {
  const { user, updateProfile } = useAuth();
  const [loading, setLoading] = useState(false);

  // Debug logging
  console.log('TeacherProfile - User:', user);

  // Early return if no user
  if (!user) {
    return (
      <TeacherDashboardLayout>
        <div className="min-h-screen bg-gray-50 p-6 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading user data...</p>
          </div>
        </div>
      </TeacherDashboardLayout>
    );
  }
  const [activeTab, setActiveTab] = useState('profile');
  const [isEditing, setIsEditing] = useState(false);
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  
  const [profileData, setProfileData] = useState({
    full_name: '',
    email: '',
    phone: '',
    bio: '',
    location: '',
    department: '',
    specialization: '',
    experience_years: '',
    education: '',
    linkedin_url: '',
    website_url: ''
  });

  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  });

  const [settings, setSettings] = useState({
    emailNotifications: true,
    pushNotifications: true,
    weeklyReports: true,
    studentMessages: true,
    assignmentReminders: true,
    profileVisibility: 'public'
  });

  const [ratings, setRatings] = useState([]);
  const [ratingSummary, setRatingSummary] = useState(null);
  const [profilePictureUrl, setProfilePictureUrl] = useState(null);

  const [stats, setStats] = useState({
    totalStudents: 0,
    totalCourses: 0,
    totalAssignments: 0,
    totalQuizzes: 0,
    averageRating: 0,
    yearsTeaching: 0,
    totalRatings: 0
  });

  useEffect(() => {
    if (user) {
      fetchProfileData();
      fetchTeacherStats();
      fetchTeacherRatings();
    }
  }, [user]);

  // Listen for rating updates
  useEffect(() => {
    const handleRatingUpdate = () => {
      if (user) {
        fetchTeacherStats();
        fetchTeacherRatings();
      }
    };

    window.addEventListener('teacherRatingUpdated', handleRatingUpdate);
    return () => window.removeEventListener('teacherRatingUpdated', handleRatingUpdate);
  }, [user]);

  const fetchProfileData = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/teacher/reports/profile/${user.id}`);
      if (response.ok) {
        const data = await response.json();
        setProfileData({
          full_name: data.full_name || '',
          email: data.email || '',
          phone: data.phone || '',
          bio: data.bio || '',
          location: data.location || '',
          department: data.department || '',
          specialization: data.specialization || '',
          experience_years: data.experience_years || '',
          education: data.education || '',
          linkedin_url: data.linkedin_url || '',
          website_url: data.website_url || ''
        });
        setProfilePictureUrl(data.profile_picture);
      } else {
        // Use user data as fallback
        setProfileData(prev => ({
          ...prev,
          full_name: user.full_name || '',
          email: user.email || ''
        }));
        setProfilePictureUrl(user.profile_picture);
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
      setProfileData(prev => ({
        ...prev,
        full_name: user.full_name || '',
        email: user.email || ''
      }));
    }
  };

  const fetchTeacherStats = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/teacher/reports/stats/${user.id}`);
      if (response.ok) {
        const data = await response.json();
        setStats({
          totalStudents: data.totalStudents || 0,
          totalCourses: data.totalCourses || 0,
          totalAssignments: data.totalAssignments || 0,
          totalQuizzes: data.totalQuizzes || 0,
          averageRating: data.averageRating || 0,
          yearsTeaching: data.yearsTeaching || 0,
          totalRatings: data.totalRatings || 0
        });
      } else {
        console.error('Failed to fetch teacher stats');
        setStats({
          totalStudents: 0,
          totalCourses: 0,
          totalAssignments: 0,
          totalQuizzes: 0,
          averageRating: 0,
          yearsTeaching: 0,
          totalRatings: 0
        });
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
      setStats({
        totalStudents: 0,
        totalCourses: 0,
        totalAssignments: 0,
        totalQuizzes: 0,
        averageRating: 0,
        yearsTeaching: 0,
        totalRatings: 0
      });
    }
  };

  const handleSaveProfile = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/teacher/reports/profile/${user.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(profileData)
      });

      if (response.ok) {
        toast.success('Profile updated successfully!');
        setIsEditing(false);
        // Update auth context if needed
        if (updateProfile) {
          updateProfile({ full_name: profileData.full_name });
        }
      } else {
        throw new Error('Failed to update profile');
      }
    } catch (error) {
      console.error('Error updating profile:', error);
      toast.error('Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const fetchTeacherRatings = async () => {
    try {
      // Fetch rating summary
      const summaryResponse = await fetch(`http://localhost:8000/api/teacher-ratings/teacher/${user.id}/summary`);
      if (summaryResponse.ok) {
        const summary = await summaryResponse.json();
        setRatingSummary(summary);
      }

      // Fetch recent ratings
      const ratingsResponse = await fetch(`http://localhost:8000/api/teacher-ratings/teacher/${user.id}?limit=5`);
      if (ratingsResponse.ok) {
        const ratingsData = await ratingsResponse.json();
        setRatings(ratingsData);
      }
    } catch (error) {
      console.error('Error fetching teacher ratings:', error);
    }
  };

  const handleChangePassword = async () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      toast.error('New passwords do not match');
      return;
    }

    if (passwordData.newPassword.length < 6) {
      toast.error('Password must be at least 6 characters long');
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/auth/change-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: user.id,
          current_password: passwordData.currentPassword,
          new_password: passwordData.newPassword
        })
      });

      if (response.ok) {
        toast.success('Password changed successfully!');
        setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
        setShowPasswordForm(false);
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to change password');
      }
    } catch (error) {
      console.error('Error changing password:', error);
      toast.error(error.message || 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSettings = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/teacher/settings/${user.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
      });

      if (response.ok) {
        toast.success('Settings saved successfully!');
      } else {
        throw new Error('Failed to save settings');
      }
    } catch (error) {
      console.error('Error saving settings:', error);
      toast.error('Failed to save settings');
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, icon: Icon, color }) => (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-white rounded-xl shadow-lg p-6 border border-gray-100"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        </div>
        <div className={`p-3 rounded-lg ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </motion.div>
  );

  const tabs = [
    { id: 'profile', label: 'Profile Information', icon: User },
    { id: 'ratings', label: 'Student Ratings', icon: Star },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'settings', label: 'Preferences', icon: Settings }
  ];

  return (
    <TeacherDashboardLayout>
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
          <div className="flex items-center space-x-6">
            <ProfilePictureUpload
              currentPictureUrl={profilePictureUrl}
              onPictureUpdate={setProfilePictureUrl}
              size="xlarge"
            />
            
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {profileData.full_name || 'Teacher Name'}
              </h1>
              <p className="text-gray-600 mb-1">{profileData.department || 'Department'}</p>
              <p className="text-gray-500">{profileData.specialization || 'Specialization'}</p>
              <div className="flex items-center space-x-4 mt-3">
                <div className="flex items-center space-x-1 text-yellow-500">
                  <Award className="w-4 h-4" />
                  <span className="font-medium">{stats.averageRating}/5.0</span>
                  <span className="text-gray-500 text-sm">({stats.totalRatings} reviews)</span>
                </div>
                <div className="flex items-center space-x-1 text-gray-500">
                  <Calendar className="w-4 h-4" />
                  <span>{stats.yearsTeaching} years teaching</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
          <StatCard
            title="Total Students"
            value={stats.totalStudents}
            icon={User}
            color="bg-blue-500"
          />
          <StatCard
            title="Courses Teaching"
            value={stats.totalCourses}
            icon={BookOpen}
            color="bg-green-500"
          />
          <StatCard
            title="Assignments Created"
            value={stats.totalAssignments}
            icon={Edit3}
            color="bg-purple-500"
          />
          <StatCard
            title="Quizzes Created"
            value={stats.totalQuizzes}
            icon={FileText}
            color="bg-indigo-500"
          />
          <StatCard
            title="Average Rating"
            value={`${stats.averageRating}/5.0`}
            icon={Award}
            color="bg-yellow-500"
          />
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-2xl shadow-lg">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-8">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              ))}
            </nav>
          </div>

          <div className="p-8">
            {activeTab === 'profile' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">Profile Information</h3>
                  <button
                    onClick={() => setIsEditing(!isEditing)}
                    className="flex items-center space-x-2 text-blue-600 hover:text-blue-700"
                  >
                    <Edit3 className="w-4 h-4" />
                    <span>{isEditing ? 'Cancel' : 'Edit Profile'}</span>
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
                    <input
                      type="text"
                      value={profileData.full_name}
                      onChange={(e) => setProfileData({...profileData, full_name: e.target.value})}
                      disabled={!isEditing}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                    <input
                      type="email"
                      value={profileData.email}
                      onChange={(e) => setProfileData({...profileData, email: e.target.value})}
                      disabled={!isEditing}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Phone</label>
                    <input
                      type="tel"
                      value={profileData.phone}
                      onChange={(e) => setProfileData({...profileData, phone: e.target.value})}
                      disabled={!isEditing}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
                    <input
                      type="text"
                      value={profileData.location}
                      onChange={(e) => setProfileData({...profileData, location: e.target.value})}
                      disabled={!isEditing}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Department</label>
                    <input
                      type="text"
                      value={profileData.department}
                      onChange={(e) => setProfileData({...profileData, department: e.target.value})}
                      disabled={!isEditing}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Specialization</label>
                    <input
                      type="text"
                      value={profileData.specialization}
                      onChange={(e) => setProfileData({...profileData, specialization: e.target.value})}
                      disabled={!isEditing}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Bio</label>
                  <textarea
                    value={profileData.bio}
                    onChange={(e) => setProfileData({...profileData, bio: e.target.value})}
                    disabled={!isEditing}
                    rows={4}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
                    placeholder="Tell us about yourself, your teaching philosophy, and experience..."
                  />
                </div>

                {isEditing && (
                  <div className="flex items-center justify-end space-x-4">
                    <button
                      onClick={() => setIsEditing(false)}
                      className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSaveProfile}
                      disabled={loading}
                      className="flex items-center space-x-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                    >
                      <Save className="w-4 h-4" />
                      <span>{loading ? 'Saving...' : 'Save Changes'}</span>
                    </button>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'ratings' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-gray-900">Student Ratings & Reviews</h3>

                {/* Rating Summary */}
                {ratingSummary && (
                  <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg p-6 border border-yellow-200">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h4 className="text-xl font-bold text-gray-900">
                          {ratingSummary.average_rating}/5.0
                        </h4>
                        <p className="text-gray-600">
                          Based on {ratingSummary.total_ratings} reviews
                        </p>
                      </div>
                      <div className="flex items-center space-x-1">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <Star
                            key={star}
                            className={`w-6 h-6 ${
                              star <= Math.round(ratingSummary.average_rating)
                                ? 'text-yellow-400 fill-current'
                                : 'text-gray-300'
                            }`}
                          />
                        ))}
                      </div>
                    </div>

                    {/* Rating Distribution */}
                    <div className="space-y-2">
                      {[5, 4, 3, 2, 1].map((rating) => (
                        <div key={rating} className="flex items-center space-x-3">
                          <span className="text-sm font-medium w-8">{rating}★</span>
                          <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-yellow-400 h-2 rounded-full transition-all duration-300"
                              style={{
                                width: `${ratingSummary.total_ratings > 0
                                  ? (ratingSummary.rating_distribution[rating.toString()] / ratingSummary.total_ratings) * 100
                                  : 0}%`
                              }}
                            ></div>
                          </div>
                          <span className="text-sm text-gray-600 w-8">
                            {ratingSummary.rating_distribution[rating.toString()] || 0}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Recent Reviews */}
                <div>
                  <h4 className="text-lg font-medium text-gray-900 mb-4">Recent Reviews</h4>
                  {ratings.length > 0 ? (
                    <div className="space-y-4">
                      {ratings.map((rating) => (
                        <div key={rating.id} className="bg-white border border-gray-200 rounded-lg p-4">
                          <div className="flex items-start justify-between mb-2">
                            <div>
                              <div className="flex items-center space-x-2 mb-1">
                                <span className="font-medium text-gray-900">{rating.student_name}</span>
                                <span className="text-gray-500">•</span>
                                <span className="text-sm text-gray-600">{rating.course_title}</span>
                              </div>
                              <div className="flex items-center space-x-1">
                                {[1, 2, 3, 4, 5].map((star) => (
                                  <Star
                                    key={star}
                                    className={`w-4 h-4 ${
                                      star <= rating.rating
                                        ? 'text-yellow-400 fill-current'
                                        : 'text-gray-300'
                                    }`}
                                  />
                                ))}
                              </div>
                            </div>
                            <span className="text-sm text-gray-500">
                              {new Date(rating.created_at).toLocaleDateString()}
                            </span>
                          </div>
                          {rating.review && (
                            <p className="text-gray-700 text-sm mt-2">{rating.review}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <Star className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                      <p>No reviews yet</p>
                      <p className="text-sm">Students can rate you after enrolling in your courses</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'security' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-gray-900">Security Settings</h3>
                
                <div className="bg-gray-50 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h4 className="font-medium text-gray-900">Password</h4>
                      <p className="text-sm text-gray-600">Change your account password</p>
                    </div>
                    <button
                      onClick={() => setShowPasswordForm(!showPasswordForm)}
                      className="text-blue-600 hover:text-blue-700 font-medium"
                    >
                      {showPasswordForm ? 'Cancel' : 'Change Password'}
                    </button>
                  </div>

                  {showPasswordForm && (
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Current Password</label>
                        <div className="relative">
                          <input
                            type={showPasswords.current ? 'text' : 'password'}
                            value={passwordData.currentPassword}
                            onChange={(e) => setPasswordData({...passwordData, currentPassword: e.target.value})}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-12"
                          />
                          <button
                            type="button"
                            onClick={() => setShowPasswords({...showPasswords, current: !showPasswords.current})}
                            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                          >
                            {showPasswords.current ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                          </button>
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">New Password</label>
                        <div className="relative">
                          <input
                            type={showPasswords.new ? 'text' : 'password'}
                            value={passwordData.newPassword}
                            onChange={(e) => setPasswordData({...passwordData, newPassword: e.target.value})}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-12"
                          />
                          <button
                            type="button"
                            onClick={() => setShowPasswords({...showPasswords, new: !showPasswords.new})}
                            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                          >
                            {showPasswords.new ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                          </button>
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Confirm New Password</label>
                        <div className="relative">
                          <input
                            type={showPasswords.confirm ? 'text' : 'password'}
                            value={passwordData.confirmPassword}
                            onChange={(e) => setPasswordData({...passwordData, confirmPassword: e.target.value})}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-12"
                          />
                          <button
                            type="button"
                            onClick={() => setShowPasswords({...showPasswords, confirm: !showPasswords.confirm})}
                            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                          >
                            {showPasswords.confirm ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                          </button>
                        </div>
                      </div>

                      <button
                        onClick={handleChangePassword}
                        disabled={loading}
                        className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                      >
                        {loading ? 'Changing Password...' : 'Change Password'}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'settings' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-gray-900">Notification Preferences</h3>
                
                <div className="space-y-4">
                  {Object.entries({
                    emailNotifications: 'Email Notifications',
                    pushNotifications: 'Push Notifications',
                    weeklyReports: 'Weekly Reports',
                    studentMessages: 'Student Messages',
                    assignmentReminders: 'Assignment Reminders'
                  }).map(([key, label]) => (
                    <div key={key} className="flex items-center justify-between py-3 border-b border-gray-200">
                      <div>
                        <h4 className="font-medium text-gray-900">{label}</h4>
                        <p className="text-sm text-gray-600">Receive {label.toLowerCase()}</p>
                      </div>
                      <button
                        onClick={() => setSettings({...settings, [key]: !settings[key]})}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          settings[key] ? 'bg-blue-600' : 'bg-gray-200'
                        }`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            settings[key] ? 'translate-x-6' : 'translate-x-1'
                          }`}
                        />
                      </button>
                    </div>
                  ))}
                </div>

                <div className="pt-6">
                  <button
                    onClick={handleSaveSettings}
                    disabled={loading}
                    className="flex items-center space-x-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    <Save className="w-4 h-4" />
                    <span>{loading ? 'Saving...' : 'Save Settings'}</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
        </div>
      </div>
    </TeacherDashboardLayout>
  );
};

export default TeacherProfile;
