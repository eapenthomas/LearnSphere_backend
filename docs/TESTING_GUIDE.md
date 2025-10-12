# 🧪 LearnSphere Testing Guide

This guide provides comprehensive step-by-step instructions for testing LearnSphere features using Selenium automation and manual testing.

## 📋 Table of Contents

1. [Setup & Prerequisites](#setup--prerequisites)
2. [Automated Testing with Selenium](#automated-testing-with-selenium)
3. [Manual Testing Procedures](#manual-testing-procedures)
4. [Feature-Specific Test Cases](#feature-specific-test-cases)
5. [Performance Testing](#performance-testing)
6. [Security Testing](#security-testing)

## 🚀 Setup & Prerequisites

### Required Tools
- **Python 3.8+**
- **Selenium WebDriver**
- **Chrome/Firefox Browser**
- **Node.js 16+** (for frontend testing)
- **Postman/Insomnia** (for API testing)

### Installation
```bash
# Install Selenium
pip install selenium webdriver-manager

# Install additional testing tools
pip install requests pytest allure-pytest

# Install frontend dependencies
cd frontend
npm install
```

## 🤖 Automated Testing with Selenium

### Basic Selenium Setup

Create `test_setup.py`:
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

class LearnSphereTester:
    def __init__(self):
        self.driver = None
        self.base_url = "http://localhost:3000"
        self.backend_url = "http://localhost:8000"
        
    def setup_driver(self):
        """Initialize Chrome WebDriver"""
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.implicitly_wait(10)
        
    def teardown_driver(self):
        """Close WebDriver"""
        if self.driver:
            self.driver.quit()
```

## 📝 Feature-Specific Test Cases

### 1. 🔐 Authentication Testing

#### Test Case 1.1: User Registration
```python
def test_user_registration(self):
    """Test user registration process"""
    self.driver.get(f"{self.base_url}/register")
    
    # Fill registration form
    self.driver.find_element(By.NAME, "email").send_keys("test@example.com")
    self.driver.find_element(By.NAME, "fullName").send_keys("Test User")
    self.driver.find_element(By.NAME, "password").send_keys("TestPassword123")
    self.driver.find_element(By.NAME, "role").send_keys("student")
    
    # Submit form
    self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    
    # Verify success
    WebDriverWait(self.driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "toast-success"))
    )
    
    print("✅ User registration test passed")
```

#### Test Case 1.2: User Login
```python
def test_user_login(self):
    """Test user login process"""
    self.driver.get(f"{self.base_url}/login")
    
    # Fill login form
    self.driver.find_element(By.NAME, "email").send_keys("test@example.com")
    self.driver.find_element(By.NAME, "password").send_keys("TestPassword123")
    
    # Submit form
    self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    
    # Verify redirect to dashboard
    WebDriverWait(self.driver, 10).until(
        EC.url_contains("/dashboard")
    )
    
    print("✅ User login test passed")
```

### 2. 📚 Course Management Testing

#### Test Case 2.1: Course Creation (Teacher)
```python
def test_course_creation(self):
    """Test course creation by teacher"""
    # Login as teacher first
    self.test_teacher_login()
    
    # Navigate to My Courses
    self.driver.find_element(By.XPATH, "//a[contains(text(), 'My Courses')]").click()
    
    # Click Create Course button
    self.driver.find_element(By.XPATH, "//button[contains(text(), 'Create Course')]").click()
    
    # Fill course form
    course_title = f"Test Course {int(time.time())}"
    self.driver.find_element(By.NAME, "title").send_keys(course_title)
    self.driver.find_element(By.NAME, "description").send_keys("Test course description")
    self.driver.find_element(By.NAME, "category").send_keys("Development")
    self.driver.find_element(By.NAME, "difficulty").send_keys("Beginner")
    
    # Submit form
    self.driver.find_element(By.XPATH, "//button[contains(text(), 'Create Course')]").click()
    
    # Verify success
    WebDriverWait(self.driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "toast-success"))
    )
    
    print(f"✅ Course creation test passed: {course_title}")
```

#### Test Case 2.2: Course Enrollment (Student)
```python
def test_course_enrollment(self):
    """Test course enrollment by student"""
    # Login as student
    self.test_student_login()
    
    # Navigate to All Courses
    self.driver.find_element(By.XPATH, "//a[contains(text(), 'All Courses')]").click()
    
    # Find and click on first available course
    course_card = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".course-card"))
    )
    course_card.click()
    
    # Click Enroll button
    enroll_button = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Enroll')]"))
    )
    enroll_button.click()
    
    # Verify enrollment success
    WebDriverWait(self.driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "toast-success"))
    )
    
    print("✅ Course enrollment test passed")
