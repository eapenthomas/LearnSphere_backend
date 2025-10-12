// API Configuration for LearnSphere Frontend
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Helper function to get full API endpoint URL
export const getApiUrl = (endpoint) => {
  // Remove leading slash if present to avoid double slashes
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
  return `${API_BASE_URL}/${cleanEndpoint}`;
};

// Common API endpoints
export const API_ENDPOINTS = {
  // Auth endpoints
  AUTH: {
    LOGIN: 'api/auth/login',
    REGISTER: 'api/auth/register',
    REFRESH: 'api/auth/refresh',
    LOGOUT: 'api/auth/logout',
    VERIFY_EMAIL: 'api/auth/verify-email',
    RESEND_VERIFICATION: 'api/auth/resend-verification',
    FORGOT_PASSWORD: 'api/auth/forgot-password',
    RESET_PASSWORD: 'api/auth/reset-password',
  },
  
  // Teacher verification
  TEACHER_VERIFICATION: {
    REGISTER: 'api/teacher-verification/register',
    REGISTER_MANUAL: 'api/teacher-verification/register-manual',
    PENDING_REQUESTS: 'api/teacher-verification/admin/pending-requests',
  },
  
  // Admin endpoints
  ADMIN: {
    APPROVE_TEACHER: 'api/admin/approve-teacher',
    REJECT_TEACHER: 'api/admin/reject-teacher',
    TOGGLE_USER_STATUS: 'api/admin/toggle-user-status',
    DASHBOARD_STATS: 'api/admin/dashboard/stats',
    USER_GROWTH: 'api/admin/dashboard/user-growth',
    ACTIVITY_LOGS: 'api/admin/dashboard/activity-logs',
  },
  
  // Course endpoints
  COURSES: {
    THUMBNAIL: (courseId) => `api/courses/${courseId}/thumbnail`,
  },
  
  // Notifications
  NOTIFICATIONS: {
    TEACHER_APPROVAL: 'api/notifications/teacher-approval',
    TEACHER_REJECTION: 'api/notifications/teacher-rejection',
    USER_STATUS_CHANGE: 'api/notifications/user-status-change',
  },
};

export default API_BASE_URL;
