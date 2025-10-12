import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext.jsx';
import TeacherDashboardLayout from '../../layouts/TeacherDashboardLayout.jsx';
import {
  TrendingUp,
  Users,
  BookOpen,
  CheckCircle,
  Clock,
  Award,
  BarChart3,
  PieChart,
  Activity,
  Target
} from 'lucide-react';

const TeacherProgress = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [courses, setCourses] = useState([]);
  const [overallStats, setOverallStats] = useState({
    totalStudents: 0,
    totalCourses: 0,
    averageProgress: 0,
    completedCourses: 0
  });

  useEffect(() => {
    if (user?.id) {
      fetchProgressData();
    }
  }, [user]);

  const fetchProgressData = async () => {
    try {
      setLoading(true);
      
      // Fetch teacher's courses
      const coursesResponse = await fetch(`http://localhost:8000/api/courses/teacher/${user.id}`);
      const coursesResult = coursesResponse.ok ? await coursesResponse.json() : { success: false, data: [] };
      const coursesArray = (coursesResult.success && Array.isArray(coursesResult.data)) ? coursesResult.data : [];
      
      // Fetch progress for each course
      const coursesWithProgress = await Promise.all(
        coursesArray.map(async (course) => {
          try {
            // Get enrollments
            const enrollmentsResponse = await fetch(`http://localhost:8000/api/enrollments/course/${course.id}?teacher_id=${user.id}`);
            const enrollments = enrollmentsResponse.ok ? await enrollmentsResponse.json() : [];
            
            // Get progress for each student
            const studentsProgress = await Promise.all(
              enrollments.map(async (enrollment) => {
                try {
                  const progressResponse = await fetch(`http://localhost:8000/api/progress/course/${course.id}/student/${enrollment.student_id}`);
                  const progress = progressResponse.ok ? await progressResponse.json() : { overall_progress_percentage: 0 };
                  return {
                    studentId: enrollment.student_id,
                    studentName: enrollment.student_name || 'Unknown',
                    progress: progress.overall_progress_percentage || 0,
                    isCompleted: progress.is_completed || false
                  };
                } catch (error) {
                  console.error('Error fetching student progress:', error);
                  return {
                    studentId: enrollment.student_id,
                    studentName: enrollment.student_name || 'Unknown',
                    progress: 0,
                    isCompleted: false
                  };
                }
              })
            );
            
            const averageProgress = studentsProgress.length > 0 
              ? studentsProgress.reduce((sum, student) => sum + student.progress, 0) / studentsProgress.length 
              : 0;
            
            const completedStudents = studentsProgress.filter(student => student.isCompleted).length;
            
            return {
              ...course,
              enrolledStudents: studentsProgress.length,
              averageProgress: Math.round(averageProgress),
              completedStudents,
              studentsProgress
            };
          } catch (error) {
            console.error('Error fetching course progress:', error);
            return {
              ...course,
              enrolledStudents: 0,
              averageProgress: 0,
              completedStudents: 0,
              studentsProgress: []
            };
          }
        })
      );
      
      setCourses(coursesWithProgress);
      
      // Calculate overall stats
      const totalStudents = coursesWithProgress.reduce((sum, course) => sum + course.enrolledStudents, 0);
      const totalCourses = coursesWithProgress.length;
      const averageProgress = coursesWithProgress.length > 0 
        ? coursesWithProgress.reduce((sum, course) => sum + course.averageProgress, 0) / coursesWithProgress.length 
        : 0;
      const completedCourses = coursesWithProgress.filter(course => course.averageProgress === 100).length;
      
      setOverallStats({
        totalStudents,
        totalCourses,
        averageProgress: Math.round(averageProgress),
        completedCourses
      });
      
    } catch (error) {
      console.error('Error fetching progress data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getProgressColor = (progress) => {
    if (progress >= 80) return 'bg-green-500';
    if (progress >= 60) return 'bg-blue-500';
    if (progress >= 40) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getProgressTextColor = (progress) => {
    if (progress >= 80) return 'text-green-600';
    if (progress >= 60) return 'text-blue-600';
    if (progress >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <TeacherDashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
        </div>
      </TeacherDashboardLayout>
    );
  }

  return (
    <TeacherDashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Student Progress</h1>
            <p className="text-gray-600 mt-1">Monitor your students' learning progress across all courses</p>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={fetchProgressData}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            Refresh Data
          </motion.button>
        </div>

        {/* Overall Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white p-6 rounded-xl shadow-sm border border-gray-200"
          >
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-lg">
                <Users className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Students</p>
                <p className="text-2xl font-bold text-gray-900">{overallStats.totalStudents}</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white p-6 rounded-xl shadow-sm border border-gray-200"
          >
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-lg">
                <BookOpen className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Courses</p>
                <p className="text-2xl font-bold text-gray-900">{overallStats.totalCourses}</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white p-6 rounded-xl shadow-sm border border-gray-200"
          >
            <div className="flex items-center">
              <div className="p-3 bg-purple-100 rounded-lg">
                <TrendingUp className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Average Progress</p>
                <p className="text-2xl font-bold text-gray-900">{overallStats.averageProgress}%</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white p-6 rounded-xl shadow-sm border border-gray-200"
          >
            <div className="flex items-center">
              <div className="p-3 bg-yellow-100 rounded-lg">
                <Award className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Completed Courses</p>
                <p className="text-2xl font-bold text-gray-900">{overallStats.completedCourses}</p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Courses Progress */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Course Progress Overview</h2>
            <p className="text-gray-600 mt-1">Detailed progress for each of your courses</p>
          </div>
          
          <div className="p-6">
            {courses.length === 0 ? (
              <div className="text-center py-12">
                <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Courses Found</h3>
                <p className="text-gray-600">You haven't created any courses yet.</p>
              </div>
            ) : (
              <div className="space-y-6">
                {courses.map((course, index) => (
                  <motion.div
                    key={course.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="border border-gray-200 rounded-lg p-6"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{course.title}</h3>
                        <p className="text-gray-600">{course.enrolledStudents} students enrolled</p>
                      </div>
                      <div className="text-right">
                        <p className={`text-2xl font-bold ${getProgressTextColor(course.averageProgress)}`}>
                          {course.averageProgress}%
                        </p>
                        <p className="text-sm text-gray-600">Average Progress</p>
                      </div>
                    </div>
                    
                    <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
                      <div
                        className={`h-3 rounded-full ${getProgressColor(course.averageProgress)} transition-all duration-300`}
                        style={{ width: `${course.averageProgress}%` }}
                      ></div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="flex items-center">
                        <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
                        <span className="text-sm text-gray-600">
                          {course.completedStudents} completed
                        </span>
                      </div>
                      <div className="flex items-center">
                        <Clock className="h-5 w-5 text-blue-500 mr-2" />
                        <span className="text-sm text-gray-600">
                          {course.enrolledStudents - course.completedStudents} in progress
                        </span>
                      </div>
                      <div className="flex items-center">
                        <Activity className="h-5 w-5 text-purple-500 mr-2" />
                        <span className="text-sm text-gray-600">
                          {course.enrolledStudents} total students
                        </span>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </TeacherDashboardLayout>
  );
};

export default TeacherProgress;
