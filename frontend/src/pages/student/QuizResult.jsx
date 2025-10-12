import { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext.jsx';
import DashboardLayout from '../../components/DashboardLayout.jsx';
import { toast } from 'react-hot-toast';
import {
  Award,
  TrendingUp,
  Clock,
  CheckCircle,
  XCircle,
  ArrowLeft,
  BookOpen,
  Target,
  Star,
  Trophy,
  Calendar
} from 'lucide-react';

const QuizResult = () => {
  const { quizId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [quiz, setQuiz] = useState(null);
  const [submission, setSubmission] = useState(null);
  const [loading, setLoading] = useState(true);

  // Get result data from navigation state or fetch from API
  const resultData = location.state;

  useEffect(() => {
    fetchQuizAndSubmission();
  }, [quizId, user]);

  const fetchQuizAndSubmission = async () => {
    try {
      setLoading(true);
      
      // Fetch quiz details
      const quizResponse = await fetch(`http://localhost:8000/api/quizzes/${quizId}`);
      const quizData = await quizResponse.json();
      
      if (quizData.success) {
        setQuiz(quizData.data);
      }

      // Fetch submission details
      const submissionResponse = await fetch(`http://localhost:8000/api/quizzes/${quizId}/submissions`);
      const submissionData = await submissionResponse.json();
      
      if (submissionData.success) {
        // Find the current user's submission
        const userSubmission = submissionData.data.find(sub => sub.student_id === user.id);
        setSubmission(userSubmission);
      }
    } catch (error) {
      console.error('Error fetching quiz result:', error);
      toast.error('Failed to load quiz result');
    } finally {
      setLoading(false);
    }
  };

  const getGrade = (percentage) => {
    if (percentage >= 90) return { grade: 'A+', color: 'text-emerald-600', bgColor: 'bg-emerald-50' };
    if (percentage >= 80) return { grade: 'A', color: 'text-emerald-600', bgColor: 'bg-emerald-50' };
    if (percentage >= 70) return { grade: 'B+', color: 'text-blue-600', bgColor: 'bg-blue-50' };
    if (percentage >= 60) return { grade: 'B', color: 'text-blue-600', bgColor: 'bg-blue-50' };
    if (percentage >= 50) return { grade: 'C+', color: 'text-yellow-600', bgColor: 'bg-yellow-50' };
    if (percentage >= 40) return { grade: 'C', color: 'text-yellow-600', bgColor: 'bg-yellow-50' };
    return { grade: 'F', color: 'text-red-600', bgColor: 'bg-red-50' };
  };

  const getPerformanceMessage = (percentage) => {
    if (percentage >= 90) return { message: 'Outstanding Performance!', icon: Trophy, color: 'text-emerald-600' };
    if (percentage >= 80) return { message: 'Excellent Work!', icon: Star, color: 'text-emerald-600' };
    if (percentage >= 70) return { message: 'Good Job!', icon: TrendingUp, color: 'text-blue-600' };
    if (percentage >= 60) return { message: 'Well Done!', icon: CheckCircle, color: 'text-blue-600' };
    if (percentage >= 40) return { message: 'Keep Practicing!', icon: Target, color: 'text-yellow-600' };
    return { message: 'Need More Practice', icon: XCircle, color: 'text-red-600' };
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
        </div>
      </DashboardLayout>
    );
  }

  const score = resultData?.score || submission?.score || 0;
  const totalMarks = resultData?.totalMarks || submission?.total_marks || quiz?.total_marks || 1;
  const percentage = resultData?.percentage || Math.round((score / totalMarks) * 100);
  
  const gradeInfo = getGrade(percentage);
  const performanceInfo = getPerformanceMessage(percentage);
  const PerformanceIcon = performanceInfo.icon;

  return (
    <DashboardLayout>
      <div className="p-6 space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl shadow-lg p-8"
        >
          <div className="flex items-center justify-between mb-6">
            <button
              onClick={() => navigate('/student/quizzes')}
              className="flex items-center space-x-2 text-gray-700 hover:text-gray-900 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              <span>Back to Quizzes</span>
            </button>
          </div>

          <div className="text-center">
            <div className={`w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4 ${gradeInfo.bgColor}`}>
              <PerformanceIcon className={`w-10 h-10 ${performanceInfo.color}`} />
            </div>
            
            <h1 className="text-3xl font-extrabold text-gray-900 mb-2">
              {performanceInfo.message}
            </h1>
            
            <p className="text-lg text-gray-700 mb-4">
              You've completed "{quiz?.title}"
            </p>

            <div className="flex items-center justify-center space-x-6 text-gray-600">
              <div className="flex items-center space-x-2">
                <BookOpen className="w-5 h-5" />
                <span>{quiz?.courses?.title}</span>
              </div>
              {submission?.submitted_at && (
                <div className="flex items-center space-x-2">
                  <Calendar className="w-5 h-5" />
                  <span>{new Date(submission.submitted_at).toLocaleDateString()}</span>
                </div>
              )}
              {submission?.time_taken_minutes && (
                <div className="flex items-center space-x-2">
                  <Clock className="w-5 h-5" />
                  <span>{submission.time_taken_minutes} minutes</span>
                </div>
              )}
            </div>
          </div>
        </motion.div>

        {/* Score Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-6"
        >
          {/* Score */}
          <div className="bg-white rounded-2xl shadow-lg p-6 text-center">
            <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Award className="w-8 h-8 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Your Score</h3>
            <p className="text-3xl font-bold text-purple-600">
              {score}/{totalMarks}
            </p>
            <p className="text-sm text-gray-600">marks</p>
          </div>

          {/* Percentage */}
          <div className="bg-white rounded-2xl shadow-lg p-6 text-center">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <TrendingUp className="w-8 h-8 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Percentage</h3>
            <p className="text-3xl font-bold text-blue-600">
              {percentage}%
            </p>
            <p className="text-sm text-gray-600">score</p>
          </div>

          {/* Grade */}
          <div className="bg-white rounded-2xl shadow-lg p-6 text-center">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 ${gradeInfo.bgColor}`}>
              <Star className={`w-8 h-8 ${gradeInfo.color}`} />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Grade</h3>
            <p className={`text-3xl font-bold ${gradeInfo.color}`}>
              {gradeInfo.grade}
            </p>
            <p className="text-sm text-gray-600">letter grade</p>
          </div>

          {/* Status */}
          <div className="bg-white rounded-2xl shadow-lg p-6 text-center">
            <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 ${
              percentage >= 60 ? 'bg-emerald-100' : 'bg-red-100'
            }`}>
              {percentage >= 60 ? (
                <CheckCircle className="w-8 h-8 text-emerald-600" />
              ) : (
                <XCircle className="w-8 h-8 text-red-600" />
              )}
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Status</h3>
            <p className={`text-xl font-bold ${
              percentage >= 60 ? 'text-emerald-600' : 'text-red-600'
            }`}>
              {percentage >= 60 ? 'Passed' : 'Failed'}
            </p>
            <p className="text-sm text-gray-600">
              {percentage >= 60 ? 'Congratulations!' : 'Try again!'}
            </p>
          </div>
        </motion.div>

        {/* Performance Analysis */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-2xl shadow-lg p-8"
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Performance Analysis</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Score Breakdown */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Score Breakdown</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <span className="text-gray-700">Total Questions</span>
                  <span className="font-semibold text-gray-900">{quiz?.questions?.length || 0}</span>
                </div>
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <span className="text-gray-700">Total Marks</span>
                  <span className="font-semibold text-gray-900">{totalMarks}</span>
                </div>
                <div className="flex items-center justify-between p-4 bg-purple-50 rounded-lg">
                  <span className="text-purple-700">Marks Obtained</span>
                  <span className="font-semibold text-purple-900">{score}</span>
                </div>
                <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
                  <span className="text-blue-700">Percentage</span>
                  <span className="font-semibold text-blue-900">{percentage}%</span>
                </div>
              </div>
            </div>

            {/* Performance Insights */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Insights</h3>
              <div className="space-y-4">
                {percentage >= 90 && (
                  <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Trophy className="w-5 h-5 text-emerald-600" />
                      <span className="font-semibold text-emerald-800">Excellent Performance!</span>
                    </div>
                    <p className="text-emerald-700 text-sm">
                      You've demonstrated outstanding understanding of the material. Keep up the excellent work!
                    </p>
                  </div>
                )}
                
                {percentage >= 70 && percentage < 90 && (
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <TrendingUp className="w-5 h-5 text-blue-600" />
                      <span className="font-semibold text-blue-800">Good Performance!</span>
                    </div>
                    <p className="text-blue-700 text-sm">
                      You have a solid understanding of the material. Review the areas you missed to improve further.
                    </p>
                  </div>
                )}
                
                {percentage >= 60 && percentage < 70 && (
                  <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Target className="w-5 h-5 text-yellow-600" />
                      <span className="font-semibold text-yellow-800">Satisfactory Performance</span>
                    </div>
                    <p className="text-yellow-700 text-sm">
                      You've passed the quiz! Consider reviewing the material to strengthen your understanding.
                    </p>
                  </div>
                )}
                
                {percentage < 60 && (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <XCircle className="w-5 h-5 text-red-600" />
                      <span className="font-semibold text-red-800">Needs Improvement</span>
                    </div>
                    <p className="text-red-700 text-sm">
                      Don't worry! Review the course material and try again. Practice makes perfect!
                    </p>
                  </div>
                )}

                {submission?.time_taken_minutes && (
                  <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Clock className="w-5 h-5 text-gray-600" />
                      <span className="font-semibold text-gray-800">Time Management</span>
                    </div>
                    <p className="text-gray-700 text-sm">
                      You completed the quiz in {submission.time_taken_minutes} minutes out of {quiz?.duration_minutes} minutes allowed.
                      {submission.time_taken_minutes < (quiz?.duration_minutes * 0.5) && ' Great time management!'}
                      {submission.time_taken_minutes > (quiz?.duration_minutes * 0.9) && ' Consider managing your time more efficiently next time.'}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="flex items-center justify-center space-x-4"
        >
          <button
            onClick={() => navigate('/student/quizzes')}
            className="btn-primary btn-lg"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to Quizzes</span>
          </button>

          <button
            onClick={() => navigate('/student/courses')}
            className="btn-secondary btn-lg"
          >
            <BookOpen className="w-5 h-5" />
            <span>Continue Learning</span>
          </button>
        </motion.div>
      </div>
    </DashboardLayout>
  );
};

export default QuizResult;
