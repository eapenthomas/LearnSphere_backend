# 🔔 Notification System - LearnSphere

A comprehensive notification system providing real-time in-app notifications and email alerts for all platform activities and important events.

## 🌟 Overview

The Notification System in LearnSphere keeps users informed about important activities, deadlines, and updates through multiple channels. It provides real-time in-app notifications, email alerts, and customizable notification preferences to ensure users never miss critical information.

## ✨ Features

### 📱 **In-App Notifications**
- **Real-time Updates** - Instant notifications for new activities
- **Notification Center** - Centralized notification management
- **Read/Unread Status** - Track notification status
- **Action Buttons** - Quick actions from notifications
- **Categorization** - Different types with distinct styling

### 📧 **Email Notifications**
- **Automated Emails** - System-generated email alerts
- **Template System** - Professional email templates
- **Batch Processing** - Efficient email delivery
- **Delivery Tracking** - Monitor email delivery status
- **Customizable Content** - Dynamic email content

### ⚙️ **Notification Preferences**
- **User Controls** - Customize notification settings
- **Channel Selection** - Choose email, in-app, or both
- **Frequency Settings** - Immediate, daily digest, or weekly
- **Category Filters** - Enable/disable specific notification types
- **Quiet Hours** - Set do-not-disturb periods

## 🏗️ Architecture

### Frontend Structure

#### **Notification Components**
```
frontend/src/components/
├── notifications/
│   ├── NotificationCenter.jsx    # Main notification panel
│   ├── NotificationItem.jsx      # Individual notification
│   ├── NotificationBell.jsx      # Notification icon with count
│   ├── NotificationSettings.jsx  # User preferences
│   └── ToastNotification.jsx     # Toast notifications
└── layout/
    └── Header.jsx                # Contains notification bell
```

#### **Notification Context**
```javascript
// frontend/src/context/NotificationContext.jsx
const NotificationContext = {
  notifications: [],           // All notifications
  unreadCount: 0,             // Unread notification count
  preferences: {},            // User notification preferences
  markAsRead: () => {},       // Mark notification as read
  markAllAsRead: () => {},    // Mark all as read
  deleteNotification: () => {},// Delete notification
  updatePreferences: () => {} // Update user preferences
}
```

### Backend Structure

#### **Notification API Module**
```
backend/
├── notification_api.py        # Notification endpoints
├── notification_service.py    # Notification business logic
├── email_service.py          # Email notification handling
└── notification_models.py     # Notification data models
```

## 🔧 Implementation Details

### Frontend Implementation

#### **Notification Bell Component**
```jsx
// frontend/src/components/notifications/NotificationBell.jsx
import React, { useState, useEffect } from 'react';
import { Bell } from 'lucide-react';
import { useNotifications } from '../../context/NotificationContext';

const NotificationBell = () => {
  const [showPanel, setShowPanel] = useState(false);
  const { notifications, unreadCount, markAllAsRead } = useNotifications();

  return (
    <div className="relative">
      <button
        onClick={() => setShowPanel(!showPanel)}
        className="relative p-2 text-gray-600 hover:text-gray-800 focus:outline-none"
      >
        <Bell size={24} />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {showPanel && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border z-50">
          <div className="p-4 border-b">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold">Notifications</h3>
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Mark all as read
                </button>
              )}
            </div>
          </div>

          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                No notifications
              </div>
            ) : (
              notifications.slice(0, 10).map(notification => (
                <NotificationItem
                  key={notification.id}
                  notification={notification}
                />
              ))
            )}
          </div>

          <div className="p-3 border-t">
            <button
              onClick={() => {
                setShowPanel(false);
                navigate('/notifications');
              }}
              className="w-full text-center text-blue-600 hover:text-blue-800 text-sm"
            >
              View all notifications
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
```

