import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext.jsx';
import TeacherDashboardLayout from '../../layouts/TeacherDashboardLayout.jsx';
import { toast } from 'react-hot-toast';
import {
  Calendar as CalendarIcon,
  ChevronLeft,
  ChevronRight,
  Clock,
  FileText,
  Target,
  BookOpen,
  AlertTriangle,
  CheckCircle,
  Filter,
  RefreshCw,
  X,
  Download,
  Users,
  TrendingUp
} from 'lucide-react';

const TeacherCalendar = () => {
  const { user } = useAuth();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [events, setEvents] = useState([]);
  const [upcomingDeadlines, setUpcomingDeadlines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(null);
  const [showEventModal, setShowEventModal] = useState(false);
  const [selectedEvents, setSelectedEvents] = useState([]);
  const [categoryFilter, setCategoryFilter] = useState('all');

  // Category configurations
  const categoryConfig = {
    assignment: {
      color: '#3b82f6', // Blue
      icon: FileText,
      label: 'Assignments',
      emoji: '📄'
    },
    quiz: {
      color: '#ef4444', // Red
      icon: Target,
      label: 'Quizzes',
      emoji: '📝'
    },
    deadline: {
      color: '#f59e0b', // Amber
      icon: Clock,
      label: 'Deadlines',
      emoji: '⏰'
    }
  };

  useEffect(() => {
    if (user?.id) {
      fetchCalendarData();
    }
  }, [user, currentDate, categoryFilter]);

  const fetchCalendarData = async () => {
    try {
      setLoading(true);
      
      // Get teacher's courses first
      const coursesResponse = await fetch(`http://localhost:8000/api/courses/teacher/${user.id}`);
      if (!coursesResponse.ok) {
        throw new Error('Failed to fetch courses');
      }
      const courses = await coursesResponse.json();
      
      // Fetch assignments and quizzes for the current month
      const startOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
      const endOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
      
      const events = [];
      
      // Fetch assignments
      const assignmentsResponse = await fetch(`http://localhost:8000/api/assignments/teacher/${user.id}`);
      if (assignmentsResponse.ok) {
        const assignments = await assignmentsResponse.json();
        
        assignments.forEach(assignment => {
          const dueDate = new Date(assignment.due_date);
          if (dueDate >= startOfMonth && dueDate <= endOfMonth) {
            events.push({
              id: assignment.id,
              title: assignment.title,
              course_name: assignment.course_title,
              course_id: assignment.course_id,
              due_date: assignment.due_date,
              category: 'assignment',
              description: assignment.description,
              status: 'active'
            });
          }
        });
      }
      
      // Fetch quizzes
      const quizzesResponse = await fetch(`http://localhost:8000/api/quizzes/teacher/${user.id}`);
      if (quizzesResponse.ok) {
        const quizzesData = await quizzesResponse.json();
        if (quizzesData.success) {
          quizzesData.data.forEach(quiz => {
            const endDate = quiz.end_time ? new Date(quiz.end_time) : null;
            if (endDate && endDate >= startOfMonth && endDate <= endOfMonth) {
              events.push({
                id: quiz.id,
                title: quiz.title,
                course_name: quiz.courses?.title || 'Unknown Course',
                course_id: quiz.course_id,
                due_date: quiz.end_time,
                category: 'quiz',
                description: quiz.description,
                status: quiz.status
              });
            }
          });
        }
      }
      
      setEvents(events);
      
      // Fetch upcoming deadlines from analytics
      const analyticsResponse = await fetch(`http://localhost:8000/api/teacher/analytics/${user.id}`);
      if (analyticsResponse.ok) {
        const analyticsData = await analyticsResponse.json();
        setUpcomingDeadlines(analyticsData.upcomingDeadlines || []);
      }
      
    } catch (error) {
      console.error('Error fetching calendar data:', error);
      toast.error('Failed to load calendar data');
    } finally {
      setLoading(false);
    }
  };

  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();
    
    const days = [];
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }
    
    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day));
    }
    
    return days;
  };

  const getEventsForDate = (date) => {
    if (!date) return [];
    
    return events.filter(event => {
      const eventDate = new Date(event.due_date);
      return eventDate.toDateString() === date.toDateString();
    });
  };

  const handleDateClick = (date, dayEvents) => {
    if (dayEvents.length > 0) {
      setSelectedDate(date);
      setSelectedEvents(dayEvents);
      setShowEventModal(true);
    }
  };

  const navigateMonth = (direction) => {
    setCurrentDate(prev => {
      const newDate = new Date(prev);
      newDate.setMonth(prev.getMonth() + direction);
      return newDate;
    });
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getUrgencyClass = (event) => {
    const dueDate = new Date(event.due_date);
    const now = new Date();
    const daysUntil = Math.ceil((dueDate - now) / (1000 * 60 * 60 * 24));
    
    if (daysUntil <= 1) return 'bg-red-50 border-red-200';
    if (daysUntil <= 3) return 'bg-yellow-50 border-yellow-200';
    return 'bg-blue-50 border-blue-200';
  };

  const filteredEvents = categoryFilter === 'all' 
    ? events 
    : events.filter(event => event.category === categoryFilter);

  const days = getDaysInMonth(currentDate);
  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];
  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

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
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Teacher Calendar</h1>
            <p className="text-gray-600">Manage your assignments, quizzes, and deadlines</p>
          </div>
          
          <div className="flex items-center space-x-4">
            <button
              onClick={() => fetchCalendarData()}
              className="btn-ghost"
              disabled={loading}
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 xl:grid-cols-4 gap-8">
          {/* Calendar */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="xl:col-span-3 bg-white rounded-2xl shadow-lg p-6"
          >
            {/* Calendar Header */}
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">
                {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
              </h2>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => navigateMonth(-1)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <button
                  onClick={() => navigateMonth(1)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Category Filter */}
            <div className="flex items-center space-x-2 mb-6">
              <Filter className="w-4 h-4 text-gray-500" />
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="text-sm border border-gray-300 rounded-lg px-3 py-1 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="all">All Events</option>
                <option value="assignment">Assignments</option>
                <option value="quiz">Quizzes</option>
              </select>
            </div>

            {/* Calendar Grid */}
            <div className="grid grid-cols-7 gap-1">
              {/* Day headers */}
              {dayNames.map(day => (
                <div key={day} className="p-3 text-center text-sm font-medium text-gray-500">
                  {day}
                </div>
              ))}
              
              {/* Calendar days */}
              {days.map((date, index) => {
                const dayEvents = date ? getEventsForDate(date) : [];
                const isToday = date && date.toDateString() === new Date().toDateString();
                
                return (
                  <motion.div
                    key={index}
                    whileHover={dayEvents.length > 0 ? { scale: 1.02 } : {}}
                    className={`
                      min-h-[80px] p-2 border border-gray-100 cursor-pointer transition-all
                      ${date ? 'hover:bg-gray-50' : ''}
                      ${isToday ? 'bg-purple-50 border-purple-200' : ''}
                      ${dayEvents.length > 0 ? 'bg-blue-50' : ''}
                    `}
                    onClick={() => date && handleDateClick(date, dayEvents)}
                  >
                    {date && (
                      <>
                        <div className={`text-sm font-medium mb-1 ${isToday ? 'text-purple-600' : 'text-gray-900'}`}>
                          {date.getDate()}
                        </div>
                        <div className="space-y-1">
                          {dayEvents.slice(0, 2).map((event, eventIndex) => {
                            const config = categoryConfig[event.category];
                            return (
                              <div
                                key={eventIndex}
                                className="text-xs p-1 rounded truncate"
                                style={{ backgroundColor: config.color + '20', color: config.color }}
                              >
                                {event.title}
                              </div>
                            );
                          })}
                          {dayEvents.length > 2 && (
                            <div className="text-xs text-gray-500">
                              +{dayEvents.length - 2} more
                            </div>
                          )}
                        </div>
                      </>
                    )}
                  </motion.div>
                );
              })}
            </div>
          </motion.div>

          {/* Upcoming Deadlines Sidebar */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-6"
          >
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                <Clock className="w-5 h-5 mr-2 text-purple-600" />
                Upcoming Deadlines
              </h3>
              
              <div className="space-y-3">
                {upcomingDeadlines.length === 0 ? (
                  <p className="text-gray-500 text-sm">No upcoming deadlines</p>
                ) : (
                  upcomingDeadlines.map((deadline, index) => {
                    const config = categoryConfig[deadline.type] || categoryConfig.deadline;
                    const Icon = config.icon;
                    
                    return (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className={`p-3 rounded-lg border-l-4 ${
                          deadline.priority === 'high' ? 'bg-red-50 border-red-400' :
                          deadline.priority === 'medium' ? 'bg-yellow-50 border-yellow-400' :
                          'bg-blue-50 border-blue-400'
                        }`}
                      >
                        <div className="flex items-start space-x-3">
                          <Icon className="w-4 h-4 mt-1" style={{ color: config.color }} />
                          <div className="flex-1 min-w-0">
                            <h4 className="font-medium text-sm truncate text-gray-900">
                              {deadline.title}
                            </h4>
                            <p className="text-xs text-gray-600 truncate">
                              {deadline.course}
                            </p>
                            <div className="flex items-center justify-between mt-1">
                              <span className="text-xs text-gray-900">
                                {deadline.dueDate}
                              </span>
                              <div className="flex items-center space-x-1">
                                <Users className="w-3 h-3 text-gray-400" />
                                <span className="text-xs text-gray-600">
                                  {deadline.submissions}/{deadline.total}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    );
                  })
                )}
              </div>
            </div>
          </motion.div>
        </div>

        {/* Event Modal */}
        <AnimatePresence>
          {showEventModal && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
              onClick={() => setShowEventModal(false)}
            >
              <motion.div
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.95, opacity: 0 }}
                className="bg-white rounded-2xl shadow-xl max-w-md w-full p-6"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-bold text-gray-900">
                    Events for {selectedDate?.toLocaleDateString()}
                  </h3>
                  <button
                    onClick={() => setShowEventModal(false)}
                    className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
                
                <div className="space-y-3">
                  {selectedEvents.map((event, index) => {
                    const config = categoryConfig[event.category];
                    const Icon = config.icon;
                    
                    return (
                      <div key={index} className={`p-3 rounded-lg ${getUrgencyClass(event)}`}>
                        <div className="flex items-start space-x-3">
                          <Icon className="w-4 h-4 mt-1" style={{ color: config.color }} />
                          <div className="flex-1">
                            <h4 className="font-medium text-gray-900">{event.title}</h4>
                            <p className="text-sm text-gray-600">{event.course_name}</p>
                            <p className="text-xs text-gray-500 mt-1">
                              Due: {formatDate(event.due_date)}
                            </p>
                            {event.description && (
                              <p className="text-xs text-gray-600 mt-2">{event.description}</p>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </TeacherDashboardLayout>
  );
};

export default TeacherCalendar;
