import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext.jsx';
import { toast } from 'react-hot-toast';
import {
  X,
  Plus,
  Trash2,
  BookOpen,
  Clock,
  Calendar,
  FileText,
  Award,
  Save,
  Eye
} from 'lucide-react';

const CreateQuizModal = ({ isOpen, onClose, onQuizCreated }) => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [courses, setCourses] = useState([]);
  const [currentStep, setCurrentStep] = useState(1);
  
  // Quiz basic info
  const [quizData, setQuizData] = useState({
    title: '',
    description: '',
    course_id: '',
    instructions: '',
    duration_minutes: 60,
    start_time: '',
    end_time: ''
  });

  // Questions
  const [questions, setQuestions] = useState([
    {
      question_text: '',
      question_type: 'mcq',
      options: [
        { text: '', is_correct: false },
        { text: '', is_correct: false },
        { text: '', is_correct: false },
        { text: '', is_correct: false }
      ],
      correct_answer: '',
      marks: 1
    }
  ]);

  useEffect(() => {
    if (isOpen) {
      fetchCourses();
    }
  }, [isOpen, user]);

  const fetchCourses = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/quizzes/courses/${user.id}`);
      const data = await response.json();
      
      if (data.success) {
        setCourses(data.data);
      }
    } catch (error) {
      console.error('Error fetching courses:', error);
      toast.error('Failed to load courses');
    }
  };

  const handleQuizDataChange = (field, value) => {
    setQuizData(prev => ({ ...prev, [field]: value }));
  };

  const handleQuestionChange = (questionIndex, field, value) => {
    setQuestions(prev => prev.map((q, i) => 
      i === questionIndex ? { ...q, [field]: value } : q
    ));
  };

  const handleOptionChange = (questionIndex, optionIndex, field, value) => {
    setQuestions(prev => prev.map((q, i) => {
      if (i === questionIndex) {
        const newOptions = q.options.map((opt, j) => {
          if (j === optionIndex) {
            return { ...opt, [field]: value };
          }
          // If setting this option as correct, unset others
          if (field === 'is_correct' && value === true) {
            return { ...opt, is_correct: false };
          }
          return opt;
        });
        return { ...q, options: newOptions };
      }
      return q;
    }));
  };

  const addQuestion = () => {
    setQuestions(prev => [...prev, {
      question_text: '',
      question_type: 'mcq',
      options: [
        { text: '', is_correct: false },
        { text: '', is_correct: false },
        { text: '', is_correct: false },
        { text: '', is_correct: false }
      ],
      correct_answer: '',
      marks: 1
    }]);
  };

  const removeQuestion = (index) => {
    if (questions.length > 1) {
      setQuestions(prev => prev.filter((_, i) => i !== index));
    }
  };

  const addOption = (questionIndex) => {
    setQuestions(prev => prev.map((q, i) => 
      i === questionIndex 
        ? { ...q, options: [...q.options, { text: '', is_correct: false }] }
        : q
    ));
  };

  const removeOption = (questionIndex, optionIndex) => {
    setQuestions(prev => prev.map((q, i) => 
      i === questionIndex && q.options.length > 2
        ? { ...q, options: q.options.filter((_, j) => j !== optionIndex) }
        : q
    ));
  };

  const validateQuiz = () => {
    if (!quizData.title.trim()) {
      toast.error('Quiz title is required');
      return false;
    }
    
    if (!quizData.course_id) {
      toast.error('Please select a course');
      return false;
    }

    for (let i = 0; i < questions.length; i++) {
      const question = questions[i];
      
      if (!question.question_text.trim()) {
        toast.error(`Question ${i + 1} text is required`);
        return false;
      }

      if (question.question_type === 'mcq') {
        const validOptions = question.options.filter(opt => opt.text.trim());
        if (validOptions.length < 2) {
          toast.error(`Question ${i + 1} must have at least 2 options`);
          return false;
        }
        
        const correctOptions = question.options.filter(opt => opt.is_correct);
        if (correctOptions.length !== 1) {
          toast.error(`Question ${i + 1} must have exactly one correct answer`);
          return false;
        }
      } else if (question.question_type === 'true_false') {
        if (!question.correct_answer) {
          toast.error(`Question ${i + 1} must have a correct answer selected`);
          return false;
        }
      } else if (question.question_type === 'short_answer') {
        if (!question.correct_answer.trim()) {
          toast.error(`Question ${i + 1} must have a correct answer`);
          return false;
        }
      }
    }

    return true;
  };

  const handleSubmit = async () => {
    if (!validateQuiz()) return;

    try {
      setLoading(true);
      
      const response = await fetch(`http://localhost:8000/api/quizzes/create?teacher_id=${user.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...quizData,
          questions: questions.map(q => ({
            ...q,
            options: q.question_type === 'mcq' ? q.options.filter(opt => opt.text.trim()) : undefined
          }))
        })
      });

      const data = await response.json();

      if (data.success) {
        toast.success('Quiz created successfully!');
        onQuizCreated();
        onClose();
        resetForm();
      } else {
        toast.error('Failed to create quiz');
      }
    } catch (error) {
      console.error('Error creating quiz:', error);
      toast.error('Failed to create quiz');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setQuizData({
      title: '',
      description: '',
      course_id: '',
      instructions: '',
      duration_minutes: 60,
      start_time: '',
      end_time: ''
    });
    setQuestions([{
      question_text: '',
      question_type: 'mcq',
      options: [
        { text: '', is_correct: false },
        { text: '', is_correct: false },
        { text: '', is_correct: false },
        { text: '', is_correct: false }
      ],
      correct_answer: '',
      marks: 1
    }]);
    setCurrentStep(1);
  };

  const totalMarks = questions.reduce((sum, q) => sum + q.marks, 0);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-white shadow rounded-xl border border-gray-200 max-w-4xl w-full max-h-[95vh] overflow-hidden flex flex-col"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Create New Quiz</h2>
            <p className="text-gray-700" style={{ color: '#374151' }}>Step {currentStep} of 2</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-6 h-6 text-gray-600" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="px-6 py-4 bg-gray-50">
          <div className="flex items-center space-x-4">
            <div className={`flex items-center space-x-2 ${currentStep >= 1 ? 'text-purple-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${currentStep >= 1 ? 'bg-purple-600 text-white' : 'bg-gray-200'}`}>
                1
              </div>
              <span className="font-medium">Quiz Details</span>
            </div>
            <div className={`flex-1 h-1 ${currentStep >= 2 ? 'bg-purple-600' : 'bg-gray-200'} rounded`}></div>
            <div className={`flex items-center space-x-2 ${currentStep >= 2 ? 'text-purple-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${currentStep >= 2 ? 'bg-purple-600 text-white' : 'bg-gray-200'}`}>
                2
              </div>
              <span className="font-medium">Questions</span>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto flex-1 min-h-0">
          {currentStep === 1 ? (
            <div className="space-y-6">
              {/* Basic Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-900 mb-2">
                    Quiz Title *
                  </label>
                  <input
                    type="text"
                    value={quizData.title}
                    onChange={(e) => handleQuizDataChange('title', e.target.value)}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white placeholder-gray-500 text-black"
                    style={{ color: '#000000 !important', backgroundColor: '#ffffff !important' }}
                    placeholder="Enter quiz title"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-900 mb-2">
                    Course *
                  </label>
                  <select
                    value={quizData.course_id}
                    onChange={(e) => handleQuizDataChange('course_id', e.target.value)}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent text-black bg-white"
                    style={{ color: '#000000 !important', backgroundColor: '#ffffff !important' }}
                  >
                    <option value="">Select a course</option>
                    {courses.map(course => (
                      <option key={course.id} value={course.id}>
                        {course.title} ({course.code})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Description
                </label>
                <textarea
                  value={quizData.description}
                  onChange={(e) => handleQuizDataChange('description', e.target.value)}
                  rows={3}
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white placeholder-gray-500 text-black"
                  style={{ color: '#000000 !important', backgroundColor: '#ffffff !important' }}
                  placeholder="Brief description of the quiz"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-900 mb-2">
                  Instructions
                </label>
                <textarea
                  value={quizData.instructions}
                  onChange={(e) => handleQuizDataChange('instructions', e.target.value)}
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white placeholder-gray-500 text-black"
                  style={{ color: '#000000 !important', backgroundColor: '#ffffff !important' }}
                  placeholder="Instructions for students taking the quiz"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-900 mb-2">
                    Duration (minutes)
                  </label>
                  <input
                    type="number"
                    value={quizData.duration_minutes}
                    onChange={(e) => handleQuizDataChange('duration_minutes', parseInt(e.target.value))}
                    min="1"
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white text-black"
                    style={{ color: '#000000 !important', backgroundColor: '#ffffff !important' }}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-900 mb-2">
                    Start Time (Optional)
                  </label>
                  <input
                    type="datetime-local"
                    value={quizData.start_time}
                    onChange={(e) => handleQuizDataChange('start_time', e.target.value)}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent text-black bg-white"
                    style={{ color: '#000000 !important', backgroundColor: '#ffffff !important' }}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-900 mb-2">
                    End Time (Optional)
                  </label>
                  <input
                    type="datetime-local"
                    value={quizData.end_time}
                    onChange={(e) => handleQuizDataChange('end_time', e.target.value)}
                    className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent text-black bg-white"
                    style={{ color: '#000000 !important', backgroundColor: '#ffffff !important' }}
                  />
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Questions Header */}
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold" style={{ color: '#000000' }}>Quiz Questions</h3>
                  <p className="text-sm" style={{ color: '#374151' }}>
                    {questions.length} question{questions.length !== 1 ? 's' : ''} • Total: {totalMarks} mark{totalMarks !== 1 ? 's' : ''}
                  </p>
                </div>
                <button
                  onClick={addQuestion}
                  className="btn-primary btn-sm"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Question</span>
                </button>
              </div>

              {/* Questions List */}
              <div className="space-y-6">
                {questions.map((question, questionIndex) => (
                  <div key={questionIndex} className="border border-gray-200 rounded-xl p-6">
                    <div className="flex items-start justify-between mb-4">
                      <h4 className="text-lg font-medium text-gray-900">
                        Question {questionIndex + 1}
                      </h4>
                      <div className="flex items-center space-x-2">
                        <div className="flex items-center space-x-2">
                          <label className="text-sm text-gray-700">Marks:</label>
                          <input
                            type="number"
                            value={question.marks}
                            onChange={(e) => handleQuestionChange(questionIndex, 'marks', parseInt(e.target.value) || 1)}
                            min="1"
                            className="w-16 px-2 py-1 border border-gray-200 rounded text-center text-black bg-white"
                            style={{ color: '#000000 !important', backgroundColor: '#ffffff !important' }}
                          />
                        </div>
                        {questions.length > 1 && (
                          <button
                            onClick={() => removeQuestion(questionIndex)}
                            className="btn-icon-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </div>

                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-900 mb-2">
                          Question Text *
                        </label>
                        <textarea
                          value={question.question_text}
                          onChange={(e) => handleQuestionChange(questionIndex, 'question_text', e.target.value)}
                          rows={2}
                          className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white placeholder-gray-500 text-black"
                          style={{ color: '#000000 !important', backgroundColor: '#ffffff !important' }}
                          placeholder="Enter your question"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-900 mb-2">
                          Question Type
                        </label>
                        <select
                          value={question.question_type}
                          onChange={(e) => handleQuestionChange(questionIndex, 'question_type', e.target.value)}
                          className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent text-black bg-white"
                          style={{ color: '#000000 !important', backgroundColor: '#ffffff !important' }}
                        >
                          <option value="mcq">Multiple Choice</option>
                          <option value="true_false">True/False</option>
                          <option value="short_answer">Short Answer</option>
                        </select>
                      </div>

                      {/* Question Type Specific Fields */}
                      {question.question_type === 'mcq' && (
                        <div>
                          <div className="flex items-center justify-between mb-3">
                            <label className="text-sm font-medium text-gray-900">
                              Options (Select the correct answer)
                            </label>
                            <button
                              onClick={() => addOption(questionIndex)}
                              className="btn-ghost-primary btn-sm"
                            >
                              + Add Option
                            </button>
                          </div>
                          <div className="space-y-2">
                            {question.options.map((option, optionIndex) => (
                              <div key={optionIndex} className="flex items-center space-x-3">
                                <input
                                  type="radio"
                                  name={`question-${questionIndex}-correct`}
                                  checked={option.is_correct}
                                  onChange={(e) => handleOptionChange(questionIndex, optionIndex, 'is_correct', e.target.checked)}
                                  className="text-purple-600"
                                />
                                <input
                                  type="text"
                                  value={option.text}
                                  onChange={(e) => handleOptionChange(questionIndex, optionIndex, 'text', e.target.value)}
                                  className="flex-1 px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white placeholder-gray-500 text-black"
                                  style={{ color: '#000000 !important', backgroundColor: '#ffffff !important' }}
                                  placeholder={`Option ${optionIndex + 1}`}
                                />
                                {question.options.length > 2 && (
                                  <button
                                    onClick={() => removeOption(questionIndex, optionIndex)}
                                    className="btn-icon-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                                  >
                                    <Trash2 className="w-4 h-4" />
                                  </button>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {question.question_type === 'true_false' && (
                        <div>
                          <label className="block text-sm font-medium text-gray-900 mb-2">
                            Correct Answer
                          </label>
                          <div className="flex items-center space-x-4">
                            <label className="flex items-center space-x-2">
                              <input
                                type="radio"
                                name={`question-${questionIndex}-tf`}
                                value="true"
                                checked={question.correct_answer === 'true'}
                                onChange={(e) => handleQuestionChange(questionIndex, 'correct_answer', e.target.value)}
                                className="text-purple-600"
                              />
                              <span>True</span>
                            </label>
                            <label className="flex items-center space-x-2">
                              <input
                                type="radio"
                                name={`question-${questionIndex}-tf`}
                                value="false"
                                checked={question.correct_answer === 'false'}
                                onChange={(e) => handleQuestionChange(questionIndex, 'correct_answer', e.target.value)}
                                className="text-purple-600"
                              />
                              <span>False</span>
                            </label>
                          </div>
                        </div>
                      )}

                      {question.question_type === 'short_answer' && (
                        <div>
                          <label className="block text-sm font-medium text-gray-900 mb-2">
                            Correct Answer
                          </label>
                          <input
                            type="text"
                            value={question.correct_answer}
                            onChange={(e) => handleQuestionChange(questionIndex, 'correct_answer', e.target.value)}
                            className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white placeholder-gray-500 text-black"
                            style={{ color: '#000000 !important', backgroundColor: '#ffffff !important' }}
                            placeholder="Enter the correct answer"
                          />
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200">
          <div className="flex items-center space-x-4">
            {currentStep === 2 && (
              <button
                onClick={() => setCurrentStep(1)}
                className="btn-ghost"
              >
                Back
              </button>
            )}
          </div>

          <div className="flex items-center space-x-4">
            <button
              onClick={onClose}
              className="btn-ghost"
            >
              Cancel
            </button>
            
            {currentStep === 1 ? (
              <button
                onClick={() => setCurrentStep(2)}
                disabled={!quizData.title || !quizData.course_id}
                className="btn-primary"
              >
                Next: Add Questions
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={loading}
                className={`btn-primary ${loading ? 'btn-loading' : ''}`}
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Creating...</span>
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    <span>Create Quiz</span>
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default CreateQuizModal;