#### **Notification Item Component**
```jsx
// frontend/src/components/notifications/NotificationItem.jsx
const NotificationItem = ({ notification }) => {
  const { markAsRead } = useNotifications();

  const handleClick = () => {
    if (!notification.read) {
      markAsRead(notification.id);
    }
    
    // Navigate to relevant page if action URL exists
    if (notification.action_url) {
      navigate(notification.action_url);
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'assignment_created':
        return <FileText className="text-blue-500" size={20} />;
      case 'assignment_submitted':
        return <Upload className="text-green-500" size={20} />;
      case 'assignment_graded':
        return <CheckCircle className="text-purple-500" size={20} />;
      case 'quiz_available':
        return <Brain className="text-orange-500" size={20} />;
      case 'course_enrolled':
        return <BookOpen className="text-indigo-500" size={20} />;
      default:
        return <Bell className="text-gray-500" size={20} />;
    }
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInMinutes = Math.floor((now - time) / (1000 * 60));

    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return `${Math.floor(diffInMinutes / 1440)}d ago`;
  };

  return (
    <div
      onClick={handleClick}
      className={`p-4 border-b hover:bg-gray-50 cursor-pointer transition-colors ${
        !notification.read ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
      }`}
    >
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0 mt-1">
          {getNotificationIcon(notification.type)}
        </div>
        
        <div className="flex-1 min-w-0">
          <p className={`text-sm ${!notification.read ? 'font-semibold' : 'font-medium'}`}>
            {notification.title}
          </p>
          <p className="text-sm text-gray-600 mt-1">
            {notification.message}
          </p>
          <p className="text-xs text-gray-500 mt-2">
            {formatTimeAgo(notification.created_at)}
          </p>
        </div>

        {!notification.read && (
          <div className="flex-shrink-0">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
          </div>
        )}
      </div>
    </div>
  );
};
```

#### **Notification Settings Component**
```jsx
// frontend/src/components/notifications/NotificationSettings.jsx
const NotificationSettings = () => {
  const [preferences, setPreferences] = useState({
    email_notifications: true,
    in_app_notifications: true,
    assignment_notifications: true,
    quiz_notifications: true,
    course_notifications: true,
    grade_notifications: true,
    digest_frequency: 'immediate'
  });

  const handlePreferenceChange = async (key, value) => {
    const newPreferences = { ...preferences, [key]: value };
    setPreferences(newPreferences);

    try {
      await fetch('/api/notifications/preferences', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(newPreferences)
      });
      
      toast.success('Notification preferences updated');
    } catch (error) {
      toast.error('Failed to update preferences');
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Notification Settings</h1>

      <div className="space-y-6">
        {/* Delivery Methods */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">Delivery Methods</h2>
          
          <div className="space-y-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={preferences.email_notifications}
                onChange={(e) => handlePreferenceChange('email_notifications', e.target.checked)}
                className="mr-3"
              />
              <span>Email notifications</span>
            </label>
            
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={preferences.in_app_notifications}
                onChange={(e) => handlePreferenceChange('in_app_notifications', e.target.checked)}
                className="mr-3"
              />
              <span>In-app notifications</span>
            </label>
          </div>
        </div>

        {/* Notification Types */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">Notification Types</h2>
          
          <div className="space-y-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={preferences.assignment_notifications}
                onChange={(e) => handlePreferenceChange('assignment_notifications', e.target.checked)}
                className="mr-3"
              />
              <span>Assignment updates</span>
            </label>
            
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={preferences.quiz_notifications}
                onChange={(e) => handlePreferenceChange('quiz_notifications', e.target.checked)}
                className="mr-3"
              />
              <span>Quiz notifications</span>
            </label>
            
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={preferences.grade_notifications}
                onChange={(e) => handlePreferenceChange('grade_notifications', e.target.checked)}
                className="mr-3"
              />
              <span>Grade updates</span>
            </label>
          </div>
        </div>

        {/* Email Frequency */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">Email Frequency</h2>
          
          <select
            value={preferences.digest_frequency}
            onChange={(e) => handlePreferenceChange('digest_frequency', e.target.value)}
            className="w-full px-4 py-2 border rounded-lg"
          >
            <option value="immediate">Immediate</option>
            <option value="daily">Daily digest</option>
            <option value="weekly">Weekly digest</option>
            <option value="never">Never</option>
          </select>
        </div>
      </div>
    </div>
  );
};
```

