import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext.jsx';
import DashboardLayout from '../../components/DashboardLayout.jsx';
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
  Download
} from 'lucide-react';

const StudentCalendar = () => {
  const { user } = useAuth();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [events, setEvents] = useState([]);
  const [upcomingDeadlines, setUpcomingDeadlines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(null);
  const [showEventModal, setShowEventModal] = useState(false);
  const [selectedEvents, setSelectedEvents] = useState([]);
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [showCompleted, setShowCompleted] = useState(true);

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
    exam: {
      color: '#dc2626', // Dark Red
      icon: Target,
      label: 'Exams',
      emoji: '📊'
    },
    project: {
      color: '#f59e0b', // Yellow
      icon: BookOpen,
      label: 'Projects',
      emoji: '🚀'
    },
    event: {
      color: '#8b5cf6', // Purple
      icon: CalendarIcon,
      label: 'Events',
      emoji: '📅'
    }
  };

  useEffect(() => {
    if (user?.id) {
      fetchCalendarData();
    }
  }, [user, currentDate, categoryFilter, showCompleted]);

  const fetchCalendarData = async () => {
    try {
      setLoading(true);
      
      // Calculate month range
      const startOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
      const endOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
      
      // Fetch events for the current month
      const params = new URLSearchParams({
        student_id: user.id,
        start_date: startOfMonth.toISOString().split('T')[0],
        end_date: endOfMonth.toISOString().split('T')[0],
        include_completed: showCompleted.toString()
      });
      
      if (categoryFilter !== 'all') {
        params.append('category', categoryFilter);
      }
      
      const eventsResponse = await fetch(`http://localhost:8000/api/student/deadlines?${params}`);
      
      if (eventsResponse.ok) {
        const eventsData = await eventsResponse.json();
        setEvents(eventsData.events);
      } else {
        throw new Error('Failed to fetch events');
      }
      
      // Fetch upcoming deadlines
      const upcomingResponse = await fetch(`http://localhost:8000/api/student/deadlines/upcoming?student_id=${user.id}&limit=7`);
      
      if (upcomingResponse.ok) {
        const upcomingData = await upcomingResponse.json();
        setUpcomingDeadlines(upcomingData);
      } else {
        throw new Error('Failed to fetch upcoming deadlines');
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
    
    // Add all days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day));
    }
    
    return days;
  };

  const getEventsForDate = (date) => {
    if (!date) return [];
    
    const dateStr = date.toISOString().split('T')[0];
    return events.filter(event => {
      const eventDate = new Date(event.due_date).toISOString().split('T')[0];
      return eventDate === dateStr;
    });
  };

  const handleDateClick = (date, dayEvents) => {
    if (!date || dayEvents.length === 0) return;
    
    setSelectedDate(date);
    setSelectedEvents(dayEvents);
    setShowEventModal(true);
  };

  const navigateMonth = (direction) => {
    setCurrentDate(prev => {
      const newDate = new Date(prev);
      newDate.setMonth(prev.getMonth() + direction);
      return newDate;
    });
  };

  const isToday = (date) => {
    if (!date) return false;
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  const getUrgencyClass = (event) => {
    const now = new Date();
    const dueDate = new Date(event.due_date);
    const hoursUntilDue = (dueDate - now) / (1000 * 60 * 60);
    
    if (hoursUntilDue < 0) return 'border-red-500 bg-red-50'; // Overdue
    if (hoursUntilDue <= 24) return 'border-red-400 bg-red-50 animate-pulse'; // Due within 24 hours
    if (hoursUntilDue <= 72) return 'border-orange-400 bg-orange-50'; // Due within 3 days
    return 'border-gray-200 bg-white';
  };

  const formatTime = (dateString) => {
    return new Date(dateString).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  return (
    <DashboardLayout>
      <div className="min-h-screen student-page-bg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-8">
            <div className="mb-4 lg:mb-0">
              <h1 className="text-heading-xl font-bold mb-2 font-serif" style={{color: '#000000'}}>
                Academic Calendar
              </h1>
              <p className="text-body-lg" style={{color: '#000000'}}>
                Track your assignments, quizzes, and important deadlines
              </p>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={fetchCalendarData}
                disabled={loading}
                className="btn-primary px-4 py-3 rounded-lg transition-all duration-300 flex items-center space-x-2 font-medium"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* Main Calendar */}
            <div className="lg:col-span-3">
              {/* Calendar Controls */}
              <div className="student-card-bg rounded-lg shadow-elegant p-6 mb-6">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
                  <div className="flex items-center space-x-4 mb-4 sm:mb-0">
                    <button
                      onClick={() => navigateMonth(-1)}
                      className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                      <ChevronLeft className="w-5 h-5" style={{color: '#000000'}} />
                    </button>
                    
                    <h2 className="text-xl font-semibold" style={{color: '#000000'}}>
                      {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
                    </h2>
                    
                    <button
                      onClick={() => navigateMonth(1)}
                      className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                      <ChevronRight className="w-5 h-5" style={{color: '#000000'}} />
                    </button>
                  </div>

                  {/* Filters */}
                  <div className="flex items-center space-x-4">
                    <select
                      value={categoryFilter}
                      onChange={(e) => setCategoryFilter(e.target.value)}
                      className="px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-400 focus:border-transparent text-sm"
                      style={{color: '#000000', backgroundColor: '#ffffff'}}
                    >
                      <option value="all">All Categories</option>
                      {Object.entries(categoryConfig).map(([key, config]) => (
                        <option key={key} value={key}>{config.label}</option>
                      ))}
                    </select>
                    
                    <label className="flex items-center space-x-2 text-sm">
                      <input
                        type="checkbox"
                        checked={showCompleted}
                        onChange={(e) => setShowCompleted(e.target.checked)}
                        className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      />
                      <span style={{color: '#000000'}}>Show Completed</span>
                    </label>
                  </div>
                </div>

                {/* Color Legend */}
                <div className="flex flex-wrap items-center gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium" style={{color: '#000000'}}>Legend:</span>
                  {Object.entries(categoryConfig).map(([key, config]) => (
                    <div key={key} className="flex items-center space-x-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: config.color }}
                      ></div>
                      <span className="text-sm" style={{color: '#000000'}}>
                        {config.emoji} {config.label}
                      </span>
                    </div>
                  ))}
                </div>

                {/* Calendar Grid */}
                <div className="grid grid-cols-7 gap-1">
                  {/* Day headers */}
                  {dayNames.map(day => (
                    <div key={day} className="p-3 text-center font-medium text-sm" style={{color: '#000000'}}>
                      {day}
                    </div>
                  ))}
                  
                  {/* Calendar days */}
                  {getDaysInMonth(currentDate).map((date, index) => {
                    const dayEvents = getEventsForDate(date);
                    const hasEvents = dayEvents.length > 0;
                    
                    return (
                      <div
                        key={index}
                        className={`
                          min-h-[80px] p-2 border border-gray-100 cursor-pointer transition-all duration-200
                          ${date ? 'hover:bg-blue-50' : ''}
                          ${isToday(date) ? 'bg-blue-100 border-blue-300 font-bold' : 'bg-white'}
                          ${hasEvents ? 'hover:shadow-md' : ''}
                        `}
                        onClick={() => handleDateClick(date, dayEvents)}
                      >
                        {date && (
                          <>
                            <div className={`text-sm ${isToday(date) ? 'font-bold' : ''}`} style={{color: '#000000'}}>
                              {date.getDate()}
                            </div>
                            
                            {/* Event dots */}
                            {hasEvents && (
                              <div className="flex flex-wrap gap-1 mt-1">
                                {dayEvents.slice(0, 3).map((event, eventIndex) => (
                                  <div
                                    key={eventIndex}
                                    className="w-2 h-2 rounded-full"
                                    style={{ backgroundColor: categoryConfig[event.category]?.color || '#6b7280' }}
                                    title={`${event.title} - ${event.course_name}`}
                                  ></div>
                                ))}
                                {dayEvents.length > 3 && (
                                  <div className="text-xs" style={{color: '#000000'}}>
                                    +{dayEvents.length - 3}
                                  </div>
                                )}
                              </div>
                            )}
                          </>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Upcoming Deadlines Sidebar */}
            <div className="lg:col-span-1">
              <div className="student-card-bg rounded-lg shadow-elegant p-6">
                <div className="flex items-center space-x-2 mb-6">
                  <Clock className="w-5 h-5 text-orange-500" />
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                    Upcoming Deadlines
                  </h3>
                </div>

                {loading ? (
                  <div className="text-center py-8">
                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-600" />
                    <p className="text-sm text-gray-700 dark:text-gray-300 font-medium">Loading...</p>
                  </div>
                ) : upcomingDeadlines.length === 0 ? (
                  <div className="text-center py-8">
                    <CheckCircle className="w-12 h-12 mx-auto mb-4 text-green-500" />
                    <p className="text-gray-700 dark:text-gray-300 font-medium">No upcoming deadlines!</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {upcomingDeadlines.map((deadline, index) => {
                      const config = categoryConfig[deadline.category] || categoryConfig.event;
                      const Icon = config.icon;
                      
                      return (
                        <motion.div
                          key={deadline.id}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.1 }}
                          className={`p-4 bg-white dark:bg-gray-800 rounded-lg border-l-4 shadow-lg hover:shadow-xl transition-all duration-300 ${getUrgencyClass(deadline)}`}
                          style={{ borderLeftColor: config.color }}
                        >
                          <div className="flex items-start space-x-3">
                            <Icon className="w-4 h-4 mt-1" style={{ color: config.color }} />
                            <div className="flex-1 min-w-0">
                              <h4 className="font-bold text-base truncate text-gray-900 dark:text-white">
                                {deadline.title}
                              </h4>
                              <p className="text-sm text-gray-800 dark:text-gray-200 truncate font-bold">
                                {deadline.course_name}
                              </p>
                              <div className="flex items-center justify-between mt-1">
                                <span className="text-sm text-gray-700 dark:text-gray-300 font-bold">
                                  {formatDate(deadline.due_date)}
                                </span>
                                <span className="text-sm font-bold text-gray-900 dark:text-white">
                                  {formatTime(deadline.due_date)}
                                </span>
                              </div>
                            </div>
                          </div>
                        </motion.div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Event Details Modal */}
      <AnimatePresence>
        {showEventModal && selectedDate && (
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
              className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-semibold" style={{color: '#000000'}}>
                    Events for {selectedDate.toLocaleDateString('en-US', {
                      weekday: 'long',
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </h3>
                  <button
                    onClick={() => setShowEventModal(false)}
                    className="text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>

                <div className="space-y-4">
                  {selectedEvents.map((event, index) => {
                    const config = categoryConfig[event.category] || categoryConfig.event;
                    const Icon = config.icon;

                    return (
                      <motion.div
                        key={event.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className={`p-4 rounded-lg border-l-4 ${getUrgencyClass(event)}`}
                        style={{ borderLeftColor: config.color }}
                      >
                        <div className="flex items-start space-x-4">
                          <div
                            className="p-2 rounded-lg"
                            style={{ backgroundColor: `${config.color}20`, color: config.color }}
                          >
                            <Icon className="w-5 h-5" />
                          </div>

                          <div className="flex-1">
                            <div className="flex items-start justify-between">
                              <div>
                                <h4 className="font-semibold text-lg" style={{color: '#000000'}}>
                                  {event.title}
                                </h4>
                                <p className="text-sm" style={{color: '#000000'}}>
                                  {event.course_name}
                                </p>
                                {event.teacher_name && (
                                  <p className="text-sm text-gray-600">
                                    Instructor: {event.teacher_name}
                                  </p>
                                )}
                              </div>

                              <div className="text-right">
                                <div
                                  className="px-3 py-1 rounded-full text-xs font-medium"
                                  style={{
                                    backgroundColor: `${config.color}20`,
                                    color: config.color
                                  }}
                                >
                                  {config.emoji} {config.label}
                                </div>
                                {event.submission_status && (
                                  <div className={`mt-2 px-2 py-1 rounded text-xs font-medium ${
                                    event.submission_status === 'reviewed'
                                      ? 'bg-green-100 text-green-700'
                                      : event.submission_status === 'submitted'
                                      ? 'bg-blue-100 text-blue-700'
                                      : 'bg-gray-100 text-gray-700'
                                  }`}>
                                    {event.submission_status.replace('_', ' ').toUpperCase()}
                                  </div>
                                )}
                              </div>
                            </div>

                            {event.description && (
                              <p className="mt-3 text-sm" style={{color: '#000000'}}>
                                {event.description}
                              </p>
                            )}

                            <div className="mt-4 flex items-center justify-between">
                              <div className="flex items-center space-x-4 text-sm">
                                <div className="flex items-center space-x-1">
                                  <Clock className="w-4 h-4" style={{color: '#000000'}} />
                                  <span style={{color: '#000000'}}>
                                    Due: {formatTime(event.due_date)}
                                  </span>
                                </div>

                                {event.score !== null && (
                                  <div className="flex items-center space-x-1">
                                    <CheckCircle className="w-4 h-4 text-green-500" />
                                    <span style={{color: '#000000'}}>
                                      Score: {event.score}/100
                                    </span>
                                  </div>
                                )}
                              </div>

                              <div className="flex items-center space-x-2">
                                {event.category === 'assignment' && (
                                  <button
                                    onClick={() => window.location.href = '/assignments'}
                                    className="btn-primary px-3 py-1 text-sm rounded-lg"
                                  >
                                    View Assignment
                                  </button>
                                )}
                                {event.category === 'quiz' && (
                                  <button
                                    onClick={() => window.location.href = '/student/quizzes'}
                                    className="btn-primary px-3 py-1 text-sm rounded-lg"
                                  >
                                    View Quiz
                                  </button>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </DashboardLayout>
  );
};

export default StudentCalendar;