```

### 3. 📝 Quiz System Testing

#### Test Case 3.1: Quiz Creation (Teacher)
```python
def test_quiz_creation(self):
    """Test quiz creation by teacher"""
    # Login as teacher
    self.test_teacher_login()
    
    # Navigate to Quizzes
    self.driver.find_element(By.XPATH, "//a[contains(text(), 'Quizzes')]").click()
    
    # Click Create Quiz button
    self.driver.find_element(By.XPATH, "//button[contains(text(), 'Create Quiz')]").click()
    
    # Fill quiz form
    quiz_title = f"Test Quiz {int(time.time())}"
    self.driver.find_element(By.NAME, "title").send_keys(quiz_title)
    self.driver.find_element(By.NAME, "description").send_keys("Test quiz description")
    self.driver.find_element(By.NAME, "duration_minutes").clear()
    self.driver.find_element(By.NAME, "duration_minutes").send_keys("30")
    
    # Add questions
    self.add_quiz_question("What is Python?", "Programming Language", ["Scripting Language", "Markup Language", "Database"])
    
    # Submit quiz
    self.driver.find_element(By.XPATH, "//button[contains(text(), 'Create Quiz')]").click()
    
    # Verify success
    WebDriverWait(self.driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "toast-success"))
    )
    
    print(f"✅ Quiz creation test passed: {quiz_title}")

def add_quiz_question(self, question_text, correct_answer, options):
    """Helper method to add quiz questions"""
    # Add question text
    self.driver.find_element(By.NAME, "question_text").send_keys(question_text)
    
    # Add options
    for i, option in enumerate(options):
        option_input = self.driver.find_element(By.NAME, f"options[{i}].text")
        option_input.send_keys(option)
        
        # Mark correct answer
        if option == correct_answer:
            self.driver.find_element(By.NAME, f"options[{i}].is_correct").click()
    
    # Add question
    self.driver.find_element(By.XPATH, "//button[contains(text(), 'Add Question')]").click()
```

#### Test Case 3.2: Quiz Taking (Student)
```python
def test_quiz_taking(self):
    """Test quiz taking by student"""
    # Login as student
    self.test_student_login()
    
    # Navigate to Quizzes
    self.driver.find_element(By.XPATH, "//a[contains(text(), 'Quizzes')]").click()
    
    # Find and click on available quiz
    quiz_card = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".quiz-card"))
    )
    quiz_card.click()
    
    # Start quiz
    start_button = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Start Quiz')]"))
    )
    start_button.click()
    
    # Answer questions
    self.answer_quiz_questions()
    
    # Submit quiz
    submit_button = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Submit Quiz')]"))
    )
    submit_button.click()
    
    # Verify submission
    WebDriverWait(self.driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "quiz-result"))
    )
    
    print("✅ Quiz taking test passed")

def answer_quiz_questions(self):
    """Helper method to answer quiz questions"""
    # Find all questions and answer them
    questions = self.driver.find_elements(By.CSS_SELECTOR, ".quiz-question")
    
    for question in questions:
        # Select first option for each question
        first_option = question.find_element(By.CSS_SELECTOR, "input[type='radio']")
        first_option.click()
        time.sleep(1)  # Brief pause between questions
```

### 4. 📄 Notes Summarizer Testing

#### Test Case 4.1: PDF Upload and Summarization
```python
def test_notes_summarizer(self):
    """Test PDF upload and summarization"""
    # Login as student
    self.test_student_login()
    
    # Navigate to Notes Summarizer
    self.driver.find_element(By.XPATH, "//a[contains(text(), 'Notes Summarizer')]").click()
    
    # Upload PDF file
    file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
    file_input.send_keys("/path/to/test/document.pdf")  # Replace with actual PDF path
    
    # Click Generate Summary
    self.driver.find_element(By.XPATH, "//button[contains(text(), 'Generate Summary')]").click()
    
    # Wait for processing
    WebDriverWait(self.driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "summary-result"))
    )
    
    # Verify summary is displayed
    summary_text = self.driver.find_element(By.CSS_SELECTOR, ".summary-result").text
    assert len(summary_text) > 100, "Summary should be substantial"
    
    print("✅ Notes summarizer test passed")