### Backend Implementation

#### **Notification Service**
```python
# backend/notification_service.py
from typing import List, Dict, Any
import uuid
from datetime import datetime
from email_service import EmailService

class NotificationService:
    def __init__(self):
        self.email_service = EmailService()

    async def create_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str,
        action_url: str = None,
        send_email: bool = True
    ) -> dict:
        """Create a new notification"""
        
        notification_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": notification_type,
            "action_url": action_url,
            "read": False,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Save to database
        result = supabase.table("notifications").insert(notification_data).execute()
        
        # Send email if enabled
        if send_email:
            await self._send_email_notification(user_id, title, message, action_url)
        
        # Send real-time notification (WebSocket)
        await self._send_realtime_notification(user_id, notification_data)
        
        return result.data[0]

    async def notify_assignment_created(self, assignment_id: str, course_id: str):
        """Notify students about new assignment"""
        
        # Get assignment details
        assignment = supabase.table("assignments")\
            .select("*, courses(title)")\
            .eq("id", assignment_id)\
            .single()\
            .execute()
        
        if not assignment.data:
            return
        
        # Get enrolled students
        enrollments = supabase.table("enrollments")\
            .select("student_id")\
            .eq("course_id", course_id)\
            .eq("status", "active")\
            .execute()
        
        # Create notifications for each student
        for enrollment in enrollments.data:
            await self.create_notification(
                user_id=enrollment["student_id"],
                title="New Assignment Available",
                message=f"New assignment '{assignment.data['title']}' has been posted in {assignment.data['courses']['title']}",
                notification_type="assignment_created",
                action_url=f"/assignments/{assignment_id}"
            )

    async def notify_assignment_submitted(self, submission_id: str):
        """Notify teacher about assignment submission"""
        
        # Get submission details
        submission = supabase.table("assignment_submissions")\
            .select("*, assignments(title, teacher_id), profiles!student_id(full_name)")\
            .eq("id", submission_id)\
            .single()\
            .execute()
        
        if not submission.data:
            return
        
        await self.create_notification(
            user_id=submission.data["assignments"]["teacher_id"],
            title="Assignment Submitted",
            message=f"{submission.data['profiles']['full_name']} has submitted '{submission.data['assignments']['title']}'",
            notification_type="assignment_submitted",
            action_url=f"/teacher/assignments/{submission.data['assignment_id']}/submissions"
        )

    async def notify_assignment_graded(self, submission_id: str):
        """Notify student about graded assignment"""
        
        # Get submission details
        submission = supabase.table("assignment_submissions")\
            .select("*, assignments(title), profiles!student_id(full_name)")\
            .eq("id", submission_id)\
            .single()\
            .execute()
        
        if not submission.data:
            return
        
        await self.create_notification(
            user_id=submission.data["student_id"],
            title="Assignment Graded",
            message=f"Your assignment '{submission.data['assignments']['title']}' has been graded. Score: {submission.data['score']}/{submission.data['max_score']}",
            notification_type="assignment_graded",
            action_url=f"/assignments/{submission.data['assignment_id']}/submission"
        )

    async def notify_quiz_available(self, quiz_id: str, course_id: str):
        """Notify students about available quiz"""
        
        # Get quiz details
        quiz = supabase.table("quizzes")\
            .select("*, courses(title)")\
            .eq("id", quiz_id)\
            .single()\
            .execute()
        
        if not quiz.data:
            return
        
        # Get enrolled students
        enrollments = supabase.table("enrollments")\
            .select("student_id")\
            .eq("course_id", course_id)\
            .eq("status", "active")\
            .execute()
        
        # Create notifications for each student
        for enrollment in enrollments.data:
            await self.create_notification(
                user_id=enrollment["student_id"],
                title="Quiz Available",
                message=f"Quiz '{quiz.data['title']}' is now available in {quiz.data['courses']['title']}",
                notification_type="quiz_available",
                action_url=f"/quizzes/{quiz_id}"
            )

    async def _send_email_notification(self, user_id: str, title: str, message: str, action_url: str = None):
        """Send email notification"""
        
        # Get user email and preferences
        user = supabase.table("profiles")\
            .select("email, notification_preferences")\
            .eq("id", user_id)\
            .single()\
            .execute()
        
        if not user.data or not user.data.get("email"):
            return
        
        # Check if user wants email notifications
        preferences = user.data.get("notification_preferences", {})
        if not preferences.get("email_notifications", True):
            return
        
        # Send email
        await self.email_service.send_notification_email(
            to_email=user.data["email"],
            subject=title,
            message=message,
            action_url=action_url
        )

    async def _send_realtime_notification(self, user_id: str, notification_data: dict):
        """Send real-time notification via WebSocket"""
        # Implementation depends on WebSocket setup
        # This could use Supabase real-time or custom WebSocket server
        pass

# Singleton instance
notification_service = NotificationService()
```

