import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import QuizEditor from './QuizEditor.jsx';
import {
  Upload,
  FileText,
  Settings,
  Zap,
  CheckCircle,
  AlertCircle,
  Download,
  Save,
  Eye,
  Clock,
  Hash,
  Brain
} from 'lucide-react';

const QuizGenerator = ({ courseId, teacherId, onQuizGenerated }) => {
  const [file, setFile] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [generatedQuiz, setGeneratedQuiz] = useState(null);
  const [saving, setSaving] = useState(false);
  const [showEditor, setShowEditor] = useState(false);
  const [settings, setSettings] = useState({
    numQuestions: 10,
    difficulty: 'medium',
    questionTypes: ['multiple_choice', 'true_false', 'short_answer']
  });

  const handleFileUpload = (event) => {
    const uploadedFile = event.target.files[0];
    if (uploadedFile) {
      const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (allowedTypes.includes(uploadedFile.type)) {
        setFile(uploadedFile);
        toast.success('File uploaded successfully!');
      } else {
        toast.error('Please upload a PDF or DOCX file');
      }
    }
  };

  const handleGenerateQuiz = async () => {
    if (!file) {
      toast.error('Please upload a file first');
      return;
    }

    setGenerating(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('num_questions', settings.numQuestions.toString());
      formData.append('difficulty', settings.difficulty);
      formData.append('question_types', settings.questionTypes.join(','));
      formData.append('course_id', courseId);
      formData.append('teacher_id', teacherId);

      const response = await fetch('http://localhost:8000/api/quiz-generator/generate', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const quiz = await response.json();
        setGeneratedQuiz(quiz);
        setShowEditor(true);
        toast.success(`Generated ${quiz.total_questions} questions successfully!`);
      } else {
        const error = await response.json();
        const errorMessage = typeof error.detail === 'string' ? error.detail : 'Failed to generate quiz';
        toast.error(errorMessage);
      }
    } catch (error) {
      console.error('Error generating quiz:', error);
      toast.error('Failed to generate quiz');
    } finally {
      setGenerating(false);
    }
  };

  const handleSaveQuiz = async (editedQuiz) => {
    setSaving(true);
    try {
      const response = await fetch('http://localhost:8000/api/quiz-generator/save-generated-quiz', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...editedQuiz,
          course_id: courseId,
          teacher_id: teacherId
        })
      });

      if (response.ok) {
        const result = await response.json();
        toast.success('Quiz saved successfully!');
        if (onQuizGenerated) {
          onQuizGenerated(result.quiz_id);
        }
        // Reset form
        setFile(null);
        setGeneratedQuiz(null);
        setShowEditor(false);
      } else {
        const error = await response.json();
        const errorMessage = typeof error.detail === 'string' ? error.detail : 'Failed to save quiz';
        toast.error(errorMessage);
      }
    } catch (error) {
      console.error('Error saving quiz:', error);
      toast.error('Failed to save quiz');
    } finally {
      setSaving(false);
    }
  };

  const handleCancelEdit = () => {
    setShowEditor(false);
    setGeneratedQuiz(null);
  };

  const handleQuestionTypeChange = (type) => {
    setSettings(prev => ({
      ...prev,
      questionTypes: prev.questionTypes.includes(type)
        ? prev.questionTypes.filter(t => t !== type)
        : [...prev.questionTypes, type]
    }));
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center space-x-3 mb-6">
        <div className="p-2 bg-purple-100 rounded-lg">
          <Brain className="w-6 h-6 text-purple-600" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900">AI Quiz Generator</h2>
          <p className="text-gray-600">Upload a document and generate quiz questions automatically</p>
        </div>
      </div>

      {/* File Upload */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Upload Document (PDF or DOCX)
        </label>
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-purple-400 transition-colors">
          <input
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileUpload}
            className="hidden"
            id="file-upload"
          />
          <label htmlFor="file-upload" className="cursor-pointer">
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">
              {file ? file.name : 'Click to upload or drag and drop'}
            </p>
            <p className="text-sm text-gray-500 mt-1">PDF or DOCX files only</p>
          </label>
        </div>
      </div>

      {/* Settings */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Number of Questions
          </label>
          <input
            type="number"
            min="1"
            max="50"
            value={settings.numQuestions}
            onChange={(e) => setSettings(prev => ({ ...prev, numQuestions: parseInt(e.target.value) }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Difficulty Level
          </label>
          <select
            value={settings.difficulty}
            onChange={(e) => setSettings(prev => ({ ...prev, difficulty: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
          </select>
        </div>
      </div>

      {/* Question Types */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Question Types
        </label>
        <div className="flex flex-wrap gap-3">
          {[
            { value: 'multiple_choice', label: 'Multiple Choice' },
            { value: 'true_false', label: 'True/False' },
            { value: 'short_answer', label: 'Short Answer' }
          ].map((type) => (
            <label key={type.value} className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.questionTypes.includes(type.value)}
                onChange={() => handleQuestionTypeChange(type.value)}
                className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
              />
              <span className="text-sm text-gray-700">{type.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Generate Button */}
      <button
        onClick={handleGenerateQuiz}
        disabled={!file || generating}
        className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white font-medium py-3 px-4 rounded-lg transition-colors flex items-center justify-center space-x-2"
      >
        {generating ? (
          <>
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            <span>Generating Quiz...</span>
          </>
        ) : (
          <>
            <Zap className="w-5 h-5" />
            <span>Generate Quiz</span>
          </>
        )}
      </button>

      {/* Quiz Editor */}
      {showEditor && generatedQuiz && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6"
        >
          <QuizEditor
            generatedQuiz={generatedQuiz}
            onSave={handleSaveQuiz}
            onCancel={handleCancelEdit}
            saving={saving}
          />
        </motion.div>
      )}
    </div>
  );
};

export default QuizGenerator;
