import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext.jsx';
import { toast } from 'react-hot-toast';
import {
  Star,
  X,
  Send,
  Edit3,
  Trash2
} from 'lucide-react';

const TeacherRatingModal = ({ isOpen, onClose, teacher, course }) => {
  const { user } = useAuth();
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [review, setReview] = useState('');
  const [loading, setLoading] = useState(false);
  const [existingRating, setExistingRating] = useState(null);

  useEffect(() => {
    if (isOpen && teacher && course && user) {
      fetchExistingRating();
    }
  }, [isOpen, teacher, course, user]);

  const fetchExistingRating = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/teacher-ratings/student/${user.id}/rating/${teacher.id}/${course.id}`
      );
      
      if (response.ok) {
        const data = await response.json();
        if (data) {
          setExistingRating(data);
          setRating(data.rating);
          setReview(data.review || '');
        }
      }
    } catch (error) {
      console.error('Error fetching existing rating:', error);
    }
  };

  const handleSubmit = async () => {
    if (rating === 0) {
      toast.error('Please select a rating');
      return;
    }

    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/teacher-ratings/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          teacher_id: teacher.id,
          student_id: user.id,
          course_id: course.id,
          rating: rating,
          review: review.trim() || null
        })
      });

      if (response.ok) {
        const data = await response.json();
        toast.success(data.message);
        onClose();
        // Refresh the page or emit an event to update teacher ratings
        window.dispatchEvent(new CustomEvent('teacherRatingUpdated'));
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to submit rating');
      }
    } catch (error) {
      console.error('Error submitting rating:', error);
      toast.error(error.message || 'Failed to submit rating');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!existingRating) return;

    try {
      setLoading(true);
      const response = await fetch(
        `http://localhost:8000/api/teacher-ratings/${existingRating.id}?student_id=${user.id}`,
        { method: 'DELETE' }
      );

      if (response.ok) {
        toast.success('Rating deleted successfully');
        setRating(0);
        setReview('');
        setExistingRating(null);
        onClose();
        window.dispatchEvent(new CustomEvent('teacherRatingUpdated'));
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to delete rating');
      }
    } catch (error) {
      console.error('Error deleting rating:', error);
      toast.error(error.message || 'Failed to delete rating');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setRating(0);
    setHoverRating(0);
    setReview('');
    setExistingRating(null);
    onClose();
  };

  if (!teacher || !course) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="bg-white rounded-2xl shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  {existingRating ? 'Update Rating' : 'Rate Teacher'}
                </h3>
                <p className="text-sm text-gray-600">
                  {teacher.name} • {course.title}
                </p>
              </div>
              <button
                onClick={handleClose}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6 space-y-6">
              {/* Star Rating */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">
                  Your Rating
                </label>
                <div className="flex items-center space-x-1">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      onClick={() => setRating(star)}
                      onMouseEnter={() => setHoverRating(star)}
                      onMouseLeave={() => setHoverRating(0)}
                      className="p-1 transition-transform hover:scale-110"
                    >
                      <Star
                        className={`w-8 h-8 ${
                          star <= (hoverRating || rating)
                            ? 'text-yellow-400 fill-current'
                            : 'text-gray-300'
                        } transition-colors`}
                      />
                    </button>
                  ))}
                </div>
                {rating > 0 && (
                  <p className="text-sm text-gray-600 mt-2">
                    {rating === 1 && 'Poor'}
                    {rating === 2 && 'Fair'}
                    {rating === 3 && 'Good'}
                    {rating === 4 && 'Very Good'}
                    {rating === 5 && 'Excellent'}
                  </p>
                )}
              </div>

              {/* Review Text */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Review (Optional)
                </label>
                <textarea
                  value={review}
                  onChange={(e) => setReview(e.target.value)}
                  placeholder="Share your experience with this teacher..."
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  maxLength={500}
                />
                <p className="text-xs text-gray-500 mt-1">
                  {review.length}/500 characters
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-between pt-4">
                {existingRating && (
                  <button
                    onClick={handleDelete}
                    disabled={loading}
                    className="flex items-center space-x-2 px-4 py-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
                  >
                    <Trash2 className="w-4 h-4" />
                    <span>Delete</span>
                  </button>
                )}
                
                <div className="flex items-center space-x-3 ml-auto">
                  <button
                    onClick={handleClose}
                    className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSubmit}
                    disabled={loading || rating === 0}
                    className="flex items-center space-x-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {existingRating ? <Edit3 className="w-4 h-4" /> : <Send className="w-4 h-4" />}
                    <span>{loading ? 'Saving...' : existingRating ? 'Update' : 'Submit'}</span>
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};

export default TeacherRatingModal;
