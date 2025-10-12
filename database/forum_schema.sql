-- LearnSphere Forum System Schema
-- Run this SQL in your Supabase SQL editor

-- Create forum_questions table
CREATE TABLE IF NOT EXISTS forum_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    course_id UUID REFERENCES courses(id) ON DELETE SET NULL,
    student_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    tags TEXT[] DEFAULT '{}',
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create forum_answers table
CREATE TABLE IF NOT EXISTS forum_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID NOT NULL REFERENCES forum_questions(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    teacher_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    is_accepted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_forum_questions_student_id ON forum_questions(student_id);
CREATE INDEX IF NOT EXISTS idx_forum_questions_course_id ON forum_questions(course_id);
CREATE INDEX IF NOT EXISTS idx_forum_questions_created_at ON forum_questions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_forum_questions_is_resolved ON forum_questions(is_resolved);

CREATE INDEX IF NOT EXISTS idx_forum_answers_question_id ON forum_answers(question_id);
CREATE INDEX IF NOT EXISTS idx_forum_answers_teacher_id ON forum_answers(teacher_id);
CREATE INDEX IF NOT EXISTS idx_forum_answers_created_at ON forum_answers(created_at);
CREATE INDEX IF NOT EXISTS idx_forum_answers_is_accepted ON forum_answers(is_accepted);

-- Enable Row Level Security (RLS)
ALTER TABLE forum_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE forum_answers ENABLE ROW LEVEL SECURITY;

-- RLS Policies for forum_questions

-- Students can view all questions
CREATE POLICY "Students can view all forum questions" ON forum_questions
    FOR SELECT USING (true);

-- Students can insert their own questions
CREATE POLICY "Students can create forum questions" ON forum_questions
    FOR INSERT WITH CHECK (auth.uid() = student_id);

-- Students can update their own questions
CREATE POLICY "Students can update their own forum questions" ON forum_questions
    FOR UPDATE USING (auth.uid() = student_id);

-- Students can delete their own questions
CREATE POLICY "Students can delete their own forum questions" ON forum_questions
    FOR DELETE USING (auth.uid() = student_id);

-- Teachers can view all questions
CREATE POLICY "Teachers can view all forum questions" ON forum_questions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'teacher'
        )
    );

-- RLS Policies for forum_answers

-- Everyone can view all answers
CREATE POLICY "Everyone can view forum answers" ON forum_answers
    FOR SELECT USING (true);

-- Only teachers can insert answers
CREATE POLICY "Teachers can create forum answers" ON forum_answers
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE profiles.id = auth.uid() 
            AND profiles.role = 'teacher'
        )
        AND auth.uid() = teacher_id
    );

-- Teachers can update their own answers
CREATE POLICY "Teachers can update their own forum answers" ON forum_answers
    FOR UPDATE USING (auth.uid() = teacher_id);

-- Teachers can delete their own answers
CREATE POLICY "Teachers can delete their own forum answers" ON forum_answers
    FOR DELETE USING (auth.uid() = teacher_id);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_forum_questions_updated_at 
    BEFORE UPDATE ON forum_questions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_forum_answers_updated_at 
    BEFORE UPDATE ON forum_answers 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample data for testing (optional)
-- Uncomment the following lines if you want sample data

/*
-- Sample forum questions
INSERT INTO forum_questions (title, content, student_id, tags) VALUES
('How to implement recursion in JavaScript?', 'I am having trouble understanding how recursion works in JavaScript. Can someone explain with examples?', (SELECT id FROM profiles WHERE role = 'student' LIMIT 1), ARRAY['javascript', 'recursion', 'programming']),
('What is the difference between let and var?', 'I keep getting confused about when to use let vs var in JavaScript. What are the key differences?', (SELECT id FROM profiles WHERE role = 'student' LIMIT 1), ARRAY['javascript', 'variables', 'scope']);

-- Sample forum answers (you'll need to replace teacher_id with actual teacher UUID)
-- INSERT INTO forum_answers (question_id, content, teacher_id) VALUES
-- ((SELECT id FROM forum_questions WHERE title LIKE 'How to implement recursion%' LIMIT 1), 'Recursion is a programming technique where a function calls itself...', 'TEACHER_UUID_HERE');
*/

-- Grant necessary permissions
GRANT ALL ON forum_questions TO authenticated;
GRANT ALL ON forum_answers TO authenticated;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;
