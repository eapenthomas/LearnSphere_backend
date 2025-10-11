import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Edit,
  Trash2,
  Calendar,
  Users,
  Eye,
  MoreVertical,
  BookOpen,
  Clock
} from 'lucide-react';
import { getThumbnailUrl, getFallbackThumbnail } from '../utils/thumbnailUtils.jsx';

const CourseCard = ({ course, onEdit, onDelete, onView }) => {
  const [showMenu, setShowMenu] = useState(false);

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getStatusBadge = (status) => {
    const baseClasses = "px-3 py-1 rounded-full text-body-sm font-medium";

    switch (status) {
      case 'active':
        return `${baseClasses} bg-success-50 text-success-600 border border-success-500`;
      case 'draft':
        return `${baseClasses} bg-warning-50 text-warning-600 border border-warning-500`;
      default:
        return `${baseClasses} bg-background-tertiary text-text-secondary border border-border-primary`;
    }
  };

  const truncateText = (text, maxLength = 120) => {
    if (!text) return '';
    return text.length > maxLength ? `${text.substring(0, maxLength)}...` : text;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -8, scale: 1.02 }}
      className="bg-background-secondary rounded-lg shadow-elegant hover:shadow-elegant-xl transition-all duration-300 overflow-hidden group border border-border-primary"
    >
      {/* Thumbnail */}
      <div className="relative aspect-video bg-gradient-to-br from-primary-100 to-secondary-100 overflow-hidden">
        {course.thumbnail_url ? (
          <img
            src={getThumbnailUrl(course)}
            alt={course.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            onError={(e) => {
              // If image fails to load, show fallback
              e.target.style.display = 'none';
              const fallback = e.target.nextElementSibling;
              if (fallback) fallback.style.display = 'flex';
            }}
          />
        ) : null}
        <div className="w-full h-full flex items-center justify-center" style={{ display: course.thumbnail_url ? 'none' : 'flex' }}>
          <BookOpen className="w-12 h-12 text-primary-500" />
        </div>
        
        {/* Status Badge */}
        <div className="absolute top-3 left-3">
          <span className={getStatusBadge(course.status)}>
            {course.status === 'active' ? 'Active' : 'Draft'}
          </span>
        </div>

        {/* Action Menu */}
        <div className="absolute top-3 right-3">
          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="p-2 bg-white/90 backdrop-blur-sm rounded-full shadow-md hover:bg-white transition-colors duration-200"
            >
              <MoreVertical className="w-4 h-4 text-gray-600" />
            </button>

            {showMenu && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95, y: -10 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg border border-gray-100 py-2 z-10"
              >
                <button
                  onClick={() => {
                    onView(course);
                    setShowMenu(false);
                  }}
                  className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2 transition-colors"
                >
                  <Eye className="w-4 h-4 text-gray-500" />
                  <span>View Course</span>
                </button>
                <button
                  onClick={() => {
                    onEdit(course);
                    setShowMenu(false);
                  }}
                  className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-2 transition-colors"
                >
                  <Edit className="w-4 h-4 text-blue-500" />
                  <span>Edit Course</span>
                </button>
                <button
                  onClick={() => {
                    onDelete(course);
                    setShowMenu(false);
                  }}
                  className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center space-x-2 transition-colors"
                >
                  <Trash2 className="w-4 h-4 text-red-500" />
                  <span>Delete Course</span>
                </button>
              </motion.div>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {/* Title */}
        <h3 className="text-lg font-semibold text-indigo-700 mb-2 line-clamp-2 group-hover:text-indigo-800 transition-colors">
          {course.title}
        </h3>

        {/* Description */}
        <p className="text-sm text-indigo-900/80 mb-4 line-clamp-3">
          {truncateText(course.description) || 'No description provided'}
        </p>

        {/* Footer */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-100">
          <div className="flex items-center space-x-4 text-xs text-gray-500">
            <div className="flex items-center space-x-1">
              <Calendar className="w-3 h-3" />
              <span>{formatDate(course.created_at)}</span>
            </div>
            <div className="flex items-center space-x-1">
              <Users className="w-3 h-3" />
              <span>{course.enrollment_count || 0} student{(course.enrollment_count || 0) !== 1 ? 's' : ''}</span>
              {/* Debug: Show enrollment count in console */}
              {console.log(`CourseCard - ${course.title}: enrollment_count = ${course.enrollment_count}`)}
            </div>
          </div>
          
          <div className="flex items-center space-x-1 text-xs text-gray-500">
            <Clock className="w-3 h-3" />
            <span>Updated {formatDate(course.created_at)}</span>
          </div>
        </div>
      </div>

      {/* Click outside to close menu */}
      {showMenu && (
        <div
          className="fixed inset-0 z-0"
          onClick={() => setShowMenu(false)}
        />
      )}
    </motion.div>
  );
};

export default CourseCard;
