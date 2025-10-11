-- Create teacher_ratings table for student ratings of teachers
CREATE TABLE IF NOT EXISTS teacher_ratings (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    teacher_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(teacher_id, student_id, course_id) -- One rating per student per teacher per course
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_teacher_ratings_teacher_id ON teacher_ratings(teacher_id);
CREATE INDEX IF NOT EXISTS idx_teacher_ratings_student_id ON teacher_ratings(student_id);
CREATE INDEX IF NOT EXISTS idx_teacher_ratings_course_id ON teacher_ratings(course_id);
CREATE INDEX IF NOT EXISTS idx_teacher_ratings_rating ON teacher_ratings(rating);

-- Enable Row Level Security
ALTER TABLE teacher_ratings ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Students can insert their own ratings" ON teacher_ratings
    FOR INSERT WITH CHECK (auth.uid() = student_id);

CREATE POLICY "Students can view all ratings" ON teacher_ratings
    FOR SELECT USING (true);

CREATE POLICY "Students can update their own ratings" ON teacher_ratings
    FOR UPDATE USING (auth.uid() = student_id);

CREATE POLICY "Teachers can view ratings for themselves" ON teacher_ratings
    FOR SELECT USING (auth.uid() = teacher_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_teacher_ratings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for updated_at
CREATE TRIGGER update_teacher_ratings_updated_at_trigger
    BEFORE UPDATE ON teacher_ratings
    FOR EACH ROW
    EXECUTE FUNCTION update_teacher_ratings_updated_at();

-- Add profile_picture column to profiles table if it doesn't exist
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS profile_picture TEXT;

-- Create index for profile_picture
CREATE INDEX IF NOT EXISTS idx_profiles_profile_picture ON profiles(profile_picture) WHERE profile_picture IS NOT NULL;
