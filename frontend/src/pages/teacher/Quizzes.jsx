import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext.jsx';
import TeacherDashboardLayout from '../../layouts/TeacherDashboardLayout.jsx';
import QuizGenerator from '../../components/QuizGenerator.jsx';
import CreateQuizModal from '../../components/CreateQuizModal.jsx';
import { toast } from 'react-hot-toast';
import {
  Plus,
  BookOpen,
  Clock,
  Users,
  Edit3,
  Trash2,
  Eye,
  Calendar,
  FileText,
  Award,
  Search,
  Filter,
  MoreVertical,
  Play,
  Pause,
  Archive
} from 'lucide-react';

const Quizzes = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedQuiz, setSelectedQuiz] = useState(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [activeTab, setActiveTab] = useState('manage'); // 'manage' or 'generate'
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState('');

  useEffect(() => {
    if (user?.id) {
      fetchQuizzes();
      fetchCourses();
    }
  }, [user]);

  const fetchQuizzes = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/quizzes/teacher/${user.id}`);
      const data = await response.json();

      if (data.success) {
        setQuizzes(data.data);
      } else {
        toast.error('Failed to load quizzes');
      }
    } catch (error) {
      console.error('Error fetching quizzes:', error);
      toast.error('Failed to load quizzes');
    } finally {
      setLoading(false);
    }
  };

  const fetchCourses = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/courses/teacher/${user.id}`);
      const result = await response.json();

      if (response.ok && result.success && Array.isArray(result.data)) {
        setCourses(result.data);
        if (result.data.length > 0) {
          setSelectedCourse(result.data[0].id);
        }
      } else {
        console.error('Failed to fetch courses:', result);
        setCourses([]);
      }
    } catch (error) {
      console.error('Error fetching courses:', error);
      setCourses([]);
    }
  };

  const handleDeleteQuiz = async (quizId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/quizzes/${quizId}`, {
        method: 'DELETE'
      });
      
      const data = await response.json();
      
      if (data.success) {
        setQuizzes(prev => prev.filter(quiz => quiz.id !== quizId));
        toast.success('Quiz deleted successfully');
        setShowDeleteModal(false);
        setSelectedQuiz(null);
      } else {
        toast.error('Failed to delete quiz');
      }
    } catch (error) {
      console.error('Error deleting quiz:', error);
      toast.error('Failed to delete quiz');
    }
  };

  const handleStatusChange = async (quizId, newStatus) => {
    try {
      const response = await fetch(`http://localhost:8000/api/quizzes/${quizId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setQuizzes(prev => prev.map(quiz => 
          quiz.id === quizId ? { ...quiz, status: newStatus } : quiz
        ));
        toast.success(`Quiz ${newStatus} successfully`);
      } else {
        toast.error('Failed to update quiz status');
      }
    } catch (error) {
      console.error('Error updating quiz status:', error);
      toast.error('Failed to update quiz status');
    }
  };

  const filteredQuizzes = quizzes.filter(quiz => {
    const matchesSearch = quiz.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         quiz.courses?.title.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || quiz.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'published': return 'bg-emerald-100 text-emerald-700 border-emerald-200';
      case 'draft': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'archived': return 'bg-gray-100 text-gray-700 border-gray-200';
      default: return 'bg-blue-100 text-blue-700 border-blue-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'published': return <Play className="w-3 h-3" />;
      case 'draft': return <Pause className="w-3 h-3" />;
      case 'archived': return <Archive className="w-3 h-3" />;
      default: return <FileText className="w-3 h-3" />;
    }
  };

  const QuizCard = ({ quiz }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 overflow-hidden"
    >
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="text-xl font-bold text-text-heading mb-2 line-clamp-2">
              {quiz.title}
            </h3>
            <div className="flex items-center space-x-4 text-sm text-text-primary mb-3">
              <div className="flex items-center space-x-1">
                <BookOpen className="w-4 h-4" />
                <span>{quiz.courses?.title || 'No Course'}</span>
              </div>
              <div className="flex items-center space-x-1">
                <FileText className="w-4 h-4" />
                <span>{quiz.question_count} Questions</span>
              </div>
              <div className="flex items-center space-x-1">
                <Award className="w-4 h-4" />
                <span>{quiz.total_marks} Marks</span>
              </div>
            </div>
            <div className="flex items-center space-x-4 text-sm text-text-secondary">
              <div className="flex items-center space-x-1">
                <Clock className="w-4 h-4" />
                <span>{quiz.duration_minutes} min</span>
              </div>
              <div className="flex items-center space-x-1">
                <Users className="w-4 h-4" />
                <span>{quiz.submission_count} submissions</span>
              </div>
              <div className="flex items-center space-x-1">
                <Calendar className="w-4 h-4" />
                <span>{new Date(quiz.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
          
          <div className="flex flex-col items-end space-y-2">
            <div className={`px-3 py-1 rounded-full text-xs font-medium border flex items-center space-x-1 ${getStatusColor(quiz.status)}`}>
              {getStatusIcon(quiz.status)}
              <span className="capitalize">{quiz.status}</span>
            </div>
            
            <div className="relative">
              <button className="p-2 hover:bg-background-tertiary rounded-lg transition-colors">
                <MoreVertical className="w-4 h-4 text-text-secondary" />
              </button>
            </div>
          </div>
        </div>

        {quiz.description && (
          <p className="text-text-primary text-sm mb-4 line-clamp-2">
            {quiz.description}
          </p>
        )}

        <div className="flex items-center justify-between pt-4 border-t border-border-primary">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => navigate(`/teacher/quiz/${quiz.id}/edit`)}
              className="btn-ghost-primary btn-sm"
            >
              <Edit3 className="w-4 h-4" />
              <span>Edit</span>
            </button>

            <button
              onClick={() => navigate(`/teacher/quiz/${quiz.id}/submissions`)}
              className="btn-outline-secondary btn-sm"
            >
              <Eye className="w-4 h-4" />
              <span>View Submissions</span>
            </button>
          </div>

          <div className="flex items-center space-x-2">
            {quiz.status === 'draft' && (
              <button
                onClick={() => handleStatusChange(quiz.id, 'published')}
                className="btn-success btn-sm"
              >
                Publish
              </button>
            )}
            
            {quiz.status === 'published' && (
              <button
                onClick={() => handleStatusChange(quiz.id, 'archived')}
                className="btn-warning btn-sm"
              >
                Archive
              </button>
            )}
            
            <button
              onClick={() => {
                setSelectedQuiz(quiz);
                setShowDeleteModal(true);
              }}
              className="btn-icon-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );

  return (
    <TeacherDashboardLayout>
      <div className="p-6 space-y-8 teacher-page-bg min-h-screen">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="teacher-course-card rounded-2xl shadow-lg p-8"
        >
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
            <div>
              <div className="flex items-center space-x-4 mb-4">
                <div className="p-3 bg-gradient-to-r from-purple-500 to-indigo-500 rounded-xl">
                  <FileText className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-extrabold" style={{ color: '#000000' }}>My Quizzes</h1>
                  <p className="text-lg" style={{ color: '#000000' }}>Create and manage your course quizzes</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-2 bg-purple-50 px-4 py-2 rounded-lg">
                  <FileText className="w-5 h-5 text-purple-600" />
                  <span className="font-semibold text-purple-700">
                    {quizzes.length} Total Quiz{quizzes.length !== 1 ? 'es' : ''}
                  </span>
                </div>
                <div className="flex items-center space-x-2 bg-emerald-50 px-4 py-2 rounded-lg">
                  <Play className="w-5 h-5 text-emerald-600" />
                  <span className="font-semibold text-emerald-700">
                    {quizzes.filter(q => q.status === 'published').length} Published
                  </span>
                </div>
                <div className="flex items-center space-x-2 bg-yellow-50 px-4 py-2 rounded-lg">
                  <Pause className="w-5 h-5 text-yellow-600" />
                  <span className="font-semibold text-yellow-700">
                    {quizzes.filter(q => q.status === 'draft').length} Draft{quizzes.filter(q => q.status === 'draft').length !== 1 ? 's' : ''}
                  </span>
                </div>
              </div>
            </div>

            <div className="mt-6 lg:mt-0">
              <button
                onClick={() => setShowCreateModal(true)}
                className="btn-primary btn-lg"
              >
                <Plus className="w-5 h-5" />
                <span>Create New Quiz</span>
              </button>
            </div>
          </div>
        </motion.div>

        {/* Tab Navigation */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="bg-white rounded-2xl shadow-lg p-6"
        >
          <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
            <button
              onClick={() => setActiveTab('manage')}
              className={`flex-1 py-3 px-6 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'manage'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              📝 Manage Quizzes
            </button>
            <button
              onClick={() => setActiveTab('generate')}
              className={`flex-1 py-3 px-6 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'generate'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              🤖 AI Quiz Generator
            </button>
          </div>
        </motion.div>

        {activeTab === 'manage' && (
          <>
            {/* Search and Filters */}
            <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-2xl shadow-lg p-6"
        >
          <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
            <div className="flex-1 max-w-md">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-text-tertiary w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search quizzes..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="form-input pl-10"
                />
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Filter className="w-5 h-5 text-text-secondary" />
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="form-input"
                >
                  <option value="all">All Status</option>
                  <option value="published">Published</option>
                  <option value="draft">Draft</option>
                  <option value="archived">Archived</option>
                </select>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Quiz Grid */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
          </div>
        ) : filteredQuizzes.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-12 bg-white rounded-2xl shadow-lg"
          >
            <FileText className="w-16 h-16 text-text-tertiary mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-text-heading mb-2">
              {searchTerm || statusFilter !== 'all' ? 'No quizzes found' : 'No quizzes yet'}
            </h3>
            <p className="text-text-secondary mb-6">
              {searchTerm || statusFilter !== 'all' 
                ? 'Try adjusting your search or filter criteria'
                : 'Create your first quiz to get started'
              }
            </p>
            {!searchTerm && statusFilter === 'all' && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="btn-primary btn-lg mx-auto"
              >
                <Plus className="w-5 h-5" />
                <span>Create Your First Quiz</span>
              </button>
            )}
          </motion.div>
        ) : (
          <div className="grid gap-6 grid-cols-1 lg:grid-cols-2 xl:grid-cols-3">
            {filteredQuizzes.map((quiz, index) => (
              <motion.div
                key={quiz.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 + index * 0.05 }}
              >
                <QuizCard quiz={quiz} />
              </motion.div>
            ))}
          </div>
        )}
          </>
        )}

        {activeTab === 'generate' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            {courses.length > 0 ? (
              <div className="space-y-6">
                <div className="bg-white rounded-2xl shadow-lg p-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Course
                  </label>
                  <select
                    value={selectedCourse}
                    onChange={(e) => setSelectedCourse(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    {courses.map((course) => (
                      <option key={course.id} value={course.id}>
                        {course.title}
                      </option>
                    ))}
                  </select>
                </div>

                {selectedCourse && (
                  <QuizGenerator
                    courseId={selectedCourse}
                    teacherId={user.id}
                    onQuizGenerated={(quizId) => {
                      toast.success('Quiz generated and saved successfully!');
                      setActiveTab('manage');
                      fetchQuizzes();
                    }}
                  />
                )}
              </div>
            ) : (
              <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
                <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Courses Found</h3>
                <p className="text-gray-600">You need to create a course first before generating quizzes.</p>
              </div>
            )}
          </motion.div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      <AnimatePresence>
        {showDeleteModal && selectedQuiz && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white rounded-2xl p-6 max-w-md w-full"
            >
              <div className="text-center">
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Trash2 className="w-8 h-8 text-red-600" />
                </div>
                <h3 className="text-xl font-bold text-text-heading mb-2">Delete Quiz</h3>
                <p className="text-text-primary mb-6">
                  Are you sure you want to delete "{selectedQuiz.title}"? This action cannot be undone.
                </p>
                <div className="flex items-center space-x-4">
                  <button
                    onClick={() => {
                      setShowDeleteModal(false);
                      setSelectedQuiz(null);
                    }}
                    className="btn-ghost flex-1"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => handleDeleteQuiz(selectedQuiz.id)}
                    className="btn-danger-solid flex-1"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Create Quiz Modal */}
      <CreateQuizModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onQuizCreated={fetchQuizzes}
      />
    </TeacherDashboardLayout>
  );
};

export default Quizzes;
