-- Sample Course Data for LearnSphere
-- Run this SQL in your Supabase SQL editor after creating courses table

-- First, add category column if it doesn't exist
ALTER TABLE courses ADD COLUMN IF NOT EXISTS category TEXT DEFAULT 'General';

-- Create index for category if it doesn't exist
CREATE INDEX IF NOT EXISTS idx_courses_category ON courses(category);

-- Insert sample courses with categories
-- Note: Replace the teacher_id with actual teacher IDs from your profiles table
-- You can find teacher IDs by running: SELECT id, full_name, role FROM profiles WHERE role = 'teacher';

INSERT INTO courses (teacher_id, title, description, category, status) VALUES 
-- Programming & Development
(
    (SELECT id FROM profiles WHERE role = 'teacher' LIMIT 1),
    'Complete Web Development Bootcamp',
    'Master HTML, CSS, JavaScript, React, Node.js, and MongoDB. Build real-world projects and deploy them. Perfect for beginners starting their coding journey.',
    'Programming & Development',
    'active'
),
(
    (SELECT id FROM profiles WHERE role = 'teacher' LIMIT 1),
    'Python for Data Science',
    'Learn Python programming fundamentals and apply them to data analysis, visualization, and machine learning. Includes hands-on projects with real datasets.',
    'Programming & Development',
    'active'
),
(
    (SELECT id FROM profiles WHERE role = 'teacher' LIMIT 1),
    'Advanced JavaScript Concepts',
    'Deep dive into advanced JavaScript topics including closures, prototypes, async/await, ES6+ features, and modern development patterns.',
    'Programming & Development',
    'active'
),
(
    (SELECT id FROM profiles WHERE role = 'teacher' LIMIT 1),
    'Mobile App Development with React Native',
    'Build cross-platform mobile applications using React Native. Learn navigation, state management, APIs, and app store deployment.',
    'Programming & Development',
    'active'
),

-- Data Science & Analytics
(
    (SELECT id FROM profiles WHERE role = 'teacher' LIMIT 1),
    'Machine Learning Fundamentals',
    'Introduction to machine learning algorithms, data preprocessing, model training, and evaluation. Hands-on projects with Python and scikit-learn.',
    'Data Science & Analytics',
    'active'
),
(
    (SELECT id FROM profiles WHERE role = 'teacher' LIMIT 1),
    'SQL for Data Analysis',
    'Master SQL for data analysis and business intelligence. Learn complex queries, joins, window functions, and database optimization techniques.',
    'Data Science & Analytics',
    'active'
),
(
    (SELECT id FROM profiles WHERE role = 'teacher' LIMIT 1),
    'Tableau Data Visualization',
    'Create stunning data visualizations and dashboards with Tableau. Learn to tell compelling stories with data and build interactive reports.',
    'Data Science & Analytics',
    'active'
),

-- Design & Creativity
(
    (SELECT id FROM profiles WHERE role = 'teacher' LIMIT 1),
    'UI/UX Design Masterclass',
    'Learn user interface and user experience design principles. Master design tools, user research, prototyping, and creating user-centered designs.',
    'Design & Creativity',
    'active'
),
(
    (SELECT id FROM profiles WHERE role = 'teacher' LIMIT 1),
    'Digital Marketing Strategy',
    'Comprehensive guide to digital marketing including SEO, social media marketing, content marketing, email campaigns, and analytics.',
    'Marketing & Business',
    'active'
),
(
    (SELECT id FROM profiles WHERE role = 'teacher' LIMIT 1),
    'Graphic Design with Adobe Creative Suite',
    'Master Adobe Photoshop, Illustrator, and InDesign. Learn professional design techniques, branding, and visual communication.',
    'Design & Creativity',
    'active'
),

