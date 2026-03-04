-- ============================================================================
-- STUDY BUDDY LMS FEATURES
-- ============================================================================

-- Buddy Requests Table
CREATE TABLE IF NOT EXISTS study_buddy_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id UUID NOT NULL,
    receiver_id UUID NOT NULL,
    course_id UUID NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(sender_id, receiver_id, course_id)
);

-- Buddy Messages Table
CREATE TABLE IF NOT EXISTS buddy_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sender_id UUID NOT NULL,
    receiver_id UUID NOT NULL,
    course_id UUID,
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Study Sessions Table
CREATE TABLE IF NOT EXISTS study_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID NOT NULL,
    host_id UUID NOT NULL,
    topic TEXT,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    meeting_link TEXT, -- Manual pasting (e.g. Google Meet, Zoom)
    status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'cancelled', 'completed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Study Session Participants Table
CREATE TABLE IF NOT EXISTS study_session_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    student_id UUID NOT NULL,
    status TEXT DEFAULT 'going' CHECK (status IN ('going', 'maybe', 'not_going')),
    joined_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(session_id, student_id)
);


-- INDEXES
CREATE INDEX IF NOT EXISTS idx_buddy_requests_sender ON study_buddy_requests(sender_id);
CREATE INDEX IF NOT EXISTS idx_buddy_requests_receiver ON study_buddy_requests(receiver_id);
CREATE INDEX IF NOT EXISTS idx_buddy_requests_course ON study_buddy_requests(course_id);

CREATE INDEX IF NOT EXISTS idx_buddy_messages_sender ON buddy_messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_buddy_messages_receiver ON buddy_messages(receiver_id);
CREATE INDEX IF NOT EXISTS idx_buddy_messages_course ON buddy_messages(course_id);
CREATE INDEX IF NOT EXISTS idx_buddy_messages_created_at ON buddy_messages(created_at);

CREATE INDEX IF NOT EXISTS idx_study_sessions_course ON study_sessions(course_id);
CREATE INDEX IF NOT EXISTS idx_study_sessions_host ON study_sessions(host_id);
CREATE INDEX IF NOT EXISTS idx_study_sessions_start_time ON study_sessions(start_time);

CREATE INDEX IF NOT EXISTS idx_study_session_participants_session ON study_session_participants(session_id);
CREATE INDEX IF NOT EXISTS idx_study_session_participants_student ON study_session_participants(student_id);

-- TRIGGERS
CREATE TRIGGER update_study_buddy_requests_updated_at 
    BEFORE UPDATE ON study_buddy_requests 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_study_sessions_updated_at 
    BEFORE UPDATE ON study_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- RLS (If enabled globally, minimal examples)
ALTER TABLE study_buddy_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE buddy_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE study_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE study_session_participants ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own buddy requests" ON study_buddy_requests
    FOR SELECT USING (auth.uid()::text = sender_id::text OR auth.uid()::text = receiver_id::text);
CREATE POLICY "Users can create buddy requests" ON study_buddy_requests
    FOR INSERT WITH CHECK (auth.uid()::text = sender_id::text);
CREATE POLICY "Users can update buddy requests they sent or received" ON study_buddy_requests
    FOR UPDATE USING (auth.uid()::text = sender_id::text OR auth.uid()::text = receiver_id::text);

CREATE POLICY "Users can view messages sent to or from them" ON buddy_messages
    FOR SELECT USING (auth.uid()::text = sender_id::text OR auth.uid()::text = receiver_id::text);
CREATE POLICY "Users can send messages" ON buddy_messages
    FOR INSERT WITH CHECK (auth.uid()::text = sender_id::text);
    
CREATE POLICY "Users can view study sessions" ON study_sessions
    FOR SELECT USING (true);
CREATE POLICY "Users can create study sessions" ON study_sessions
    FOR INSERT WITH CHECK (auth.uid()::text = host_id::text);
CREATE POLICY "Hosts can update their study sessions" ON study_sessions
    FOR UPDATE USING (auth.uid()::text = host_id::text);

CREATE POLICY "Users can view session participants" ON study_session_participants
    FOR SELECT USING (true);
CREATE POLICY "Users can manage their participant status" ON study_session_participants
    FOR ALL USING (auth.uid()::text = student_id::text);