#### **Notification API Endpoints**
```python
# backend/notification_api.py
@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    unread_only: bool = Query(False),
    current_user: dict = Depends(get_current_user)
):
    """Get user notifications"""
    
    query = supabase.table("notifications")\
        .select("*")\
        .eq("user_id", current_user["id"])\
        .order("created_at", desc=True)\
        .range(offset, offset + limit - 1)
    
    if unread_only:
        query = query.eq("read", False)
    
    result = query.execute()
    
    return [NotificationResponse(**notification) for notification in result.data]

@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark notification as read"""
    
    result = supabase.table("notifications")\
        .update({"read": True, "read_at": datetime.utcnow().isoformat()})\
        .eq("id", notification_id)\
        .eq("user_id", current_user["id"])\
        .execute()
    
    if not result.data:
        raise HTTPException(404, "Notification not found")
    
    return NotificationResponse(**result.data[0])

@router.put("/preferences", response_model=dict)
async def update_notification_preferences(
    preferences: NotificationPreferences,
    current_user: dict = Depends(get_current_user)
):
    """Update user notification preferences"""
    
    result = supabase.table("profiles")\
        .update({"notification_preferences": preferences.dict()})\
        .eq("id", current_user["id"])\
        .execute()
    
    return {"success": True, "preferences": preferences.dict()}
```

## 🔗 API Endpoints

### **Notification Management Endpoints**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/notifications` | Get user notifications | Yes |
| PUT | `/api/notifications/{id}/read` | Mark as read | Yes |
| PUT | `/api/notifications/mark-all-read` | Mark all as read | Yes |
| DELETE | `/api/notifications/{id}` | Delete notification | Yes |

### **Notification Preferences Endpoints**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/notifications/preferences` | Get user preferences | Yes |
| PUT | `/api/notifications/preferences` | Update preferences | Yes |

## 📊 Notification Types

### **Assignment Notifications**
- **assignment_created** - New assignment posted
- **assignment_submitted** - Student submitted assignment
- **assignment_graded** - Assignment has been graded
- **assignment_due_soon** - Assignment due in 24 hours

### **Quiz Notifications**
- **quiz_available** - New quiz is available
- **quiz_completed** - Quiz has been completed
- **quiz_graded** - Quiz results available
- **quiz_due_soon** - Quiz due in 24 hours

### **Course Notifications**
- **course_enrolled** - Successfully enrolled in course
- **course_updated** - Course information updated
- **new_material** - New course material uploaded

### **System Notifications**
- **account_approved** - Teacher account approved
- **password_changed** - Password successfully changed
- **login_alert** - New login detected

## 🎯 User Workflows

### **Student Notification Flow**
1. Receive real-time notification in app
2. See notification count in bell icon
3. Click to view notification details
4. Take action (view assignment, take quiz, etc.)
5. Notification marked as read automatically

### **Teacher Notification Flow**
1. Receive notification about student activity
2. Review notification in notification center
3. Navigate to relevant content for review
4. Take appropriate action (grade, provide feedback)

---

**🔔 Keeping everyone informed and engaged**
