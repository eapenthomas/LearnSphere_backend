import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext.jsx';
import { Toaster } from 'react-hot-toast';
import LandingPage from './pages/LandingPage.jsx';
import LoginPage from './pages/LoginPage.jsx';
import RegisterPage from './pages/RegisterPage.jsx';
import ForgotPasswordPage from './pages/ForgotPasswordPage.jsx';
import AuthCallback from './pages/AuthCallback.jsx';
import StudentDashboard from './pages/student/Dashboard.jsx';
import StudentAllCourses from './pages/student/AllCourses.jsx';
import StudentMyCourses from './pages/student/MyCourses.jsx';
import StudentAssignments from './pages/student/Assignments.jsx';
import StudentCalendar from './pages/student/Calendar.jsx';
import StudentQuizzes from './pages/student/Quizzes.jsx';
import StudentForum from './pages/student/Forum.jsx';
import NotesSummarizer from './pages/student/NotesSummarizer.jsx';
import AITutor from './pages/student/AITutor.jsx';

import TakeQuiz from './pages/student/TakeQuiz.jsx';
import QuizResult from './pages/student/QuizResult.jsx';
import TeacherDashboard from './pages/teacher/Dashboard.jsx';
import TeacherMyCourses from './pages/teacher/MyCourses.jsx';
import TeacherAssignments from './pages/teacher/Assignments.jsx';
import TeacherQuizzes from './pages/teacher/Quizzes.jsx';
import TeacherCalendar from './pages/teacher/Calendar.jsx';
import TeacherForum from './pages/teacher/Forum.jsx';
import TeacherProgress from './pages/teacher/Progress.jsx';
import TeacherReports from './pages/teacher/Reports.jsx';
import TeacherProfile from './pages/teacher/Profile.jsx';
import QuizEdit from './pages/teacher/QuizEdit.jsx';
import QuizSubmissions from './pages/teacher/QuizSubmissions.jsx';
import AdminDashboard from './pages/admin/Dashboard.jsx';
import TeacherApprovals from './pages/admin/TeacherApprovals.jsx';
import UserManagement from './pages/admin/UserManagement.jsx';
import ActivityLogs from './pages/admin/ActivityLogs.jsx';
import EmailNotifications from './pages/admin/EmailNotifications.jsx';
import QuizResults from './pages/admin/QuizResults.jsx';
import AIUsage from './pages/admin/AIUsage.jsx';
import SystemSettings from './pages/admin/SystemSettings.jsx';

import ProfilePage from './pages/ProfilePage.jsx';
import VoiceNavigationDemo from './pages/VoiceNavigationDemo.jsx';

// Component to redirect users to their appropriate dashboard
const RoleBasedRedirect = () => {
    const { user, loading } = useAuth();

    if (loading) {
        return <div>Loading...</div>;
    }

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    // Redirect based on user role
    if (user.role === 'admin') {
        return <Navigate to="/admin/dashboard" replace />;
    } else if (user.role === 'teacher') {
        return <Navigate to="/teacher/dashboard" replace />;
    } else {
        return <Navigate to="/dashboard" replace />;
    }
};

import ProtectedRoute from './components/ProtectedRoute.jsx';

