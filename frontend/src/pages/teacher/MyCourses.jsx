import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext.jsx';
import TeacherDashboardLayout from '../../layouts/TeacherDashboardLayout.jsx';
import CourseCard from '../../components/CourseCard.jsx';
import CourseFormModal from '../../components/CourseFormModal.jsx';
import EnhancedCourseViewModal from '../../components/EnhancedCourseViewModal.jsx';
import { courseOperations } from '../../utils/supabaseClient.js';
import { toast } from 'react-hot-toast';
import {
  Plus,
  BookOpen,
  Search,
  Filter,
  Grid3X3,
  List,
  Loader,
  AlertCircle,
  Trash2,
  Eye,
  RefreshCw
} from 'lucide-react';

const TeacherMyCourses = () => {
  const { user } = useAuth();
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [viewMode, setViewMode] = useState('grid');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showViewModal, setShowViewModal] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [formLoading, setFormLoading] = useState(false);



  // Backend API fetch - primary method
  const fetchCoursesFromAPI = async () => {
    try {
      setLoading(true);
      console.log('=== BACKEND API FETCH ===');
      console.log('User ID:', user?.id);
      console.log('Fetching from:', `http://localhost:8000/api/courses/teacher/${user.id}`);

      if (!user?.id) {
        toast.error('User not authenticated');
        setLoading(false);
        return;
      }

      const response = await fetch(`http://localhost:8000/api/courses/teacher/${user.id}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      console.log('API Response status:', response.status);
      console.log('API Response headers:', response.headers);

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      console.log('API Result:', result);
      console.log('API Data:', result.data);

      if (result.success && result.data) {
        // Transform API data to match expected format
        const transformedCourses = result.data.map(course => ({
          id: course.id,
          title: course.title,
          description: course.description,
          code: course.code,
          status: 'active', // API doesn't return status, default to active
          created_at: course.created_at || new Date().toISOString(),
          teacher_id: user.id,
          enrollment_count: course.enrollment_count || 0, // Include enrollment count from API
          thumbnail_url: course.thumbnail_url // Include thumbnail URL
        }));

        console.log('Transformed courses with enrollment counts:', transformedCourses);
        
        // Debug: Log each course's enrollment count
        transformedCourses.forEach(course => {
          console.log(`Course: ${course.title} - Enrollment Count: ${course.enrollment_count}`);
        });
        
        setCourses(transformedCourses);
        toast.success(`Successfully loaded ${transformedCourses.length} courses with enrollment data!`);
      } else {
        console.log('No courses in API response');
        setCourses([]);
        toast.info('No courses found. Create your first course!');
      }
    } catch (error) {
      console.error('API fetch error:', error);
      toast.error(`Failed to load courses: ${error.message}`);
      setCourses([]);
    } finally {
      setLoading(false);
    }
  };

  // Fetch courses on component mount
  useEffect(() => {
    if (user?.id) {
      // Use API as primary method since it's working
      console.log('Component mounted, fetching courses via API...');
      fetchCoursesFromAPI();

      // Setup real-time subscription (optional)
      const cleanup = setupRealTimeSubscription();

      // Cleanup subscription on unmount
      return cleanup;
    }
  }, [user?.id]);

  const fetchCourses = async () => {
    const timeoutId = setTimeout(() => {
      console.error('Course fetch timeout - forcing loading to false');
      setLoading(false);
      toast.error('Request timed out. Please try again.');
    }, 10000); // 10 second timeout

    try {
      setLoading(true);
      console.log('=== COURSE FETCH DEBUG ===');
      console.log('Current user object:', user);
      console.log('User ID:', user?.id);
      console.log('User role:', user?.role);

      // Check if user exists
      if (!user?.id) {
        console.error('No user ID found');
        toast.error('User not authenticated');
        clearTimeout(timeoutId);
        setLoading(false);
        return;
      }

      console.log('Step 1: Testing Supabase connection...');
      // Test Supabase connection first with timeout
      const connectionPromise = courseOperations.supabase
        .from('courses')
        .select('count', { count: 'exact', head: true });

      const { data: testData, error: testError } = await Promise.race([
        connectionPromise,
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error('Connection test timeout')), 5000)
        )
      ]);

      if (testError) {
        console.error('Supabase connection test failed:', testError);
        toast.error('Database connection failed. Please check if the courses table exists.');
        clearTimeout(timeoutId);
        setLoading(false);
        return;
      }

      console.log('Step 2: Connection successful, total courses in DB:', testData);

      console.log('Step 3: Fetching teacher courses...');
      // Fetch teacher courses with timeout
      const fetchPromise = courseOperations.fetchTeacherCourses(user.id);
      const data = await Promise.race([
        fetchPromise,
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error('Fetch courses timeout')), 5000)
        )
      ]);

      console.log('Step 4: Courses fetched successfully:', data);
      setCourses(data || []);
      console.log('=== END COURSE FETCH DEBUG ===');

      // If no courses found, show a helpful message
      if (!data || data.length === 0) {
        console.log('No courses found for teacher. This is normal for new teachers.');
        toast.info('No courses found. Click "Create New Course" to get started!');
      } else {
        toast.success(`Loaded ${data.length} courses successfully!`);
      }

      clearTimeout(timeoutId);
    } catch (error) {
      console.error('Error fetching courses:', error);
      clearTimeout(timeoutId);

      if (error.message.includes('timeout')) {
        toast.error('Request timed out. Please check your internet connection and try again.');
      } else {
        toast.error(`Failed to load courses: ${error.message}`);
      }
      setCourses([]); // Set empty array on error
    } finally {
      setLoading(false);
    }
  };

  const setupRealTimeSubscription = () => {
    console.log('Setting up real-time subscription for user:', user.id);
    
    const subscription = courseOperations.subscribeToChanges(user.id, (payload) => {
      console.log('Real-time update received:', payload);
      
      switch (payload.eventType) {
        case 'INSERT':
          console.log('Real-time INSERT - Adding new course:', payload.new);
          setCourses(prev => {
            // Check if course already exists to avoid duplicates
            const exists = prev.find(course => course.id === payload.new.id);
            if (!exists) {
              console.log('Course added via real-time');
              return [payload.new, ...prev];
            }
            console.log('Course already exists, skipping duplicate');
            return prev;
          });
          break;
        case 'UPDATE':
          console.log('Real-time UPDATE - Updating course:', payload.new);
          setCourses(prev => {
            const updated = prev.map(course => 
              course.id === payload.new.id ? payload.new : course
            );
            console.log('Course updated via real-time');
            return updated;
          });
          break;
        case 'DELETE':
          console.log('Real-time DELETE - Deleting course:', payload.old);
          setCourses(prev => {
            const filtered = prev.filter(course => course.id !== payload.old.id);
            console.log('Course deleted via real-time, remaining:', filtered.length);
            return filtered;
          });
          break;
        default:
          console.log('Unknown real-time event:', payload.eventType);
      }
    });

    return () => {
      console.log('Unsubscribing from real-time updates');
      subscription.unsubscribe();
    };
  };

  const handleCreateCourse = async (formData) => {
    try {
      setFormLoading(true);

      console.log('=== COURSE CREATION VIA API ===');
      console.log('Creating course with form data:', formData);
      console.log('Current user:', user);

      // Validate required fields
      if (!user?.id) {
        throw new Error('User not authenticated');
      }

      if (!formData.title) {
        throw new Error('Course title is required');
      }

      // Generate a unique course code
      const courseCode = `COURSE_${Date.now()}_${Math.random().toString(36).substring(2, 7).toUpperCase()}`;

      // Prepare form data for multipart upload
      const apiFormData = new FormData();
      apiFormData.append('teacher_id', user.id);
      apiFormData.append('title', formData.title.trim());
      apiFormData.append('description', formData.description?.trim() || '');
      apiFormData.append('code', courseCode);
      apiFormData.append('status', formData.status || 'active');

      // Add thumbnail if provided
      if (formData.thumbnailFile) {
        apiFormData.append('thumbnail', formData.thumbnailFile);
        console.log('Adding thumbnail file:', formData.thumbnailFile.name);
      }

      console.log('Sending course data to API with thumbnail support');

      // Use the payment system API for course creation
      const response = await fetch('http://localhost:8000/api/teacher/create-course', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.accessToken}`
        },
        body: JSON.stringify({
          title: formData.title.trim(),
          description: formData.description?.trim() || '',
          is_paid: formData.is_paid || false,
          price: formData.price || 0
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `API request failed: ${response.status}`);
      }

      const result = await response.json();
      console.log('Course creation API result:', result);

      if (result.id && result.title) {
        // Add to local state - the API returns the course object directly
        setCourses(prev => [result, ...prev]);
        setShowCreateModal(false);
        toast.success('Course created successfully!');
        console.log('=== COURSE CREATION SUCCESS ===');
      } else {
        throw new Error('Invalid response format from server');
      }
    } catch (error) {
      console.error('=== COURSE CREATION ERROR ===');
      console.error('Error creating course:', error);
      toast.error(`Failed to create course: ${error.message}`);
    } finally {
      setFormLoading(false);
    }
  };

  const handleEditCourse = async (formData) => {
    try {
      setFormLoading(true);

      console.log('=== COURSE UPDATE VIA API ===');
      console.log('Updating course:', selectedCourse.id, 'with data:', formData);

      const updates = {
        title: formData.title.trim(),
        description: formData.description?.trim() || '',
        status: formData.status || 'active'
      };

      console.log('Sending update data to API:', updates);

      // Use backend API to update course
      const response = await fetch(`http://localhost:8000/api/courses/${selectedCourse.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `API request failed: ${response.status}`);
      }

      const result = await response.json();
      console.log('Course update API result:', result);

      let updatedCourse = result.data;

      // Handle thumbnail update separately if provided
      if (formData.thumbnailFile) {
        console.log('Updating course thumbnail...');

        const thumbnailFormData = new FormData();
        thumbnailFormData.append('thumbnail', formData.thumbnailFile);

        const thumbnailResponse = await fetch(`http://localhost:8000/api/courses/${selectedCourse.id}/thumbnail`, {
          method: 'PUT',
          body: thumbnailFormData
        });

        if (thumbnailResponse.ok) {
          const thumbnailResult = await thumbnailResponse.json();
          console.log('Thumbnail update result:', thumbnailResult);
          updatedCourse = thumbnailResult.data;
        } else {
          console.warn('Failed to update thumbnail, but course was updated successfully');
        }
      }

      if (result.success && updatedCourse) {
        // Update local state
        setCourses(prev => prev.map(course =>
          course.id === selectedCourse.id ? updatedCourse : course
        ));

        setShowEditModal(false);
        setSelectedCourse(null);
        toast.success('Course updated successfully!');
        console.log('=== COURSE UPDATE SUCCESS ===');
      } else {
        throw new Error(result.message || 'Failed to update course');
      }
    } catch (error) {
      console.error('=== COURSE UPDATE ERROR ===');
      console.error('Error updating course:', error);
      toast.error(`Failed to update course: ${error.message}`);
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteCourse = async () => {
    try {
      console.log('=== COURSE DELETE VIA API ===');
      console.log('Deleting course:', selectedCourse.id);

      // Store the course ID for immediate UI update
      const courseIdToDelete = selectedCourse.id;

      // Use backend API to delete course
      const response = await fetch(`http://localhost:8000/api/courses/${courseIdToDelete}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `API request failed: ${response.status}`);
      }

      const result = await response.json();
      console.log('Course delete API result:', result);

      if (result.success) {
        // Update local state
        setCourses(prev => {
          const updated = prev.filter(course => course.id !== courseIdToDelete);
          console.log('Updated courses after delete:', updated.length);
          return updated;
        });

        setShowDeleteModal(false);
        setSelectedCourse(null);
        toast.success('Course deleted successfully!');
        console.log('=== COURSE DELETE SUCCESS ===');
      } else {
        throw new Error(result.message || 'Failed to delete course');
      }
    } catch (error) {
      console.error('=== COURSE DELETE ERROR ===');
      console.error('Error deleting course:', error);
      toast.error(`Failed to delete course: ${error.message}`);
    }
  };

  const handleViewCourse = (course) => {
    console.log('View course:', course);
    setSelectedCourse(course);
    setShowViewModal(true);
  };

  // Filter courses based on search and status
  const filteredCourses = courses.filter(course => {
    const matchesSearch = course.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (course.description && course.description.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesStatus = statusFilter === 'all' || course.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusCount = (status) => {
    return courses.filter(course => status === 'all' || course.status === status).length;
  };

  return (
    <TeacherDashboardLayout>
      <div className="min-h-screen teacher-page-bg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-8">
            <div className="mb-4 lg:mb-0">
              <h1 className="text-heading-xl font-bold mb-2 font-serif" style={{color: '#000000'}}>My Courses</h1>
              <p className="text-body-lg" style={{color: '#000000'}}>
                Manage and organize your courses. You have {courses.length} course{courses.length !== 1 ? 's' : ''} total.
              </p>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={() => {
                  console.log('=== MANUAL REFRESH TRIGGERED ===');
                  console.log('User ID:', user?.id);
                  console.log('Current courses:', courses);
                  fetchCoursesFromAPI();
                }}
                disabled={loading}
                className="btn-primary px-4 py-3 border-2 border-border-primary rounded-lg transition-all duration-300 flex items-center space-x-2 font-medium"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>



              <button
                onClick={() => setShowCreateModal(true)}
                className="btn-primary px-6 py-3 rounded-lg font-semibold transition-all duration-300 flex items-center space-x-2 shadow-elegant hover:shadow-lg"
              >
                <Plus className="w-5 h-5" />
                <span>Create Course</span>
              </button>
            </div>
          </div>

          {/* Filters and Search */}
          <div className="bg-background-secondary rounded-lg shadow-elegant p-6 mb-8 border border-border-primary">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
              {/* Search */}
              <div className="relative flex-1 lg:max-w-md">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-text-secondary" />
                <input
                  type="text"
                  placeholder="Search courses..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="form-input pl-10"
                />
              </div>

              <div className="flex items-center space-x-4">
                {/* Status Filter */}
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="form-select"
                >
                  <option value="all">All Courses ({getStatusCount('all')})</option>
                  <option value="active">Active ({getStatusCount('active')})</option>
                  <option value="draft">Draft ({getStatusCount('draft')})</option>
                </select>

                {/* View Mode Toggle */}
                <div className="flex items-center bg-background-tertiary rounded-lg p-1 border border-border-primary">
                  <button
                    onClick={() => setViewMode('grid')}
                    className={`p-2 rounded-lg transition-all duration-300 ${
                      viewMode === 'grid'
                        ? 'bg-background-secondary shadow-elegant text-secondary-600'
                        : 'text-text-secondary hover:text-text-heading'
                    }`}
                  >
                    <Grid3X3 className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => setViewMode('list')}
                    className={`p-2 rounded-lg transition-all duration-300 ${
                      viewMode === 'list'
                        ? 'bg-background-secondary shadow-elegant text-secondary-600'
                        : 'text-text-secondary hover:text-text-heading'
                    }`}
                  >
                    <List className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Content */}
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader className="w-8 h-8 text-indigo-500 animate-spin" />
              <span className="ml-3 text-gray-600">Loading courses...</span>
            </div>
          ) : filteredCourses.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center py-12"
            >
              <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-600 mb-2">
                {searchTerm || statusFilter !== 'all' ? 'No courses found' : 'No courses yet'}
              </h3>
              <p className="text-gray-500 mb-6">
                {searchTerm || statusFilter !== 'all' 
                  ? 'Try adjusting your search or filter criteria'
                  : 'Create your first course to get started'
                }
              </p>
              {!searchTerm && statusFilter === 'all' && (
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="bg-gradient-to-r from-indigo-500 to-blue-500 text-white font-semibold px-6 py-3 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
                >
                  Create Your First Course
                </button>
              )}
            </motion.div>
          ) : (
            <div className={`grid gap-6 ${
              viewMode === 'grid' 
                ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3' 
                : 'grid-cols-1'
            }`}>
              {filteredCourses.map((course, index) => (
                <motion.div
                  key={course.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <CourseCard
                    course={course}
                    onEdit={(course) => {
                      setSelectedCourse(course);
                      setShowEditModal(true);
                    }}
                    onDelete={(course) => {
                      setSelectedCourse(course);
                      setShowDeleteModal(true);
                    }}
                    onView={handleViewCourse}
                  />
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Modals */}
      <CourseFormModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSubmit={handleCreateCourse}
        loading={formLoading}
      />

      <CourseFormModal
        isOpen={showEditModal}
        onClose={() => {
          setShowEditModal(false);
          setSelectedCourse(null);
        }}
        onSubmit={handleEditCourse}
        course={selectedCourse}
        loading={formLoading}
      />

      <EnhancedCourseViewModal
        isOpen={showViewModal}
        onClose={() => {
          setShowViewModal(false);
          setSelectedCourse(null);
        }}
        course={selectedCourse}
      />

      {/* Delete Confirmation Modal */}
      <AnimatePresence>
        {showDeleteModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6"
            >
              <div className="flex items-center justify-center w-12 h-12 bg-red-100 rounded-full mx-auto mb-4">
                <AlertCircle className="w-6 h-6 text-red-600" />
              </div>
              
              <h3 className="text-lg font-semibold text-gray-800 text-center mb-2">
                Delete Course
              </h3>
              
              <p className="text-gray-600 text-center mb-6">
                Are you sure you want to delete "{selectedCourse?.title}"? This action cannot be undone.
              </p>
              
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => {
                    setShowDeleteModal(false);
                    setSelectedCourse(null);
                  }}
                  className="flex-1 px-4 py-2 text-gray-600 hover:text-gray-800 font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDeleteCourse}
                  className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-xl transition-colors flex items-center justify-center space-x-2"
                >
                  <Trash2 className="w-4 h-4" />
                  <span>Delete</span>
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </TeacherDashboardLayout>
  );
};

export default TeacherMyCourses;