-- Business & Finance
(
    (SELECT id FROM profiles WHERE role = 'teacher' LIMIT 1),
    'Financial Analysis & Modeling',
    'Learn financial analysis techniques, Excel modeling, valuation methods, and investment analysis for business decision making.',
    'Business & Finance',
    'active'
),
(
    (SELECT id FROM profiles WHERE role = 'teacher' LIMIT 1),
    'Project Management Certification Prep',
    'Prepare for PMP certification with comprehensive project management training. Learn methodologies, tools, and best practices.',
    'Business & Finance',
    'active'
),
(
    (SELECT id FROM profiles WHERE role = 'teacher' LIMIT 1),
    'Entrepreneurship & Startup Fundamentals',
    'Learn how to start and scale a business. Cover business planning, funding, marketing, operations, and growth strategies.',
    'Business & Finance',
    'active'
),

-- Language & Communication
(
    (SELECT id FROM profiles WHERE role = 'teacher' LIMIT 1),
    'Business English Communication',
    'Improve your professional English communication skills. Learn business writing, presentations, negotiations, and cross-cultural communication.',
    'Language & Communication',
    'active'
),
(
    (SELECT id FROM profiles WHERE role = 'teacher' LIMIT 1),
    'Public Speaking & Presentation Skills',
    'Overcome public speaking anxiety and deliver compelling presentations. Learn storytelling, body language, and audience engagement techniques.',
    'Language & Communication',
    'active'
),

-- Technology & IT
(
    (SELECT id FROM profiles WHERE role = 'teacher' LIMIT 1),
    'Cybersecurity Fundamentals',
    'Learn essential cybersecurity concepts, threat detection, network security, and best practices for protecting digital assets.',
    'Technology & IT',
    'active'
),
(
    (SELECT id FROM profiles WHERE role = 'teacher' LIMIT 1),
    'Cloud Computing with AWS',
    'Master Amazon Web Services (AWS). Learn cloud architecture, deployment, scaling, and cost optimization for modern applications.',
    'Technology & IT',
    'active'
),
(
    (SELECT id FROM profiles WHERE role = 'teacher' LIMIT 1),
    'DevOps & CI/CD Pipeline',
    'Learn DevOps practices, Docker, Kubernetes, CI/CD pipelines, and infrastructure as code for modern software development.',
    'Technology & IT',
    'active'
),

-- Arts & Humanities
(
    (SELECT id FROM profiles WHERE role = 'teacher' LIMIT 1),
    'Creative Writing Workshop',
    'Develop your creative writing skills through exercises, feedback, and peer review. Explore fiction, poetry, and creative non-fiction.',
    'Arts & Humanities',
    'active'
),
(
    (SELECT id FROM profiles WHERE role = 'teacher' LIMIT 1),
    'Photography & Visual Storytelling',
    'Learn photography techniques, composition, lighting, and post-processing. Create compelling visual stories and build your portfolio.',
    'Arts & Humanities',
    'active'
),

-- Health & Wellness
(
    (SELECT id FROM profiles WHERE role = 'teacher' LIMIT 1),
    'Nutrition & Healthy Living',
    'Understand nutrition science, meal planning, and lifestyle changes for optimal health. Evidence-based approach to wellness.',
    'Health & Wellness',
    'active'
),
(
    (SELECT id FROM profiles WHERE role = 'teacher' LIMIT 1),
    'Mindfulness & Stress Management',
    'Learn mindfulness techniques, meditation practices, and stress reduction strategies for better mental health and well-being.',
    'Health & Wellness',
    'active'
),

-- Science & Mathematics
(
    (SELECT id FROM profiles WHERE role = 'teacher' LIMIT 1),
    'Statistics & Probability',
    'Master statistical concepts, probability theory, hypothesis testing, and data interpretation for research and decision making.',
    'Science & Mathematics',
    'active'
),
(
    (SELECT id FROM profiles WHERE role = 'teacher' LIMIT 1),
    'Physics for Engineers',
    'Comprehensive physics course covering mechanics, thermodynamics, electricity, and magnetism with engineering applications.',
    'Science & Mathematics',
    'active'
);

-- Update existing courses to have categories if they don't have them
UPDATE courses SET category = 'General' WHERE category IS NULL;

COMMIT;