// Component to handle root class changes based on route
const AppContent = () => {
    const location = useLocation();

    useEffect(() => {
        const root = document.getElementById('root');
        if (location.pathname === '/dashboard' || location.pathname === '/profile') {
            root.className = 'dashboard-root';
        } else {
            root.className = 'page-root';
        }
    }, [location.pathname]);

    return (
        <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/home" element={<RoleBasedRedirect />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/auth/callback" element={<AuthCallback />} />
            <Route
                path="/dashboard"
                element={
                    <ProtectedRoute>
                        <StudentDashboard />
                    </ProtectedRoute>}
            />
            <Route
                path="/allcourses"
                element={
                    <ProtectedRoute>
                        <StudentAllCourses />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/mycourses"
                element={
                    <ProtectedRoute>
                        <StudentMyCourses />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/assignments"
                element={
                    <ProtectedRoute>
                        <StudentAssignments />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/calendar"
                element={
                    <ProtectedRoute>
                        <StudentCalendar />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/student/quizzes"
                element={
                    <ProtectedRoute>
                        <StudentQuizzes />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/student/notes-summarizer"
                element={
                    <ProtectedRoute>
                        <NotesSummarizer />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/student/ai-tutor"
                element={
                    <ProtectedRoute>
                        <AITutor />
                    </ProtectedRoute>
                }
            />

            <Route
                path="/forum"
                element={
                    <ProtectedRoute>
                        <StudentForum />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/student/quiz/:quizId/take"
                element={
                    <ProtectedRoute>
                        <TakeQuiz />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/student/quiz/:quizId/result"
                element={
                    <ProtectedRoute>
                        <QuizResult />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/teacher/dashboard"
                element={
                    <ProtectedRoute>
                        <TeacherDashboard />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/teacher/courses"
                element={
                    <ProtectedRoute>
                        <TeacherMyCourses />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/teacher/assignments"
                element={
                    <ProtectedRoute>
                        <TeacherAssignments />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/teacher/quizzes"
                element={
                    <ProtectedRoute>
                        <TeacherQuizzes />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/teacher/calendar"
                element={
                    <ProtectedRoute>
                        <TeacherCalendar />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/teacher/forum"
                element={
                    <ProtectedRoute>
                        <TeacherForum />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/teacher/progress"
                element={
                    <ProtectedRoute>
                        <TeacherProgress />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/teacher/reports"
                element={
                    <ProtectedRoute>
                        <TeacherReports />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/teacher/profile"
                element={
                    <ProtectedRoute>
                        <TeacherProfile />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/teacher/quiz/:quizId/edit"
                element={
                    <ProtectedRoute>
                        <QuizEdit />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/teacher/quiz/:quizId/submissions"
                element={
                    <ProtectedRoute>
                        <QuizSubmissions />
                    </ProtectedRoute>
                }
            />

            <Route
                path="/admin/dashboard"
                element={
                    <ProtectedRoute>
                        <AdminDashboard />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/admin/approvals"
                element={
                    <ProtectedRoute>
                        <TeacherApprovals />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/admin/users"
                element={
                    <ProtectedRoute>
                        <UserManagement />
                    </ProtectedRoute>
                }
            />
            <Route path="/admin/activity" element={
                    <ProtectedRoute>
                        <ActivityLogs />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/admin/emails"
                element={
                    <ProtectedRoute>
                        <EmailNotifications />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/admin/quizzes"
                element={
                    <ProtectedRoute>
                        <QuizResults />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/admin/ai-usage"
                element={
                    <ProtectedRoute>
                        <AIUsage />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/admin/settings"
                element={
                    <ProtectedRoute>
                        <SystemSettings />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/admin/system"
                element={
                    <ProtectedRoute>
                        <SystemSettings />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/profile"
                element={
                    <ProtectedRoute>
                        <ProfilePage />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/voice-demo"
                element={
                    <ProtectedRoute>
                        <VoiceNavigationDemo />
                    </ProtectedRoute>
                }
            />
        </Routes>
    );
};

function App() {
    return (
        <AuthProvider>
            <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
                <AppContent />
                <Toaster
                    position="top-center"
                    toastOptions={{
                        duration: 4000,
                        style: {
                            background: '#1e2a38',
                            color: '#ffffff',
                            borderRadius: '8px',
                            border: '1px solid #d4af37',
                            fontFamily: 'Inter, sans-serif',
                            fontWeight: '500',
                        },
                        success: {
                            style: {
                                background: '#2e7d32',
                                color: '#ffffff',
                            },
                        },
                        error: {
                            style: {
                                background: '#c62828',
                                color: '#ffffff',
                            },
                        },
                    }}
                />
            </Router>
        </AuthProvider>
    );
}

export default App; 