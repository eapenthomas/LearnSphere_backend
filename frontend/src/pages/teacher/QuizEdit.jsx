import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext.jsx';
import TeacherDashboardLayout from '../../layouts/TeacherDashboardLayout.jsx';
import { toast } from 'react-hot-toast';
import {
  ArrowLeft,
  Save,
  Plus,
  Trash2,
  Edit3,
  Hash,
  Clock,
  Calendar,
  FileText
} from 'lucide-react';

const QuizEdit = () => {
  const { quizId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [quiz, setQuiz] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (quizId && user?.id) {
      fetchQuiz();
    }
  }, [quizId, user?.id]);

  const fetchQuiz = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/quizzes/${quizId}`);
      const data = await response.json();
      
      if (data.success) {
        // Format the quiz data for editing
        const quizData = data.data;
        setQuiz({
          id: quizData.id,
          title: quizData.title || '',
          description: quizData.description || '',
          instructions: quizData.instructions || '',
          duration_minutes: quizData.duration_minutes || 30,
          start_time: quizData.start_time ? new Date(quizData.start_time).toISOString().slice(0, 16) : '',
          end_time: quizData.end_time ? new Date(quizData.end_time).toISOString().slice(0, 16) : '',
          status: quizData.status || 'draft',
          questions: quizData.questions || []
        });
      } else {
        toast.error('Failed to load quiz');
        navigate('/teacher/quizzes');
      }
    } catch (error) {
      console.error('Error fetching quiz:', error);
      toast.error('Failed to load quiz');
      navigate('/teacher/quizzes');
    } finally {
      setLoading(false);
    }
  };

  const handleQuizInfoChange = (field, value) => {
    setQuiz(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleQuestionChange = (index, field, value) => {
    setQuiz(prev => ({
      ...prev,
      questions: prev.questions.map((q, i) => 
        i === index ? { ...q, [field]: value } : q
      )
    }));
  };

  const handleOptionChange = (questionIndex, optionIndex, value) => {
    setQuiz(prev => ({
      ...prev,
      questions: prev.questions.map((q, i) => 
        i === questionIndex 
          ? { 
              ...q, 
              options: q.options.map((opt, oi) => 
                oi === optionIndex 
                  ? (typeof opt === 'object' ? { ...opt, text: value } : value)
                  : opt
              )
            } 
          : q
      )
    }));
  };

  const addQuestion = () => {
    const newQuestion = {
      question_text: '',
      question_type: 'mcq',
      options: [{ text: '', is_correct: false }, { text: '', is_correct: false }],
      correct_answer: '',
      marks: 1
    };
    
    setQuiz(prev => ({
      ...prev,
      questions: [...prev.questions, newQuestion]
    }));
  };

  const removeQuestion = (index) => {
    setQuiz(prev => ({
      ...prev,
      questions: prev.questions.filter((_, i) => i !== index)
    }));
  };

  const addOption = (questionIndex) => {
    setQuiz(prev => ({
      ...prev,
      questions: prev.questions.map((q, i) => 
        i === questionIndex 
          ? { 
              ...q, 
              options: [...(q.options || []), { text: '', is_correct: false }]
            }
          : q
      )
    }));
  };

  const removeOption = (questionIndex, optionIndex) => {
    setQuiz(prev => ({
      ...prev,
      questions: prev.questions.map((q, i) => 
        i === questionIndex 
          ? { 
              ...q, 
              options: q.options.filter((_, oi) => oi !== optionIndex)
            }
          : q
      )
    }));
  };

  const handleSave = async () => {
    try {
      // Validate quiz
      if (!quiz.title.trim()) {
        toast.error('Please enter a quiz title');
        return;
      }

      if (quiz.questions.length === 0) {
        toast.error('Please add at least one question');
        return;
      }

      // Validate questions
      for (let i = 0; i < quiz.questions.length; i++) {
        const q = quiz.questions[i];
        if (!q.question_text.trim()) {
          toast.error(`Question ${i + 1} is empty`);
          return;
        }
        if (q.question_type === 'mcq' && (!q.options || q.options.length < 2)) {
          toast.error(`Question ${i + 1} needs at least 2 options`);
          return;
        }
      }

      setSaving(true);

      // Prepare update data
      const updateData = {
        title: quiz.title,
        description: quiz.description,
        instructions: quiz.instructions,
        duration_minutes: quiz.duration_minutes,
        start_time: quiz.start_time || null,
        end_time: quiz.end_time || null,
        questions: quiz.questions.map(q => ({
          question_text: q.question_text,
          question_type: q.question_type,
          options: q.question_type === 'mcq' ? q.options : null,
          correct_answer: q.question_type !== 'mcq' ? q.correct_answer : null,
          marks: q.marks || 1
        }))
      };

      const response = await fetch(`http://localhost:8000/api/quizzes/${quizId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData)
      });

      if (response.ok) {
        toast.success('Quiz updated successfully!');
        navigate('/teacher/quizzes');
      } else {
        const errorData = await response.json();
        toast.error(errorData.detail || 'Failed to update quiz');
      }
    } catch (error) {
      console.error('Error saving quiz:', error);
      toast.error('Failed to update quiz');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <TeacherDashboardLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading quiz...</p>
          </div>
        </div>
      </TeacherDashboardLayout>
    );
  }

  if (!quiz) {
    return (
      <TeacherDashboardLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <p className="text-gray-600">Quiz not found</p>
          </div>
        </div>
      </TeacherDashboardLayout>
    );
  }

  return (
    <TeacherDashboardLayout>
      <div className="p-6 space-y-6 teacher-page-bg min-h-screen">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="teacher-course-card rounded-2xl shadow-lg p-6"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/teacher/quizzes')}
                className="btn-primary px-4 py-2 rounded-lg flex items-center space-x-2"
              >
                <ArrowLeft className="w-5 h-5" />
                <span>Back to Quizzes</span>
              </button>
              
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Edit Quiz</h1>
                <p className="text-gray-600">Modify quiz details and questions</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <Hash className="w-4 h-4" />
                <span>{quiz.questions.length} questions</span>
              </div>
              
              <button
                onClick={handleSave}
                disabled={saving}
                className="btn-success px-6 py-2 rounded-lg flex items-center space-x-2"
              >
                <Save className="w-4 h-4" />
                <span>{saving ? 'Saving...' : 'Save Changes'}</span>
              </button>
            </div>
          </div>
        </motion.div>

        {/* Quiz Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="teacher-course-card rounded-2xl shadow-lg p-6 space-y-4"
        >
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quiz Information</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Quiz Title
              </label>
              <input
                type="text"
                value={quiz.title}
                onChange={(e) => handleQuizInfoChange('title', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter quiz title"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Duration (minutes)
              </label>
              <input
                type="number"
                value={quiz.duration_minutes}
                onChange={(e) => handleQuizInfoChange('duration_minutes', parseInt(e.target.value) || 30)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                min="1"
                max="300"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              value={quiz.description}
              onChange={(e) => handleQuizInfoChange('description', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows="3"
              placeholder="Enter quiz description"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Instructions
            </label>
            <textarea
              value={quiz.instructions}
              onChange={(e) => handleQuizInfoChange('instructions', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows="2"
              placeholder="Enter quiz instructions"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Start Time (optional)
              </label>
              <input
                type="datetime-local"
                value={quiz.start_time}
                onChange={(e) => handleQuizInfoChange('start_time', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                End Time (optional)
              </label>
              <input
                type="datetime-local"
                value={quiz.end_time}
                onChange={(e) => handleQuizInfoChange('end_time', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
        </motion.div>

        {/* Questions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="space-y-4"
        >
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Questions</h2>
            <button
              onClick={addQuestion}
              className="btn-primary px-4 py-2 rounded-lg flex items-center space-x-2"
            >
              <Plus className="w-4 h-4" />
              <span>Add Question</span>
            </button>
          </div>

          {quiz.questions.map((question, index) => (
            <div key={index} className="teacher-course-card rounded-2xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <span className="bg-blue-100 text-blue-600 text-sm font-medium px-3 py-1 rounded-full">
                    Question {index + 1}
                  </span>
                  <select
                    value={question.question_type}
                    onChange={(e) => handleQuestionChange(index, 'question_type', e.target.value)}
                    className="text-sm border border-gray-300 rounded px-2 py-1"
                  >
                    <option value="mcq">Multiple Choice</option>
                    <option value="true_false">True/False</option>
                    <option value="short_answer">Short Answer</option>
                  </select>
                </div>
                
                <button
                  onClick={() => removeQuestion(index)}
                  className="text-red-600 hover:text-red-700 p-1"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Question Text
                  </label>
                  <textarea
                    value={question.question_text}
                    onChange={(e) => handleQuestionChange(index, 'question_text', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows="2"
                    placeholder="Enter your question"
                  />
                </div>

                {question.question_type === 'mcq' && (
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="block text-sm font-medium text-gray-700">
                        Options
                      </label>
                      <button
                        onClick={() => addOption(index)}
                        className="text-blue-600 hover:text-blue-700 text-sm flex items-center space-x-1"
                      >
                        <Plus className="w-3 h-3" />
                        <span>Add Option</span>
                      </button>
                    </div>
                    
                    <div className="space-y-2">
                      {question.options?.map((option, optionIndex) => (
                        <div key={optionIndex} className="flex items-center space-x-2">
                          <input
                            type="radio"
                            name={`question-${index}-correct`}
                            checked={typeof option === 'object' ? option.is_correct : false}
                            onChange={() => {
                              // Mark this option as correct
                              setQuiz(prev => ({
                                ...prev,
                                questions: prev.questions.map((q, i) => 
                                  i === index 
                                    ? {
                                        ...q,
                                        options: q.options.map((opt, oi) => ({
                                          text: typeof opt === 'object' ? opt.text : opt,
                                          is_correct: oi === optionIndex
                                        }))
                                      }
                                    : q
                                )
                              }));
                            }}
                            className="text-blue-600"
                          />
                          <input
                            type="text"
                            value={typeof option === 'object' ? option.text : option}
                            onChange={(e) => handleOptionChange(index, optionIndex, e.target.value)}
                            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder={`Option ${optionIndex + 1}`}
                          />
                          {question.options.length > 2 && (
                            <button
                              onClick={() => removeOption(index, optionIndex)}
                              className="text-red-600 hover:text-red-700 p-1"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {question.question_type !== 'mcq' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Correct Answer
                    </label>
                    <input
                      type="text"
                      value={question.correct_answer || ''}
                      onChange={(e) => handleQuestionChange(index, 'correct_answer', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter the correct answer"
                    />
                  </div>
                )}

                <div className="w-24">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Marks
                  </label>
                  <input
                    type="number"
                    value={question.marks || 1}
                    onChange={(e) => handleQuestionChange(index, 'marks', parseInt(e.target.value) || 1)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    min="1"
                    max="10"
                  />
                </div>
              </div>
            </div>
          ))}

          {quiz.questions.length === 0 && (
            <div className="text-center py-12 teacher-course-card rounded-2xl shadow-lg">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-4">No questions added yet</p>
              <button
                onClick={addQuestion}
                className="btn-primary px-6 py-2 rounded-lg flex items-center space-x-2 mx-auto"
              >
                <Plus className="w-4 h-4" />
                <span>Add First Question</span>
              </button>
            </div>
          )}
        </motion.div>
      </div>
    </TeacherDashboardLayout>
  );
};

export default QuizEdit;
