import { motion } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext.jsx';
import TeacherDashboardLayout from '../../layouts/TeacherDashboardLayout.jsx';
import Button from '../../components/Button.jsx';
import React, { useState, useEffect } from "react";

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
  Zap,
  FileText,
  ClipboardList,
  MessageSquare,
  Plus,
  Eye,
  Edit,
  AlertTriangle,
  GraduationCap,
  BarChart3,
  RefreshCw
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar
} from 'recharts';

const TeacherDashboard = () => {
  const { user } = useAuth();

  // Real-time state management
  const [stats, setStats] = useState([
    {
      title: 'Total Courses Created',
      value: '0',
      change: 'Loading...',
      icon: BookOpen,
      color: 'from-blue-500 to-blue-600'
    },
    {
      title: 'Assignments to Grade',
      value: '0',
      change: 'Loading...',
      icon: ClipboardList,
      color: 'from-orange-500 to-orange-600'
    },
    {
      title: 'Total Students',
      value: '0',
      change: 'Loading...',
      icon: Users,
      color: 'from-green-500 to-green-600'
    }
  ]);

  const [loading, setLoading] = useState(true);
  const [recentCourses, setRecentCourses] = useState([]);
  const [pendingSubmissions, setPendingSubmissions] = useState([]);
  const [enrollmentTrends, setEnrollmentTrends] = useState([]);
  const [coursePerformanceData, setCoursePerformanceData] = useState([]);
  const [upcomingDeadlines, setUpcomingDeadlines] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);
  const [analyticsData, setAnalyticsData] = useState({
    totalStudents: 0,
    activeCourses: 0,
    totalAssignments: 0,
    averageGrade: 0.0
  });

  // Fetch real-time data
  useEffect(() => {
    if (user?.id) {
      fetchDashboardData();
    }
  }, [user]);

  // Set up real-time updates every 30 seconds
  useEffect(() => {
    if (user?.id) {
      const interval = setInterval(() => {
        fetchDashboardData();
      }, 30000); // Update every 30 seconds

      return () => clearInterval(interval);
    }
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      // First fetch analytics data, then use it in teacher stats
      await fetchAnalyticsData();
      await Promise.all([
        fetchTeacherStats(),
        fetchRecentCourses(),
        fetchPendingSubmissions()
      ]);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTeacherStats = async () => {
    try {
      // Fetch courses
      const coursesResponse = await fetch(`http://localhost:8000/api/courses/teacher/${user.id}`);
      const coursesData = coursesResponse.ok ? await coursesResponse.json() : {data: []};
      const courses = coursesData.success ? coursesData.data : [];

      // Fetch assignments
      const assignmentsResponse = await fetch(`http://localhost:8000/api/assignments/teacher/${user.id}`);
      const assignmentsData = assignmentsResponse.ok ? await assignmentsResponse.json() : [];
      const assignments = Array.isArray(assignmentsData) ? assignmentsData : [];

      // Fetch unique students across all courses
      const uniqueStudents = new Set();
      let totalProgress = 0;
      let studentsWithProgress = 0;

      for (const course of courses) {
        try {
          // Get enrollments for this course
          const enrollmentsResponse = await fetch(`http://localhost:8000/api/enrollments/course/${course.id}`);
          if (enrollmentsResponse.ok) {
            const enrollments = await enrollmentsResponse.json();

            // Add unique students
            enrollments.forEach(enrollment => {
              uniqueStudents.add(enrollment.student_id);
            });

            // Get progress for each enrolled student
            for (const enrollment of enrollments) {
              try {
                const progressResponse = await fetch(`http://localhost:8000/api/progress/course/${course.id}/student/${enrollment.student_id}`);
                if (progressResponse.ok) {
                  const progress = await progressResponse.json();
                  if (progress) {
                    totalProgress += progress.overall_progress_percentage || 0;
                    studentsWithProgress++;
                  }
                }
              } catch (e) {
                console.log('Progress not available for student:', enrollment.student_id);
              }
            }
          }
        } catch (e) {
          console.log('Enrollments not available for course:', course.id);
        }
      }

      const totalStudents = uniqueStudents.size;

      // Calculate pending submissions
      let totalPendingSubmissions = 0;
      for (const assignment of assignments) {
        const submissionsResponse = await fetch(`http://localhost:8000/api/assignments/submissions/${assignment.id}?teacher_id=${user.id}`);
        if (submissionsResponse.ok) {
          const submissions = await submissionsResponse.json();
          totalPendingSubmissions += submissions.filter(s => s.status !== 'reviewed').length;
        }
      }

      // Calculate average progress
      const averageProgress = studentsWithProgress > 0 ? Math.round(totalProgress / studentsWithProgress) : 0;

      // Update stats using analytics data if available, otherwise use manual calculation
      const statsData = analyticsData.totalStudents > 0 ? {
        totalCourses: analyticsData.activeCourses,
        totalStudents: analyticsData.totalStudents,
        totalAssignments: analyticsData.totalAssignments,
        pendingSubmissions: totalPendingSubmissions
      } : {
        totalCourses: courses.length,
        totalStudents: totalStudents,
        totalAssignments: assignments.length,
        pendingSubmissions: totalPendingSubmissions
      };

      setStats([
        {
          title: 'Total Courses Created',
          value: statsData.totalCourses.toString(),
          change: `${courses.filter(c => c.status === 'active').length} active`,
          icon: BookOpen,
          color: 'from-blue-500 to-blue-600'
        },
        {
          title: 'Assignments to Grade',
          value: statsData.pendingSubmissions.toString(),
          change: `${statsData.totalAssignments} total assignments`,
          icon: ClipboardList,
          color: 'from-orange-500 to-orange-600'
        },
        {
          title: 'Total Students',
          value: statsData.totalStudents.toString(),
          change: `${studentsWithProgress} with tracked progress`,
          icon: Users,
          color: 'from-purple-500 to-purple-600'
        }
      ]);
    } catch (error) {
      console.error('Error fetching teacher stats:', error);
    }
  };

  const fetchRecentCourses = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/courses/teacher/${user.id}`);
      if (response.ok) {
        const coursesData = await response.json();
        const courses = Array.isArray(coursesData) ? coursesData : [];
        // Get the most recent 3 courses
        const recent = courses.slice(0, 3).map(course => ({
          id: course.id,
          title: course.title,
          students: course.enrollment_count || 0,
          status: course.status,
          lastActivity: 'Recently updated'
        }));
        setRecentCourses(recent);
      }
    } catch (error) {
      console.error('Error fetching recent courses:', error);
      setRecentCourses([]); // Set empty array on error
    }
  };

  const fetchPendingSubmissions = async () => {
    try {
      const assignmentsResponse = await fetch(`http://localhost:8000/api/assignments/teacher/${user.id}`);
      if (assignmentsResponse.ok) {
        const assignments = await assignmentsResponse.json();
        const pending = [];

        for (const assignment of assignments.slice(0, 3)) {
          const submissionsResponse = await fetch(`http://localhost:8000/api/assignments/submissions/${assignment.id}?teacher_id=${user.id}`);
          if (submissionsResponse.ok) {
            const submissions = await submissionsResponse.json();
            const pendingCount = submissions.filter(s => s.status !== 'reviewed').length;
            if (pendingCount > 0) {
              pending.push({
                assignment: assignment.title,
                course: assignment.course_title,
                count: pendingCount,
                dueDate: new Date(assignment.due_date).toLocaleDateString()
              });
            }
          }
        }

        setPendingSubmissions(pending);
      }
    } catch (error) {
      console.error('Error fetching pending submissions:', error);
    }
  };

  const fetchAnalyticsData = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/teacher/analytics/${user.id}`);
      if (response.ok) {
        const data = await response.json();
        setEnrollmentTrends(data.enrollmentTrends || []);
        setCoursePerformanceData(data.coursePerformanceData || []);
        setUpcomingDeadlines(data.upcomingDeadlines || []);
        setRecentActivity(data.recentActivity || []);

        // Update analytics data for display
        setAnalyticsData({
          totalStudents: data.totalStudents || 0,
          activeCourses: data.activeCourses || 0,
          totalAssignments: data.totalAssignments || 0,
          averageGrade: data.averageGrade || 0.0
        });
      }
    } catch (error) {
      console.error('Error fetching analytics data:', error);
    }
  };

  // Helper functions for UI
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'text-red-500 bg-red-50';
      case 'medium': return 'text-yellow-500 bg-yellow-50';
      case 'low': return 'text-green-500 bg-green-50';
      default: return 'text-gray-500 bg-gray-50';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'quiz': return FileText;
      case 'assignment': return ClipboardList;
      case 'project': return Target;
      default: return FileText;
    }
  };

  const getActivityIcon = (iconName) => {
    switch (iconName) {
      case 'CheckCircle': return CheckCircle;
      case 'Star': return Star;
      case 'MessageSquare': return MessageSquare;
      case 'AlertTriangle': return AlertTriangle;
      default: return CheckCircle;
    }
  };

  const quickActions = [
    {
      title: 'Create Course',
      description: 'Start a new course for your students',
      icon: BookOpen,
      color: 'from-blue-500 to-blue-600',
      action: () => window.location.href = '/teacher/courses'
    },
    {
      title: 'Add Quiz',
      description: 'Create a new quiz or assessment',
      icon: FileText,
      color: 'from-green-500 to-green-600',
      action: () => console.log('Add quiz')
    },
    {
      title: 'Post Assignment',
      description: 'Assign new tasks to students',
      icon: ClipboardList,
      color: 'from-purple-500 to-purple-600',
      action: () => console.log('Post assignment')
    }
  ];

  // Get username from user data
  const username = user?.fullName?.split(' ')[0] || user?.email?.split('@')[0] || 'Teacher';

  return (
    <TeacherDashboardLayout>
      <div className="space-y-6 teacher-page-bg min-h-screen p-6">
        {/* Welcome Banner */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-blue-500 to-blue-600 p-6 text-white hover:shadow-xl transition-all duration-300"
        >
          <div className="absolute inset-0 bg-white/10"></div>
          <div className="relative z-10">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-semibold text-white mb-2">
                  Welcome back, {username}! 👨‍🏫
                </h1>
                <p className="text-base text-white mb-4">
                  Ready to inspire and educate your students? You have great impact on their learning journey!
                </p>
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <Users className="w-5 h-5" />
                    <span className="font-semibold">{analyticsData.totalStudents} Active Students</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <TrendingUp className="w-5 h-5" />
                    <span className="font-semibold">{analyticsData.averageGrade}% Avg Performance</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <button
                  onClick={fetchDashboardData}
                  className="flex items-center space-x-2 bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg transition-colors"
                  title="Refresh Dashboard"
                >
                  <RefreshCw className="w-4 h-4 text-white" />
                  <span className="text-white font-medium">Refresh</span>
                </button>
                <div className="hidden md:block">
                  <div className="w-24 h-24 bg-white/20 rounded-full flex items-center justify-center">
                    <GraduationCap className="w-12 h-12 text-white" />
                  </div>
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
              className="teacher-course-card rounded-xl p-6 transition-all duration-300 group"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 bg-gradient-to-br ${stat.color} rounded-xl group-hover:scale-110 transition-transform duration-300`}>
                  <stat.icon className="w-6 h-6 text-white" />
                </div>
                <span className={`text-sm font-bold ${stat.change.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
                  {stat.change}
                </span>
              </div>
              <h3 className="text-2xl font-extrabold mb-1" style={{color: '#ffffffff'}}>{stat.value}</h3>
              <p className="text-sm font-medium" style={{color: '#978181ff'}}>{stat.title}</p>
            </motion.div>
          ))}
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Student Enrollment Trends Chart */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-extrabold tracking-tight text-gray-800">
                Student Progress & Engagement
              </h2>
              <div className="flex items-center space-x-4 text-sm">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                  <span className="font-medium text-gray-700">Total Enrolled</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="font-medium text-gray-700">Weekly Active</span>
                </div>
              </div>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={enrollmentTrends}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="name" stroke="#6b7280" />
                  <YAxis stroke="#6b7280" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: 'none',
                      borderRadius: '12px',
                      boxShadow: '0 10px 25px rgba(0,0,0,0.1)'
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="enrollments"
                    stroke="#3b82f6"
                    strokeWidth={3}
                    dot={{ fill: '#3b82f6', strokeWidth: 2, r: 6 }}
                  />
                  <Line
                    type="monotone"
                    dataKey="active_students"
                    stroke="#10b981"
                    strokeWidth={3}
                    dot={{ fill: '#10b981', strokeWidth: 2, r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* Course Performance Chart */}
          {/* <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-extrabold text-gray-800 tracking-tight">
                Course Performance
              </h2>
              <BarChart3 className="w-5 h-5 text-gray-400" />
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={coursePerformanceData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="course" stroke="#6b7280" />
                  <YAxis stroke="#6b7280" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: 'none',
                      borderRadius: '12px',
                      boxShadow: '0 10px 25px rgba(0,0,0,0.1)'
                    }}
                  />
                  <Bar dataKey="avgScore" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </motion.div> */}
        </div>
      </div>
    </TeacherDashboardLayout>
  );
};

export default TeacherDashboard;
