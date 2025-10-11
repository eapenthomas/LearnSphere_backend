import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext.jsx';
import TeacherDashboardLayout from '../../layouts/TeacherDashboardLayout.jsx';
import { toast } from 'react-hot-toast';
import {
  MessageSquare,
  Search,
  Filter,
  Clock,
  CheckCircle,
  User,
  BookOpen,
  Tag,
  Send,
  X,
  AlertCircle,
  MessageCircle,
  Reply
} from 'lucide-react';

const TeacherForum = () => {
  const { user } = useAuth();
  const [questions, setQuestions] = useState([]);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [showQuestionModal, setShowQuestionModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCourse, setFilterCourse] = useState('');
  const [filterResolved, setFilterResolved] = useState('all');
  const [answerContent, setAnswerContent] = useState('');
  const [submittingAnswer, setSubmittingAnswer] = useState(false);

  useEffect(() => {
    if (user?.id) {
      fetchQuestions();
      fetchCourses();
    }
  }, [user, filterCourse, filterResolved]);

  const fetchQuestions = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      
      if (filterCourse) params.append('course_id', filterCourse);
      if (filterResolved !== 'all') params.append('resolved', filterResolved === 'resolved');
      
      const response = await fetch(`http://localhost:8000/api/forum/questions?${params}`);
      if (response.ok) {
        const data = await response.json();
        setQuestions(data);
      } else {
        throw new Error('Failed to fetch questions');
      }
    } catch (error) {
      console.error('Error fetching questions:', error);
      toast.error('Failed to load forum questions');
    } finally {
      setLoading(false);
    }
  };

  const fetchCourses = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/courses/teacher/${user.id}`);
      if (response.ok) {
        const data = await response.json();
        const coursesArray = Array.isArray(data) ? data : [];
        setCourses(coursesArray);
      }
    } catch (error) {
      console.error('Error fetching courses:', error);
      setCourses([]); // Set empty array on error
    }
  };

  const fetchQuestionDetails = async (questionId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/forum/questions/${questionId}`);
      if (response.ok) {
        const data = await response.json();
        setSelectedQuestion(data);
        setShowQuestionModal(true);
      } else {
        throw new Error('Failed to fetch question details');
      }
    } catch (error) {
      console.error('Error fetching question details:', error);
      toast.error('Failed to load question details');
    }
  };

  const handleSubmitAnswer = async (e) => {
    e.preventDefault();
    
    if (!answerContent.trim()) {
      toast.error('Please enter an answer');
      return;
    }

    try {
      setSubmittingAnswer(true);
      const response = await fetch(`http://localhost:8000/api/forum/answers?teacher_id=${user.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question_id: selectedQuestion.question.id,
          content: answerContent
        }),
      });

      if (response.ok) {
        toast.success('Answer posted successfully!');
        setAnswerContent('');
        fetchQuestionDetails(selectedQuestion.question.id);
        fetchQuestions();
      } else {
        throw new Error('Failed to post answer');
      }
    } catch (error) {
      console.error('Error posting answer:', error);
      toast.error('Failed to post answer');
    } finally {
      setSubmittingAnswer(false);
    }
  };

  const filteredQuestions = questions.filter(question =>
    question.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    question.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
    question.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <TeacherDashboardLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
        </div>
      </TeacherDashboardLayout>
    );
  }

  return (
    <TeacherDashboardLayout>
      <div className="space-y-8 p-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4"
        >
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Student Questions</h1>
            <p className="text-gray-600">Help students by answering their questions</p>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="bg-white rounded-lg px-4 py-2 shadow-sm border">
              <span className="text-sm text-gray-600">
                {filteredQuestions.filter(q => !q.is_resolved).length} unanswered questions
              </span>
            </div>
          </div>
        </motion.div>

        {/* Search and Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-2xl shadow-lg p-6"
        >
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search questions..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            
            {/* Course Filter */}
            <select
              value={filterCourse}
              onChange={(e) => setFilterCourse(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="">All Courses</option>
              {courses && courses.length > 0 ? courses.map(course => (
                <option key={course.id} value={course.id}>{course.title}</option>
              )) : (
                <option value="" disabled>No courses available</option>
              )}
            </select>
            
            {/* Status Filter */}
            <select
              value={filterResolved}
              onChange={(e) => setFilterResolved(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="all">All Questions</option>
              <option value="unresolved">Unanswered</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>
        </motion.div>

        {/* Questions List */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="space-y-4"
        >
          {filteredQuestions.length === 0 ? (
            <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
              <MessageSquare className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No questions found</h3>
              <p className="text-gray-600">Students haven't asked any questions yet.</p>
            </div>
          ) : (
            filteredQuestions.map((question, index) => (
              <motion.div
                key={question.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`bg-white rounded-2xl shadow-lg p-6 hover:shadow-xl transition-all duration-300 cursor-pointer border-l-4 ${
                  question.is_resolved ? 'border-green-400' : 
                  question.answer_count === 0 ? 'border-red-400' : 'border-yellow-400'
                }`}
                onClick={() => fetchQuestionDetails(question.id)}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">{question.title}</h3>
                      {question.is_resolved && (
                        <CheckCircle className="w-5 h-5 text-green-500" />
                      )}
                      {question.answer_count === 0 && !question.is_resolved && (
                        <AlertCircle className="w-5 h-5 text-red-500" />
                      )}
                    </div>
                    <p className="text-gray-600 line-clamp-2">{question.content}</p>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <div className="flex items-center space-x-1">
                      <User className="w-4 h-4" />
                      <span>{question.student_name}</span>
                    </div>
                    {question.course_name && (
                      <div className="flex items-center space-x-1">
                        <BookOpen className="w-4 h-4" />
                        <span>{question.course_name}</span>
                      </div>
                    )}
                    <div className="flex items-center space-x-1">
                      <Clock className="w-4 h-4" />
                      <span>{formatDate(question.created_at)}</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-1 text-sm text-gray-500">
                      <MessageCircle className="w-4 h-4" />
                      <span>{question.answer_count} answers</span>
                    </div>
                    {question.answer_count === 0 && !question.is_resolved && (
                      <span className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full font-medium">
                        Needs Answer
                      </span>
                    )}
                    {question.tags.length > 0 && (
                      <div className="flex items-center space-x-1">
                        {question.tags.slice(0, 2).map(tag => (
                          <span key={tag} className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">
                            {tag}
                          </span>
                        ))}
                        {question.tags.length > 2 && (
                          <span className="text-xs text-gray-500">+{question.tags.length - 2}</span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            ))
          )}
        </motion.div>

        {/* Question Details Modal */}
        <AnimatePresence>
          {showQuestionModal && selectedQuestion && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
              onClick={() => setShowQuestionModal(false)}
            >
              <motion.div
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.95, opacity: 0 }}
                className="bg-white rounded-2xl shadow-xl max-w-4xl w-full p-6 max-h-[90vh] overflow-y-auto"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">Answer Student Question</h2>
                  <button
                    onClick={() => setShowQuestionModal(false)}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                {/* Question */}
                <div className="bg-gray-50 rounded-lg p-6 mb-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-semibold text-gray-900">{selectedQuestion.question.title}</h3>
                    {selectedQuestion.question.is_resolved && (
                      <span className="flex items-center space-x-1 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                        <CheckCircle className="w-4 h-4" />
                        <span>Resolved</span>
                      </span>
                    )}
                  </div>

                  <p className="text-gray-700 mb-4 whitespace-pre-wrap">{selectedQuestion.question.content}</p>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <div className="flex items-center space-x-1">
                        <User className="w-4 h-4" />
                        <span>{selectedQuestion.question.student_name}</span>
                      </div>
                      {selectedQuestion.question.course_name && (
                        <div className="flex items-center space-x-1">
                          <BookOpen className="w-4 h-4" />
                          <span>{selectedQuestion.question.course_name}</span>
                        </div>
                      )}
                      <div className="flex items-center space-x-1">
                        <Clock className="w-4 h-4" />
                        <span>{formatDate(selectedQuestion.question.created_at)}</span>
                      </div>
                    </div>

                    {selectedQuestion.question.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {selectedQuestion.question.tags.map(tag => (
                          <span key={tag} className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {/* Existing Answers */}
                {selectedQuestion.answers.length > 0 && (
                  <div className="mb-6">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4">
                      Previous Answers ({selectedQuestion.answers.length})
                    </h4>

                    <div className="space-y-4">
                      {selectedQuestion.answers.map((answer, index) => (
                        <motion.div
                          key={answer.id}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.1 }}
                          className={`p-4 rounded-lg border-l-4 ${
                            answer.is_accepted
                              ? 'bg-green-50 border-green-400'
                              : 'bg-white border-gray-200'
                          }`}
                        >
                          <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center space-x-2">
                              <div className="flex items-center space-x-1 text-sm text-gray-600">
                                <User className="w-4 h-4" />
                                <span className="font-medium">{answer.teacher_name}</span>
                                <span className="text-gray-400">•</span>
                                <span>{formatDate(answer.created_at)}</span>
                              </div>
                              {answer.is_accepted && (
                                <span className="flex items-center space-x-1 px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs">
                                  <CheckCircle className="w-3 h-3" />
                                  <span>Accepted Answer</span>
                                </span>
                              )}
                            </div>
                          </div>

                          <p className="text-gray-700 whitespace-pre-wrap">{answer.content}</p>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Answer Form */}
                {!selectedQuestion.question.is_resolved && (
                  <div className="border-t border-gray-200 pt-6">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                      <Reply className="w-5 h-5 mr-2" />
                      Your Answer
                    </h4>

                    <form onSubmit={handleSubmitAnswer} className="space-y-4">
                      <div>
                        <textarea
                          value={answerContent}
                          onChange={(e) => setAnswerContent(e.target.value)}
                          rows={6}
                          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                          placeholder="Write your answer here... Be detailed and helpful!"
                          required
                        />
                      </div>

                      <div className="flex justify-end space-x-4">
                        <button
                          type="button"
                          onClick={() => setShowQuestionModal(false)}
                          className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                        >
                          Cancel
                        </button>
                        <button
                          type="submit"
                          disabled={submittingAnswer}
                          className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center space-x-2 disabled:opacity-50"
                        >
                          <Send className="w-4 h-4" />
                          <span>{submittingAnswer ? 'Posting...' : 'Post Answer'}</span>
                        </button>
                      </div>
                    </form>
                  </div>
                )}

                {selectedQuestion.question.is_resolved && (
                  <div className="border-t border-gray-200 pt-6">
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                      <CheckCircle className="w-8 h-8 text-green-500 mx-auto mb-2" />
                      <p className="text-green-700 font-medium">This question has been resolved</p>
                      <p className="text-green-600 text-sm">The student has marked this question as answered</p>
                    </div>
                  </div>
                )}
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </TeacherDashboardLayout>
  );
};

export default TeacherForum;