```

### 5. 🤖 Quiz Generator Testing

#### Test Case 5.1: AI-Powered Quiz Generation
```python
def test_quiz_generator(self):
    """Test AI-powered quiz generation from PDF"""
    # Login as teacher
    self.test_teacher_login()
    
    # Navigate to Quiz Generator
    self.driver.find_element(By.XPATH, "//a[contains(text(), 'Quiz Generator')]").click()
    
    # Upload PDF file
    file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
    file_input.send_keys("/path/to/test/document.pdf")  # Replace with actual PDF path
    
    # Set quiz parameters
    self.driver.find_element(By.NAME, "num_questions").clear()
    self.driver.find_element(By.NAME, "num_questions").send_keys("5")
    self.driver.find_element(By.NAME, "difficulty").send_keys("medium")
    
    # Generate quiz
    self.driver.find_element(By.XPATH, "//button[contains(text(), 'Generate Quiz')]").click()
    
    # Wait for AI processing
    WebDriverWait(self.driver, 60).until(
        EC.presence_of_element_located((By.CLASS_NAME, "generated-questions"))
    )
    
    # Verify questions are generated
    questions = self.driver.find_elements(By.CSS_SELECTOR, ".generated-question")
    assert len(questions) >= 3, "Should generate at least 3 questions"
    
    print("✅ Quiz generator test passed")
```

### 6. 💬 Forum Testing

#### Test Case 6.1: Forum Question Posting
```python
def test_forum_question_posting(self):
    """Test posting questions in forum"""
    # Login as student
    self.test_student_login()
    
    # Navigate to Forum
    self.driver.find_element(By.XPATH, "//a[contains(text(), 'Doubt Forum')]").click()
    
    # Click Ask Question button
    self.driver.find_element(By.XPATH, "//button[contains(text(), 'Ask Question')]").click()
    
    # Fill question form
    question_title = f"Test Question {int(time.time())}"
    self.driver.find_element(By.NAME, "title").send_keys(question_title)
    self.driver.find_element(By.NAME, "content").send_keys("This is a test question for the forum.")
    
    # Select course (if available)
    try:
        course_select = self.driver.find_element(By.NAME, "course_id")
        course_select.click()
        course_option = self.driver.find_element(By.CSS_SELECTOR, "option[value]:not([value=''])")
        course_option.click()
    except:
        pass  # No course selection available
    
    # Post question
    self.driver.find_element(By.XPATH, "//button[contains(text(), 'Post Question')]").click()
    
    # Verify success
    WebDriverWait(self.driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "toast-success"))
    )
    
    print(f"✅ Forum question posting test passed: {question_title}")
```

## 🔄 Running Complete Test Suite

### Test Runner Script

Create `run_tests.py`:
```python
#!/usr/bin/env python3
"""
LearnSphere Automated Test Runner
"""

from test_setup import LearnSphereTester
import sys
import traceback

def run_all_tests():
    """Run all test cases"""
    tester = LearnSphereTester()
    
    test_cases = [
        ("User Registration", tester.test_user_registration),
        ("User Login", tester.test_user_login),
        ("Course Creation", tester.test_course_creation),
        ("Course Enrollment", tester.test_course_enrollment),
        ("Quiz Creation", tester.test_quiz_creation),
        ("Quiz Taking", tester.test_quiz_taking),
        ("Notes Summarizer", tester.test_notes_summarizer),
        ("Quiz Generator", tester.test_quiz_generator),
        ("Forum Question Posting", tester.test_forum_question_posting),
    ]
    
    passed = 0
    failed = 0
    
    try:
        tester.setup_driver()
        
        for test_name, test_func in test_cases:
            try:
                print(f"\n🧪 Running: {test_name}")
                test_func()
                passed += 1
            except Exception as e:
                print(f"❌ Failed: {test_name}")
                print(f"   Error: {str(e)}")
                failed += 1
                
    except Exception as e:
        print(f"❌ Test setup failed: {str(e)}")
        traceback.print_exc()
        
    finally:
        tester.teardown_driver()
        
    print(f"\n📊 Test Results:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")

