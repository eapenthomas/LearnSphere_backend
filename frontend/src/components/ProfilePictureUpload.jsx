import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext.jsx';
import { toast } from 'react-hot-toast';
import {
  Camera,
  Upload,
  Trash2,
  User,
  Loader
} from 'lucide-react';

const ProfilePictureUpload = ({ currentPictureUrl, onPictureUpdate, size = 'large' }) => {
  const { user } = useAuth();
  const [uploading, setUploading] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [localPictureUrl, setLocalPictureUrl] = useState(currentPictureUrl);
  const fileInputRef = useRef(null);

  const sizeClasses = {
    small: 'w-12 h-12',
    medium: 'w-20 h-20',
    large: 'w-24 h-24',
    xlarge: 'w-32 h-32'
  };

  const iconSizes = {
    small: 'w-3 h-3',
    medium: 'w-4 h-4',
    large: 'w-5 h-5',
    xlarge: 'w-6 h-6'
  };

  // Fetch user's current profile picture on component mount
  useEffect(() => {
    const fetchProfilePicture = async () => {
      if (user?.id && !localPictureUrl) {
        try {
          const response = await fetch(`http://localhost:8000/api/profile-pictures/${user.id}`);
          if (response.ok) {
            const data = await response.json();
            if (data.profile_picture_url) {
              setLocalPictureUrl(data.profile_picture_url);
              if (onPictureUpdate) {
                onPictureUpdate(data.profile_picture_url);
              }
            }
          }
        } catch (error) {
          console.error('Error fetching profile picture:', error);
        }
      }
    };

    fetchProfilePicture();
  }, [user?.id, localPictureUrl, onPictureUpdate]);

  // Update local state when prop changes
  useEffect(() => {
    setLocalPictureUrl(currentPictureUrl);
  }, [currentPictureUrl]);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      handleUpload(file);
    }
  };

  const handleUpload = async (file) => {
    try {
      setUploading(true);

      // Validate file type
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
      if (!allowedTypes.includes(file.type)) {
        toast.error('Please select a valid image file (JPEG, PNG, GIF, or WebP)');
        return;
      }

      // Validate file size (5MB max)
      const maxSize = 5 * 1024 * 1024; // 5MB
      if (file.size > maxSize) {
        toast.error('File size must be less than 5MB');
        return;
      }

      const formData = new FormData();
      formData.append('file', file);
      formData.append('user_id', user.id);

      const response = await fetch('http://localhost:8000/api/profile-pictures/upload', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        toast.success(data.message);
        
        // Update the picture URL in parent component
        if (onPictureUpdate) {
          onPictureUpdate(data.profile_picture_url);
        }
        
        // Emit event for other components to update
        window.dispatchEvent(new CustomEvent('profilePictureUpdated', {
          detail: { profilePictureUrl: data.profile_picture_url }
        }));
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to upload profile picture');
      }
    } catch (error) {
      console.error('Error uploading profile picture:', error);
      toast.error(error.message || 'Failed to upload profile picture');
    } finally {
      setUploading(false);
      // Clear the file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDelete = async () => {
    if (!localPictureUrl) return;

    try {
      setDeleting(true);

      const response = await fetch(`http://localhost:8000/api/profile-pictures/${user.id}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        const data = await response.json();
        toast.success(data.message);
        
        // Update the picture URL in parent component
        if (onPictureUpdate) {
          onPictureUpdate(null);
        }
        
        // Emit event for other components to update
        window.dispatchEvent(new CustomEvent('profilePictureUpdated', {
          detail: { profilePictureUrl: null }
        }));
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to delete profile picture');
      }
    } catch (error) {
      console.error('Error deleting profile picture:', error);
      toast.error(error.message || 'Failed to delete profile picture');
    } finally {
      setDeleting(false);
    }
  };

  const getInitials = () => {
    if (user?.full_name) {
      return user.full_name.split(' ').map(name => name.charAt(0)).join('').toUpperCase().slice(0, 2);
    }
    if (user?.email) {
      return user.email.charAt(0).toUpperCase();
    }
    return 'U';
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleUpload(files[0]);
    }
  };

  return (
    <div className="relative">
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        className="hidden"
      />
      
      <div
        className={`relative ${sizeClasses[size]} rounded-full overflow-hidden border-4 border-white shadow-lg cursor-pointer group`}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={(e) => {
          // Only trigger file input if clicking on the image area, not buttons
          if (e.target === e.currentTarget || e.target.tagName === 'IMG' || e.target.tagName === 'DIV') {
            fileInputRef.current?.click();
          }
        }}
      >
        {localPictureUrl ? (
          <img
            src={localPictureUrl}
            alt="Profile"
            className="w-full h-full object-cover"
            onError={(e) => {
              console.error('Failed to load profile picture:', localPictureUrl);
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg">
            {uploading ? (
              <Loader className={`${iconSizes[size]} animate-spin`} />
            ) : (
              getInitials()
            )}
          </div>
        )}
        
        {/* Fallback for broken images */}
        <div
          className="w-full h-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg"
          style={{ display: localPictureUrl ? 'none' : 'flex' }}
        >
          {uploading ? (
            <Loader className={`${iconSizes[size]} animate-spin`} />
          ) : (
            getInitials()
          )}
        </div>
        
        {/* Hover overlay */}
        <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
          {uploading ? (
            <Loader className={`${iconSizes[size]} text-white animate-spin`} />
          ) : (
            <Camera className={`${iconSizes[size]} text-white`} />
          )}
        </div>
      </div>

      {/* Action buttons */}
      {size === 'large' || size === 'xlarge' ? (
        <div className="absolute -bottom-2 -right-2 flex space-x-1">
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={(e) => {
              e.stopPropagation();
              fileInputRef.current?.click();
            }}
            disabled={uploading}
            className="bg-blue-600 text-white p-2 rounded-full hover:bg-blue-700 transition-colors shadow-lg disabled:opacity-50"
            title="Upload new picture"
          >
            {uploading ? (
              <Loader className="w-3 h-3 animate-spin" />
            ) : (
              <Upload className="w-3 h-3" />
            )}
          </motion.button>
          
          {localPictureUrl && (
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={(e) => {
                e.stopPropagation();
                handleDelete();
              }}
              disabled={deleting}
              className="bg-red-600 text-white p-2 rounded-full hover:bg-red-700 transition-colors shadow-lg disabled:opacity-50"
              title="Delete picture"
            >
              {deleting ? (
                <Loader className="w-3 h-3 animate-spin" />
              ) : (
                <Trash2 className="w-3 h-3" />
              )}
            </motion.button>
          )}
        </div>
      ) : (
        <div className="absolute -bottom-1 -right-1">
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={(e) => {
              e.stopPropagation();
              fileInputRef.current?.click();
            }}
            disabled={uploading}
            className="bg-blue-600 text-white p-1 rounded-full hover:bg-blue-700 transition-colors shadow-lg disabled:opacity-50"
            title="Change picture"
          >
            {uploading ? (
              <Loader className="w-2 h-2 animate-spin" />
            ) : (
              <Camera className="w-2 h-2" />
            )}
          </motion.button>
        </div>
      )}
    </div>
  );
};

export default ProfilePictureUpload;
