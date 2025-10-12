import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext.jsx';
import DashboardLayout from '../components/DashboardLayout.jsx';
import ProfileInformation from '../components/ProfileInformation.jsx';
import PasswordUpdate from '../components/PasswordUpdate.jsx';
import LoadingSkeleton from '../components/LoadingSkeleton.jsx';
import { createClient } from '@supabase/supabase-js';
import { toast, Toaster } from 'react-hot-toast';
import {
  UserCheck,
  ChevronRight,
  Home,
  User,
  Lock,
  Shield,
  Settings
} from 'lucide-react';

// Initialize Supabase client
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;
const supabase = createClient(supabaseUrl, supabaseAnonKey);

const ProfilePage = () => {
  const { user } = useAuth();
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Immediately set fallback data if user is available
  useEffect(() => {
    if (user && !profileData) {
      console.log('Setting immediate fallback profile data');
      setProfileData({
        id: user.id,
        full_name: user.fullName || '',
        email: user.email || '',
        role: user.role || 'student',
        phone: ''
      });
      setLoading(false);
    }
  }, [user, profileData]);

  // Try to enhance profile data from database (optional)
  useEffect(() => {
    const enhanceProfileData = async () => {
      if (!user?.id || !profileData) {
        return;
      }

      try {
        console.log('Trying to enhance profile data from database');

        // Check if Supabase is configured
        if (!supabaseUrl || !supabaseAnonKey) {
          console.log('Supabase not configured, skipping database fetch');
          return;
        }

        // Try to fetch additional data from database
        const { data, error } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', user.id)
          .single();

        if (!error && data) {
          console.log('Enhanced profile data from database:', data);
          setProfileData(prev => ({
            ...prev,
            ...data,
            email: user.email || data.email // Keep auth email as primary
          }));
          setError(null);
        } else {
          console.log('Database profile not found, keeping session data');
        }
      } catch (err) {
        console.log('Database enhancement failed, keeping session data:', err);
      }
    };

    // Only try to enhance after initial data is set
    if (profileData && !error) {
      enhanceProfileData();
    }
  }, [user, profileData]);

  const handleProfileUpdate = (updatedData) => {
    setProfileData(prev => ({ ...prev, ...updatedData }));
  };

  if (loading) {
    return (
      <DashboardLayout>
        <LoadingSkeleton />
      </DashboardLayout>
    );
  }

  // If no profile data and not loading, something went wrong
  if (!profileData) {
    console.error('No profile data available and not loading');
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="text-red-500 text-6xl mb-4">⚠️</div>
            <h2 className="text-2xl font-bold text-blue-800 mb-2">Unable to Load Profile</h2>
            <p className="text-gray-600 mb-4">There was an issue loading your profile data.</p>
            <button
              onClick={() => window.location.reload()}
              className="btn-primary"
            >
              Retry
            </button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#fff',
            color: '#374151',
            boxShadow: '0 10px 25px -3px rgba(255, 255, 255, 0.1), 0 4px 6px -2px rgba(255, 255, 255, 0.05)',
            border: '1px solid #e5e7eb',
            borderRadius: '12px',
            padding: '16px',
          },
          success: {
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
      
      <div className="space-y-6">
        {/* Breadcrumb Navigation */}
        <motion.nav
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center space-x-2 text-sm text-gray-600"
        >
          <Home className="w-4 h-4" />
          <span>Dashboard</span>
          <ChevronRight className="w-4 h-4" />
          <span className="text-gray-800 font-medium">Profile & Settings</span>
        </motion.nav>

        {/* Page Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center space-x-4"
        >
          <div className="p-3 bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl">
            <UserCheck className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-extrabold text-black tracking-tight">
              Profile & Settings
            </h1>
            <p className="text-black font-medium">
              Manage your account information and security settings
            </p>
          </div>
        </motion.div>

        {/* Error Message */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-red-50 border border-red-200 rounded-lg p-4"
          >
            <p className="text-red-600 font-medium">{error}</p>
          </motion.div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mobile-grid">
          {/* Profile Information Card */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
          >
            <ProfileInformation 
              profileData={profileData}
              onUpdate={handleProfileUpdate}
            />
          </motion.div>

          {/* Password Update Card */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <PasswordUpdate />
          </motion.div>
        </div>

        {/* Additional Settings Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mobile-grid">
          {/* Security Settings Preview */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="card p-6 hover:shadow-xl transition-all duration-300"
          >
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-2 bg-green-100 rounded-lg">
                <Shield className="w-5 h-5 text-green-600" />
              </div>
              <h3 className="text-lg font-bold text-white">Security Overview</h3>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-white">Two-Factor Authentication</span>
                <span className="text-sm text-white">Not enabled</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-white">Login Sessions</span>
                <span className="text-sm text-white">1 active</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-white">Last Password Change</span>
                <span className="text-sm text-white">Never</span>
              </div>
            </div>
          </motion.div>

          {/* Account Preferences */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="card p-6 hover:shadow-xl transition-all duration-300"
          >
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Settings className="w-5 h-5 text-purple-600" />
              </div>
              <h3 className="text-lg font-bold text-white">Preferences</h3>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-white">Email Notifications</span>
                <span className="text-sm text-white">Enabled</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-white">Theme</span>
                <span className="text-sm text-white">Light</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-white">Language</span>
                <span className="text-sm text-white">English</span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default ProfilePage;
