import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext.jsx';
import { toast } from 'react-hot-toast';
import {
  Clock,
  AlertTriangle,
  CheckCircle,
  ArrowLeft,
  ArrowRight,
  Flag,
  Send,
  BookOpen,
  Award,
  Timer,
  FileText
} from 'lucide-react';

const TakeQuiz = () => {
  const { quizId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [quiz, setQuiz] = useState(null);
  const [loading, setLoading] = useState(true);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(0);
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [startTime] = useState(new Date());
  const timerRef = useRef(null);

  useEffect(() => {
    fetchQuiz();
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [quizId, user]);

  useEffect(() => {
    if (quiz && quiz.duration_minutes) {
      setTimeLeft(quiz.duration_minutes * 60);
      startTimer();
    }
  }, [quiz]);

  const fetchQuiz = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/quizzes/student/${quizId}/take?student_id=${user.id}`);
      const data = await response.json();
      
      if (data.success) {
        setQuiz(data.data);
      } else {
        toast.error(data.detail || 'Failed to load quiz');
        navigate('/student/quizzes');
      }
    } catch (error) {
      console.error('Error fetching quiz:', error);
      toast.error('Failed to load quiz');
      navigate('/student/quizzes');
    } finally {
      setLoading(false);
    }
  };

  const startTimer = () => {
    timerRef.current = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          handleSubmit(true); // Auto-submit when time runs out
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const handleAnswerChange = (questionId, answer) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const handleSubmit = async (autoSubmit = false) => {
    try {
      setSubmitting(true);
      
      if (!autoSubmit) {
        setShowSubmitModal(false);
      }

      const timeTaken = Math.floor((new Date() - startTime) / 1000 / 60);
      
      // Format answers for submission
      const formattedAnswers = quiz.questions.map(question => ({
        question_id: question.id,
        answer: answers[question.id] || ''
      }));

      const response = await fetch('http://localhost:8000/api/quizzes/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          quiz_id: quizId,
          student_id: user.id,
          answers: formattedAnswers,
          time_taken_minutes: timeTaken
        })
      });

      const data = await response.json();

      if (data.success) {
        toast.success('Quiz submitted successfully!');
        navigate(`/student/quiz/${quizId}/result`, { 
          state: { 
            score: data.data.score,
            totalMarks: data.data.total_marks,
            percentage: data.data.percentage
          }
        });
      } else {
        toast.error(data.detail || 'Failed to submit quiz');
      }
    } catch (error) {
      console.error('Error submitting quiz:', error);
      toast.error('Failed to submit quiz');
    } finally {
      setSubmitting(false);
    }
  };

  const getAnsweredCount = () => {
    return Object.keys(answers).filter(key => answers[key] && answers[key].toString().trim()).length;
  };

  const isTimeRunningOut = timeLeft <= 300; // 5 minutes

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  if (!quiz) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Quiz Not Found</h2>
          <p className="text-gray-600 mb-4">The quiz you're looking for doesn't exist or is not available.</p>
          <button
            onClick={() => navigate('/student/quizzes')}
            className="btn-primary"
          >
            Back to Quizzes
          </button>
        </div>
      </div>
    );
  }

  const currentQ = quiz.questions[currentQuestion];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/student/quizzes')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </button>
              <div>
                <h1 className="text-xl font-bold text-gray-900">{quiz.title}</h1>
                <div className="flex items-center space-x-4 text-sm text-gray-600">
                  <div className="flex items-center space-x-1">
                    <BookOpen className="w-4 h-4" />
                    <span>{quiz.courses?.title}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Award className="w-4 h-4" />
                    <span>{quiz.total_marks} marks</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-6">
              <div className="text-center">
                <div className="text-sm text-gray-600">Progress</div>
                <div className="font-semibold text-gray-900">
                  {currentQuestion + 1} / {quiz.questions.length}
                </div>
              </div>
              
              <div className="text-center">
                <div className="text-sm text-gray-600">Answered</div>
                <div className="font-semibold text-gray-900">
                  {getAnsweredCount()} / {quiz.questions.length}
                </div>
              </div>

              <div className={`text-center ${isTimeRunningOut ? 'text-red-600' : 'text-gray-900'}`}>
                <div className="text-sm text-gray-600">Time Left</div>
                <div className={`font-semibold flex items-center space-x-1 ${isTimeRunningOut ? 'animate-pulse' : ''}`}>
                  <Timer className="w-4 h-4" />
                  <span>{formatTime(timeLeft)}</span>
                </div>
              </div>

              <button
                onClick={() => setShowSubmitModal(true)}
                className="btn-success"
              >
                <Send className="w-4 h-4" />
                <span>Submit</span>
              </button>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${((currentQuestion + 1) / quiz.questions.length) * 100}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Question Content */}
      <div className="max-w-4xl mx-auto px-6 py-8">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentQuestion}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="bg-white rounded-2xl shadow-lg p-8"
          >
            <div className="mb-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">
                  Question {currentQuestion + 1}
                </h2>
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <Award className="w-4 h-4" />
                  <span>{currentQ.marks} mark{currentQ.marks !== 1 ? 's' : ''}</span>
                </div>
              </div>
              
              <p className="text-lg text-gray-800 leading-relaxed">
                {currentQ.question_text}
              </p>
            </div>

            {/* Answer Options */}
            <div className="space-y-4">
              {currentQ.question_type === 'mcq' && (
                <div className="space-y-3">
                  {currentQ.options.map((option, index) => (
                    <label
                      key={index}
                      className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                        answers[currentQ.id] === option.text
                          ? 'border-purple-500 bg-purple-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <input
                        type="radio"
                        name={`question-${currentQ.id}`}
                        value={option.text}
                        checked={answers[currentQ.id] === option.text}
                        onChange={(e) => handleAnswerChange(currentQ.id, e.target.value)}
                        className="sr-only"
                      />
                      <div className={`w-4 h-4 rounded-full border-2 mr-3 flex items-center justify-center ${
                        answers[currentQ.id] === option.text
                          ? 'border-purple-500 bg-purple-500'
                          : 'border-gray-300'
                      }`}>
                        {answers[currentQ.id] === option.text && (
                          <div className="w-2 h-2 rounded-full bg-white"></div>
                        )}
                      </div>
                      <span className="text-gray-800">{option.text}</span>
                    </label>
                  ))}
                </div>
              )}

              {currentQ.question_type === 'true_false' && (
                <div className="space-y-3">
                  {['True', 'False'].map((option) => (
                    <label
                      key={option}
                      className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all ${
                        answers[currentQ.id] === option.toLowerCase()
                          ? 'border-purple-500 bg-purple-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <input
                        type="radio"
                        name={`question-${currentQ.id}`}
                        value={option.toLowerCase()}
                        checked={answers[currentQ.id] === option.toLowerCase()}
                        onChange={(e) => handleAnswerChange(currentQ.id, e.target.value)}
                        className="sr-only"
                      />
                      <div className={`w-4 h-4 rounded-full border-2 mr-3 flex items-center justify-center ${
                        answers[currentQ.id] === option.toLowerCase()
                          ? 'border-purple-500 bg-purple-500'
                          : 'border-gray-300'
                      }`}>
                        {answers[currentQ.id] === option.toLowerCase() && (
                          <div className="w-2 h-2 rounded-full bg-white"></div>
                        )}
                      </div>
                      <span className="text-gray-800">{option}</span>
                    </label>
                  ))}
                </div>
              )}

              {currentQ.question_type === 'short_answer' && (
                <div>
                  <textarea
                    value={answers[currentQ.id] || ''}
                    onChange={(e) => handleAnswerChange(currentQ.id, e.target.value)}
                    placeholder="Type your answer here..."
                    className="w-full p-4 border-2 border-gray-200 rounded-lg focus:border-purple-500 focus:outline-none resize-none"
                    rows={4}
                  />
                </div>
              )}
            </div>

            {/* Navigation */}
            <div className="flex items-center justify-between mt-8 pt-6 border-t border-gray-200">
              <button
                onClick={() => setCurrentQuestion(prev => Math.max(0, prev - 1))}
                disabled={currentQuestion === 0}
                className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Previous</span>
              </button>

              <div className="flex items-center space-x-2">
                {quiz.questions.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentQuestion(index)}
                    className={`w-8 h-8 rounded-full text-sm font-medium transition-colors ${
                      index === currentQuestion
                        ? 'bg-purple-600 text-white'
                        : answers[quiz.questions[index].id]
                        ? 'bg-emerald-100 text-emerald-700 border border-emerald-300'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {index + 1}
                  </button>
                ))}
              </div>

              <button
                onClick={() => setCurrentQuestion(prev => Math.min(quiz.questions.length - 1, prev + 1))}
                disabled={currentQuestion === quiz.questions.length - 1}
                className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <span>Next</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Submit Confirmation Modal */}
      <AnimatePresence>
        {showSubmitModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white rounded-2xl p-6 max-w-md w-full"
            >
              <div className="text-center">
                <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Send className="w-8 h-8 text-emerald-600" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">Submit Quiz</h3>
                <p className="text-gray-700 mb-4">
                  You have answered {getAnsweredCount()} out of {quiz.questions.length} questions.
                </p>
                <p className="text-gray-600 mb-6">
                  Are you sure you want to submit? You won't be able to change your answers after submission.
                </p>
                <div className="flex items-center space-x-4">
                  <button
                    onClick={() => setShowSubmitModal(false)}
                    className="btn-ghost flex-1"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => handleSubmit()}
                    disabled={submitting}
                    className={`btn-success flex-1 ${submitting ? 'btn-loading' : ''}`}
                  >
                    {submitting ? 'Submitting...' : 'Submit Quiz'}
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default TakeQuiz;
