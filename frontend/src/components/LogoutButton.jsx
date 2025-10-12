import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext.jsx';
import { LogOut, AlertTriangle } from 'lucide-react';

const LogoutButton = ({ 
  variant = 'default', 
  size = 'md', 
  showText = true, 
  className = '',
  onLogoutStart,
  onLogoutComplete 
}) => {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [showConfirm, setShowConfirm] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);

  const handleLogoutClick = () => {
    setShowConfirm(true);
    if (onLogoutStart) onLogoutStart();
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
        navigate('/login', { replace: true });
      }
    } catch (error) {
      console.error('Logout error:', error);
      navigate('/login', { replace: true });
    } finally {
      setLoggingOut(false);
      setShowConfirm(false);
      if (onLogoutComplete) onLogoutComplete();
    }
  };

  const handleLogoutCancel = () => {
    setShowConfirm(false);
  };

  // Button variants
  const variants = {
    default: 'text-gray-600 hover:text-red-600 hover:bg-red-50',
    danger: 'text-red-600 hover:text-red-700 hover:bg-red-50',
    ghost: 'text-gray-500 hover:text-gray-700 hover:bg-gray-100',
    solid: 'bg-red-600 text-white hover:bg-red-700'
  };

  // Button sizes
  const sizes = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-2 text-sm',
    lg: 'px-4 py-3 text-base'
  };

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5'
  };

  return (
    <>
      <button
        onClick={handleLogoutClick}
        disabled={loggingOut}
        className={`
          flex items-center space-x-2 rounded-lg transition-all duration-200 font-medium
          ${variants[variant]} ${sizes[size]} ${className}
          disabled:opacity-50 disabled:cursor-not-allowed
        `}
        title="Logout (Ctrl+Shift+L)"
      >
        <LogOut className={iconSizes[size]} />
        {showText && <span>Logout</span>}
      </button>

      {/* Logout Confirmation Modal */}
      <AnimatePresence>
        {showConfirm && (
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
              className="bg-white shadow rounded-xl p-4 border border-gray-200 max-w-md w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2 bg-red-100 rounded-full">
                  <AlertTriangle className="w-6 h-6 text-red-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900">Confirm Logout</h3>
              </div>
              
              <p className="text-gray-600 mb-6">
                Are you sure you want to logout? You'll need to sign in again to access your dashboard.
              </p>
              
              <div className="flex space-x-3">
                <button
                  onClick={handleLogoutCancel}
                  disabled={loggingOut}
                  className="btn-secondary flex-1 disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleLogoutConfirm}
                  disabled={loggingOut}
                  className="btn-danger flex-1 disabled:opacity-50 flex items-center justify-center space-x-2"
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
    </>
  );
};

export default LogoutButton;
