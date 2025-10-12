import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import {
  Edit3,
  Save,
  Trash2,
  Plus,
  Check,
  X,
  Clock,
  Hash,
  BookOpen,
  AlertCircle
} from 'lucide-react';

const QuizEditor = ({ generatedQuiz, onSave, onCancel, saving }) => {
  const [quiz, setQuiz] = useState({
    title: generatedQuiz.title || '',
    description: generatedQuiz.description || '',
    estimated_time: generatedQuiz.estimated_time || 30,
    questions: generatedQuiz.questions || [],
    instructions: '',
    start_time: '',
    end_time: ''
  });

  const [editingQuestion, setEditingQuestion] = useState(null);

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
              options: q.options.map((opt, oi) => oi === optionIndex ? value : opt)
            } 
          : q
      )
    }));
  };

  const addOption = (questionIndex) => {
    setQuiz(prev => ({
      ...prev,
      questions: prev.questions.map((q, i) => 
        i === questionIndex 
          ? { ...q, options: [...(q.options || []), ''] }
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

  const removeQuestion = (index) => {
    setQuiz(prev => ({
      ...prev,
      questions: prev.questions.filter((_, i) => i !== index)
    }));
  };

  const addNewQuestion = () => {
    const newQuestion = {
      question: '',
      question_type: 'multiple_choice',
      options: ['', '', '', ''],
      correct_answer: '',
      explanation: '',
      difficulty: 'medium'
    };

    setQuiz(prev => ({
      ...prev,
      questions: [...prev.questions, newQuestion]
    }));
  };

  const handleQuestionTypeChange = (index, newType) => {
    setQuiz(prev => ({
      ...prev,
      questions: prev.questions.map((q, i) => {
        if (i === index) {
          const updatedQuestion = { ...q, question_type: newType };

          // Reset options and correct answer based on question type
          if (newType === 'true_false') {
            updatedQuestion.options = ['True', 'False'];
            updatedQuestion.correct_answer = '';
          } else if (newType === 'multiple_choice') {
            updatedQuestion.options = q.options && q.options.length >= 2 ? q.options : ['', '', '', ''];
          } else if (newType === 'short_answer') {
            updatedQuestion.options = null;
          }

          return updatedQuestion;
        }
        return q;
      })
    }));
  };

  const handleSave = () => {
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
      if (!q.question.trim()) {
        toast.error(`Question ${i + 1} is empty`);
        return;
      }
      if (!q.correct_answer.trim()) {
        toast.error(`Question ${i + 1} needs a correct answer`);
        return;
      }
      if (q.question_type === 'multiple_choice' && (!q.options || q.options.length < 2)) {
        toast.error(`Question ${i + 1} needs at least 2 options`);
        return;
      }
    }

    const finalQuiz = {
      ...quiz,
      total_questions: quiz.questions.length
    };

    onSave(finalQuiz);
  };

  const renderQuestionEditor = (question, index) => {
    const isEditing = editingQuestion === index;

    return (
      <motion.div
        key={index}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white border border-gray-200 rounded-lg p-6 space-y-4"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="bg-blue-100 text-blue-600 text-sm font-medium px-3 py-1 rounded-full">
              Question {index + 1}
            </span>
            <select
              value={question.question_type}
              onChange={(e) => handleQuestionTypeChange(index, e.target.value)}
              className="text-sm border border-gray-300 rounded px-2 py-1"
            >
              <option value="multiple_choice">Multiple Choice</option>
              <option value="true_false">True/False</option>
              <option value="short_answer">Short Answer</option>
            </select>
            <select
              value={question.difficulty}
              onChange={(e) => handleQuestionChange(index, 'difficulty', e.target.value)}
              className="text-sm border border-gray-300 rounded px-2 py-1"
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setEditingQuestion(isEditing ? null : index)}
              className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded"
            >
              <Edit3 className="w-4 h-4" />
            </button>
            <button
              onClick={() => removeQuestion(index)}
              className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Question Text */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Question
          </label>
          <textarea
            value={question.question}
            onChange={(e) => handleQuestionChange(index, 'question', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows="3"
            placeholder="Enter your question here..."
          />
        </div>

        {/* Options for Multiple Choice and True/False */}
        {(question.question_type === 'multiple_choice' || question.question_type === 'true_false') && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Options
            </label>
            <div className="space-y-2">
              {(question.options || []).map((option, optionIndex) => (
                <div key={optionIndex} className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-gray-500 w-8">
                    {String.fromCharCode(65 + optionIndex)}.
                  </span>
                  <input
                    type="text"
                    value={option}
                    onChange={(e) => handleOptionChange(index, optionIndex, e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder={`Option ${String.fromCharCode(65 + optionIndex)}`}
                    disabled={question.question_type === 'true_false'}
                  />
                  {question.question_type === 'multiple_choice' && question.options.length > 2 && (
                    <button
                      onClick={() => removeOption(index, optionIndex)}
                      className="p-2 text-red-500 hover:bg-red-50 rounded"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
              {question.question_type === 'multiple_choice' && question.options.length < 6 && (
                <button
                  onClick={() => addOption(index)}
                  className="flex items-center space-x-1 text-blue-600 hover:text-blue-700 text-sm"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add Option</span>
                </button>
              )}
            </div>
          </div>
        )}

        {/* Correct Answer */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Correct Answer
          </label>
          {question.question_type === 'multiple_choice' ? (
            <select
              value={question.correct_answer}
              onChange={(e) => handleQuestionChange(index, 'correct_answer', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select correct answer</option>
              {(question.options || []).map((option, optionIndex) => (
                <option key={optionIndex} value={option}>
                  {String.fromCharCode(65 + optionIndex)}. {option}
                </option>
              ))}
            </select>
          ) : question.question_type === 'true_false' ? (
            <select
              value={question.correct_answer}
              onChange={(e) => handleQuestionChange(index, 'correct_answer', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select correct answer</option>
              <option value="True">True</option>
              <option value="False">False</option>
            </select>
          ) : (
            <input
              type="text"
              value={question.correct_answer}
              onChange={(e) => handleQuestionChange(index, 'correct_answer', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter the correct answer"
            />
          )}
        </div>

        {/* Explanation */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Explanation (Optional)
          </label>
          <textarea
            value={question.explanation || ''}
            onChange={(e) => handleQuestionChange(index, 'explanation', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows="2"
            placeholder="Explain why this is the correct answer..."
          />
        </div>
      </motion.div>
    );
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Edit Generated Quiz</h2>
          <p className="text-gray-600">Review and modify the AI-generated questions</p>
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <Hash className="w-4 h-4" />
          <span>{quiz.questions.length} questions</span>
        </div>
      </div>

      {/* Quiz Info */}
      <div className="bg-gray-50 rounded-lg p-4 mb-6 space-y-4">
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
            Description
          </label>
          <textarea
            value={quiz.description}
            onChange={(e) => handleQuizInfoChange('description', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows="2"
            placeholder="Enter quiz description"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Time Limit (minutes)
          </label>
          <input
            type="number"
            value={quiz.estimated_time}
            onChange={(e) => handleQuizInfoChange('estimated_time', parseInt(e.target.value) || 30)}
            className="w-32 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            min="1"
            max="180"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Instructions (optional)
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
      </div>

      {/* Questions */}
      <div className="space-y-6 mb-6">
        {quiz.questions.map((question, index) => renderQuestionEditor(question, index))}
      </div>

      {/* Add Question Button */}
      <div className="flex justify-center mb-6">
        <button
          onClick={addNewQuestion}
          className="flex items-center space-x-2 px-4 py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-blue-500 hover:text-blue-600 transition-colors"
        >
          <Plus className="w-5 h-5" />
          <span>Add New Question</span>
        </button>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-end space-x-4 pt-6 border-t">
        <button
          onClick={onCancel}
          className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
        >
          Cancel
        </button>
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-6 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg transition-colors flex items-center space-x-2"
        >
          {saving ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Saving...</span>
            </>
          ) : (
            <>
              <Save className="w-4 h-4" />
              <span>Save Quiz</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default QuizEditor;
