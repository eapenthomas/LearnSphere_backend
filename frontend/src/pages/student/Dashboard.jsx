import React, { useState, useEffect } from "react";
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext.jsx';
import DashboardLayout from '../../components/DashboardLayout.jsx';
import Button from '../../components/Button.jsx';
import {
  BookOpen,
  Calendar,
  TrendingUp,
  Award,
  Clock,
  Play,
  CheckCircle,
  Star,
  ArrowRight,
  Users,
  Target,
  Zap
} from 'lucide-react';

const StudentDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  // Real-time state management
  const [stats, setStats] = useState([
    {
      title: 'Enrolled Courses',
      value: '0',
      change: 'Loading...',
      icon: BookOpen,
      color: 'from-blue-500 to-blue-600'
    },
    {
      title: 'Completed Assignments',
      value: '0',
      change: 'Loading...',
      icon: CheckCircle,
      color: 'from-green-500 to-green-600'
    },
    {
      title: 'Quiz Average',
      value: '0%',
      change: 'Loading...',
      icon: Target,
      color: 'from-purple-500 to-purple-600'
    }
  ]);

  const [loading, setLoading] = useState(true);
  const [recentCourses, setRecentCourses] = useState([]);
  const [upcomingAssignments, setUpcomingAssignments] = useState([]);

  // Fetch real-time data
  useEffect(() => {
    if (user?.id) {
      fetchDashboardData();
    }
  }, [user]);

  // Listen for progress updates
  useEffect(() => {
    const handleProgressUpdate = () => {
      console.log('Progress updated, refreshing dashboard...');
      if (user?.id) {
        fetchDashboardData();
      }
    };

    window.addEventListener('progressUpdated', handleProgressUpdate);

    return () => {
      window.removeEventListener('progressUpdated', handleProgressUpdate);
    };
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchEnrollmentStats(),
        fetchRecentCourses(),
        fetchUpcomingAssignments()
      ]);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchEnrollmentStats = async () => {
    try {
      // Fetch enrolled courses count
      const enrollmentsResponse = await fetch(`http://localhost:8000/api/courses/student/${user.id}/enrolled`);
      const enrollmentsResult = enrollmentsResponse.ok ? await enrollmentsResponse.json() : { data: [] };
      const enrollments = enrollmentsResult.data || [];

      // Fetch assignment submissions
      const assignmentsResponse = await fetch(`http://localhost:8000/api/assignments/student/${user.id}`);
      const assignments = assignmentsResponse.ok ? await assignmentsResponse.json() : [];

      // Fetch course progress data
      const progressResponse = await fetch(`http://localhost:8000/api/progress/student/${user.id}/courses`);
      const courseProgress = progressResponse.ok ? await progressResponse.json() : [];

      // Calculate stats
      const enrolledCount = enrollments.length;
      const completedAssignments = assignments.filter(a => a.submission_status === 'reviewed').length;
      const totalAssignments = assignments.length;
      const assignmentPercentage = totalAssignments > 0 ? Math.round((completedAssignments / totalAssignments) * 100) : 0;

      // Calculate overall course progress
      const totalProgress = courseProgress.reduce((sum, course) => sum + (course.overall_progress_percentage || 0), 0);
      const averageProgress = courseProgress.length > 0 ? Math.round(totalProgress / courseProgress.length) : 0;

      // Count completed materials
      const totalMaterials = courseProgress.reduce((sum, course) => sum + (course.total_materials || 0), 0);
      const completedMaterials = courseProgress.reduce((sum, course) => sum + (course.materials_completed || 0), 0);

      // Update stats
      setStats([
        {
          title: 'Enrolled Courses',
          value: enrolledCount.toString(),
          change: `${enrolledCount} active`,
          icon: BookOpen,
          color: 'from-blue-500 to-blue-600'
        },
        {
          title: 'Course Progress',
          value: `${averageProgress}%`,
          change: `${completedMaterials}/${totalMaterials} materials`,
          icon: TrendingUp,
          color: 'from-green-500 to-green-600'
        },
        {
          title: 'Assignment Progress',
          value: `${assignmentPercentage}%`,
          change: `${completedAssignments}/${totalAssignments} completed`,
          icon: Target,
          color: 'from-purple-500 to-purple-600'
        }
      ]);
    } catch (error) {
      console.error('Error fetching enrollment stats:', error);
    }
  };

  const fetchRecentCourses = async () => {
    try {
      // Fetch enrolled courses from the course API (better data structure)
      const response = await fetch(`http://localhost:8000/api/courses/student/${user.id}/enrolled`);

      if (response.ok) {
        const result = await response.json();
        const enrollments = result.data || [];

        // Get the most recent 3 courses with progress
        const recent = enrollments.slice(0, 3).map(enrollment => ({
          id: enrollment.course_id,
          title: enrollment.course?.title || 'Unknown Course',
          instructor: enrollment.course?.teacher_name || 'Unknown Teacher',
          progress: enrollment.progress || 0,
          nextLesson: 'Continue Learning',
          thumbnail: null
        }));
        setRecentCourses(recent);
      }
    } catch (error) {
      console.error('Error fetching recent courses:', error);
    }
  };

  const fetchUpcomingAssignments = async () => {
    try {
      console.log('🔍 Fetching upcoming assignments for user:', user.id);

      // Use the new urgent deadlines API to get assignments and quizzes due within 2 days
      const response = await fetch(`http://localhost:8000/api/student/deadlines/urgent?student_id=${user.id}&limit=5`);
      console.log('📡 Urgent deadlines API response status:', response.status);

      if (response.ok) {
        const urgentDeadlines = await response.json();
        console.log('📋 Urgent deadlines data:', urgentDeadlines);

        // Transform the data for the dashboard
        const upcoming = urgentDeadlines.map(deadline => ({
          title: deadline.title,
          course: deadline.course_name,
          dueDate: new Date(deadline.due_date).toLocaleDateString(),
          type: deadline.category,
          priority: deadline.priority,
          daysUntil: Math.ceil((new Date(deadline.due_date) - new Date()) / (1000 * 60 * 60 * 24))
        }));

        console.log('✅ Processed upcoming assignments:', upcoming);
        setUpcomingAssignments(upcoming);
      } else {
        console.log('⚠️ Urgent deadlines API failed, trying fallback...');
        // Fallback to old method if new API fails
        try {
          const response = await fetch(`http://localhost:8000/api/assignments/student/${user.id}`);
          console.log('📡 Fallback API response status:', response.status);

          if (response.ok) {
            const assignments = await response.json();
            console.log('📋 Fallback assignments data:', assignments);

            const upcoming = assignments
              .filter(a => a.submission_status === 'not_submitted' && new Date(a.due_date) > new Date())
              .sort((a, b) => new Date(a.due_date) - new Date(b.due_date))
              .slice(0, 5)
              .map(assignment => ({
                title: assignment.title,
                course: assignment.course_title,
                dueDate: new Date(assignment.due_date).toLocaleDateString(),
                type: 'assignment',
                daysUntil: Math.ceil((new Date(assignment.due_date) - new Date()) / (1000 * 60 * 60 * 24))
              }));

            console.log('✅ Processed fallback assignments:', upcoming);
            setUpcomingAssignments(upcoming);
          }
        } catch (fallbackError) {
          console.error('❌ Error with fallback method:', fallbackError);

          // Add sample data for testing when no real data is available
          const sampleDeadlines = [
            {
              title: 'JavaScript Fundamentals Quiz',
              course: 'Web Development',
              dueDate: new Date(Date.now() + 24 * 60 * 60 * 1000).toLocaleDateString(),
              type: 'quiz',
              daysUntil: 1
            },
            {
              title: 'React Project Assignment',
              course: 'Frontend Development',
              dueDate: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toLocaleDateString(),
              type: 'assignment',
              daysUntil: 2
            }
          ];

          console.log('🧪 Using sample deadlines for testing:', sampleDeadlines);
          setUpcomingAssignments(sampleDeadlines);
        }
      }
    } catch (error) {
      console.error('❌ Error fetching urgent deadlines:', error);

      // Add sample data for testing when API completely fails
      const sampleDeadlines = [
        {
          title: 'Sample Quiz - Due Tomorrow',
          course: 'Sample Course',
          dueDate: new Date(Date.now() + 24 * 60 * 60 * 1000).toLocaleDateString(),
          type: 'quiz',
          daysUntil: 1
        }
      ];

      console.log('🧪 Using sample deadlines due to error:', sampleDeadlines);
      setUpcomingAssignments(sampleDeadlines);
    }
  };

  // Static data removed - now using dynamic data from state

  // Get username from user data
  const username = user?.fullName?.split(' ')[0] || user?.email?.split('@')[0] || 'Student';

  return (
    <DashboardLayout>
      <div className="space-y-6 student-page-bg min-h-screen p-6">
        {/* Welcome Banner */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-primary-500 to-primary-600 p-6 text-white hover:shadow-xl transition-all duration-300"
        >
          <div className="absolute inset-0 bg-white/10"></div>
          <div className="relative z-10">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-heading-lg md:text-heading-xl font-bold mb-2 tracking-tight font-serif text-white">
                  Welcome back, {username}! 🎓
                </h1>
                <p className="text-body-lg text-white/90 mb-4 font-medium">
                  Ready to continue your learning journey? You're doing great!
                </p>
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <BookOpen className="w-5 h-5" />
                    <span className="font-semibold">{stats[0]?.value || 0} Active Courses</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <TrendingUp className="w-5 h-5" />
                    <span className="font-semibold">{stats[1]?.value || '0%'} Average Progress</span>
                  </div>
                </div>
              </div>
              <div className="hidden md:block">
                <div className="w-24 h-24 bg-white/20 rounded-full flex items-center justify-center">
                  <Award className="w-12 h-12 text-white" />
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 lg:gap-6">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="course-card rounded-xl p-6 transition-all duration-300 group"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 bg-gradient-to-br ${stat.color} rounded-xl group-hover:scale-110 transition-transform duration-300`}>
                  <stat.icon className="w-6 h-6 text-white" />
                </div>
                <span className={`text-body-sm font-bold ${stat.change.startsWith('+') ? 'text-success-600' : 'text-error-600'}`}>
                  {stat.change}
                </span>
              </div>
              <h3 className="text-heading-lg font-bold mb-1" style={{color: '#000000'}}>{stat.value}</h3>
              <p className="text-body-md font-medium" style={{color: '#000000'}}>{stat.title}</p>
            </motion.div>
          ))}
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Continue Learning */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="course-card rounded-xl p-6 transition-all duration-300"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-heading-md font-semibold" style={{color: '#ffffffff'}}>
                  Continue Learning
                </h2>
                <button
                  onClick={() => navigate('/mycourses')}
                  className="btn-primary px-4 py-2 text-sm rounded-lg"
                >
                  View All
                </button>
              </div>
              <div className="space-y-4">
                {recentCourses.map((course, index) => (
                  <motion.div
                    key={course.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center space-x-4 p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-all duration-300 cursor-pointer group"
                  >
                    <div className="w-12 h-12 bg-gradient-to-br from-indigo-100 to-blue-100 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                      <BookOpen className="w-6 h-6 text-indigo-600" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-bold text-gray-800 text-sm">
                        {course.title}
                      </h3>
                      <p className="text-xs text-gray-500 font-medium">
                        {course.instructor} • Next: {course.nextLesson}
                      </p>
                      <div className="mt-2">
                        <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                          <span className="font-medium">Progress</span>
                          <span className="font-bold">{course.progress}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-blue-500 to-blue-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${course.progress}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                    <Button
                      size="sm"
                      className="opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                    >
                      <Play className="w-4 h-4 mr-1" />
                      Continue
                    </Button>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>

          {/* Upcoming Deadlines */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="card p-6 hover:shadow-xl transition-all duration-300 bg-white dark:bg-slate-800 text-gray-800 dark:text-gray-100"
          >
            <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-gray-900 dark:text-white tracking-tight">
                    Upcoming Deadlines
                  </h2>
              <Clock className="w-5 h-5 text-gray-400" />
            </div>
            <div className="space-y-4">
              {loading ? (
                <div className="text-center py-4">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto mb-2"></div>
                  <p className="text-sm text-gray-700 dark:text-gray-300 font-medium">Loading assignments...</p>
                </div>
              ) : upcomingAssignments.length === 0 ? (
                <div className="text-center py-8">
                  <Clock className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-700 dark:text-gray-300 font-medium">No upcoming deadlines</p>
                </div>
              ) : (
                upcomingAssignments.map((deadline, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 1, x: 0 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 bg-white dark:bg-gray-800 rounded-lg border-l-4 border-red-500 shadow-lg hover:shadow-xl transition-all duration-300"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <h3 className="font-bold text-gray-900 dark:text-white text-base">
                        {deadline.title}
                      </h3>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className={`text-sm px-3 py-1 rounded-full font-bold ${
                          deadline.type === 'quiz' ? 'bg-purple-500 text-white' : 'bg-blue-500 text-white'
                        }`}>
                          {deadline.type === 'quiz' ? 'Quiz' : 'Assignment'}
                        </span>
                        {deadline.daysUntil <= 1 && (
                          <span className="text-sm bg-red-500 text-white px-3 py-1 rounded-full font-bold">
                            {deadline.daysUntil === 0 ? 'Due Today' : 'Due Tomorrow'}
                          </span>
                        )}
                      </div>
                    </div>
                    <span className="text-sm text-white font-bold bg-red-600 px-3 py-1 rounded-full">
                      {deadline.dueDate}
                    </span>
                  </div>
                  <p className="text-sm text-gray-800 dark:text-gray-200 font-bold">
                    {deadline.course}
                  </p>
                  <div className="mt-2 flex items-center justify-between">
                    <span className="text-sm text-gray-700 dark:text-gray-300 capitalize font-bold">
                      {deadline.type}
                    </span>
                    <ArrowRight className="w-5 h-5 text-gray-700 dark:text-gray-300" />
                  </div>
                </motion.div>
                ))
              )}
            </div>
          </motion.div>
        </div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card p-6 hover:shadow-xl transition-all duration-300 bg-white dark:bg-slate-800 text-gray-800 dark:text-gray-100"

        >
          <h2 className="text-xl font-extrabold text-gray-800 tracking-tight mb-6">
            Quick Actions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Button
              variant="outline"
              className="h-auto p-4 flex flex-col items-center space-y-2 hover:bg-blue-50 hover:border-blue-300"
              onClick={() => navigate('/allcourses')}
            >
              <BookOpen className="w-6 h-6 text-blue-600" />
              <span className="font-semibold">Browse Courses</span>
            </Button>
            <Button
              variant="outline"
              className="h-auto p-4 flex flex-col items-center space-y-2 hover:bg-green-50 hover:border-green-300"
              onClick={() => navigate('/assignments')}
            >
              <CheckCircle className="w-6 h-6 text-green-600" />
              <span className="font-semibold">Assignments</span>
            </Button>
            <Button
              variant="outline"
              className="h-auto p-4 flex flex-col items-center space-y-2 hover:bg-purple-50 hover:border-purple-300"
              onClick={() => navigate('/student/quizzes')}
            >
              <Target className="w-6 h-6 text-purple-600" />
              <span className="font-semibold">Take Quiz</span>
            </Button>
            <Button
              variant="outline"
              className="h-auto p-4 flex flex-col items-center space-y-2 hover:bg-yellow-50 hover:border-yellow-300"
              onClick={() => navigate('/forum')}
            >
              <Zap className="w-6 h-6 text-yellow-600" />
              <span className="font-semibold">Ask Doubt</span>
            </Button>
          </div>
        </motion.div>
      </div>
    </DashboardLayout>
  );
};

export default StudentDashboard;