if __name__ == "__main__":
    run_all_tests()
```

### Running Tests
```bash
# Run all tests
python run_tests.py

# Run specific test
python -c "from test_setup import LearnSphereTester; t = LearnSphereTester(); t.setup_driver(); t.test_course_creation(); t.teardown_driver()"
```

## 📊 Performance Testing

### Load Testing with Selenium Grid
```python
def test_concurrent_users(self):
    """Test system with multiple concurrent users"""
    from concurrent.futures import ThreadPoolExecutor
    
    def simulate_user():
        driver = webdriver.Chrome()
        try:
            driver.get("http://localhost:3000/login")
            # Simulate user actions
            time.sleep(5)
        finally:
            driver.quit()
    
    # Simulate 10 concurrent users
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(simulate_user) for _ in range(10)]
        
        # Wait for all users to complete
        for future in futures:
            future.result()
    
    print("✅ Concurrent users test completed")
```

## 🔒 Security Testing

### Test Case: Authentication Bypass
```python
def test_authentication_bypass(self):
    """Test that protected routes require authentication"""
    # Try to access protected route without login
    self.driver.get(f"{self.base_url}/dashboard")
    
    # Should redirect to login
    WebDriverWait(self.driver, 10).until(
        EC.url_contains("/login")
    )
    
    print("✅ Authentication bypass test passed")
```

## 📝 Test Data Management

### Test Data Setup
```python
def setup_test_data(self):
    """Setup test data for testing"""
    test_users = [
        {"email": "student@test.com", "role": "student"},
        {"email": "teacher@test.com", "role": "teacher"},
        {"email": "admin@test.com", "role": "admin"}
    ]
    
    for user in test_users:
        # Create test user via API
        pass

def cleanup_test_data(self):
    """Clean up test data after testing"""
    # Remove test users, courses, etc.
    pass
```

## 🚀 Continuous Integration

### GitHub Actions Workflow
```yaml
name: LearnSphere Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install selenium webdriver-manager pytest
    - name: Start backend
      run: |
        cd backend
        python main.py &
        sleep 10
    - name: Start frontend
      run: |
        cd frontend
        npm install
        npm run dev &
        sleep 15
    - name: Run tests
      run: python run_tests.py
```

## 📋 Manual Testing Checklist

### Pre-Testing Setup
- [ ] Backend server running on port 8000
- [ ] Frontend server running on port 3000
- [ ] Database properly configured
- [ ] Environment variables set
- [ ] Test users created

### Authentication Features
- [ ] User registration works
- [ ] User login works
- [ ] Logout works
- [ ] Password reset works
- [ ] Session persistence works

### Course Management
- [ ] Teachers can create courses
- [ ] Students can view all courses
- [ ] Students can enroll in courses
- [ ] Course thumbnails display correctly
- [ ] Course filtering works

### Quiz System
- [ ] Teachers can create quizzes
- [ ] Students can take quizzes
- [ ] Quiz results are calculated correctly
- [ ] AI quiz generation works
- [ ] Quiz timer functions properly

### Forum System
- [ ] Students can post questions
- [ ] Teachers can answer questions
- [ ] Course-specific visibility works
- [ ] Question filtering works

### AI Features
- [ ] Notes summarizer processes PDFs
- [ ] Quiz generator creates questions
- [ ] AI responses are relevant

## 🐛 Troubleshooting

### Common Issues
1. **WebDriver not found**: Install ChromeDriver or use webdriver-manager
2. **Element not found**: Increase wait times or check element selectors
3. **Timeout errors**: Check if application is running properly
4. **Authentication failures**: Verify test user credentials

### Debug Mode
```python
def debug_mode(self):
    """Enable debug mode for detailed logging"""
    self.driver.set_window_size(1920, 1080)
    self.driver.maximize_window()
    
    # Enable console logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
```

This comprehensive testing guide ensures thorough validation of all LearnSphere features through both automated and manual testing approaches.
