-- ============================================
-- ALIGNCV COMPLETE SCHEMA SETUP
-- Run this FIRST if starting from scratch
-- ============================================

-- 1. Create users table (base table, no dependencies)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users') THEN
        CREATE TABLE public.users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email TEXT UNIQUE NOT NULL,
            full_name TEXT,
            hashed_password TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            is_verified BOOLEAN DEFAULT FALSE,
            google_id TEXT UNIQUE,
            profile_picture_url TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );

        CREATE INDEX idx_users_email ON public.users(email);
        CREATE INDEX idx_users_google_id ON public.users(google_id);

        ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "Users can view their own data"
            ON public.users FOR SELECT
            USING (auth.uid() = id);

        CREATE POLICY "Users can update their own data"
            ON public.users FOR UPDATE
            USING (auth.uid() = id);

        RAISE NOTICE 'Created users table';
    ELSE
        RAISE NOTICE 'Users table already exists, skipping';
    END IF;
END $$;

-- 2. Create documents table (depends on users)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents') THEN
        CREATE TABLE public.documents (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size INTEGER,
            mime_type TEXT,
            storage_path TEXT,
            parsed_content JSONB,
            embedding_vector FLOAT[],
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );

        CREATE INDEX idx_documents_user_id ON public.documents(user_id);
        CREATE INDEX idx_documents_created_at ON public.documents(created_at DESC);

        ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "Users can view their own documents"
            ON public.documents FOR SELECT
            USING (auth.uid() = user_id);

        CREATE POLICY "Users can insert their own documents"
            ON public.documents FOR INSERT
            WITH CHECK (auth.uid() = user_id);

        CREATE POLICY "Users can update their own documents"
            ON public.documents FOR UPDATE
            USING (auth.uid() = user_id);

        CREATE POLICY "Users can delete their own documents"
            ON public.documents FOR DELETE
            USING (auth.uid() = user_id);

        RAISE NOTICE 'Created documents table';
    ELSE
        RAISE NOTICE 'Documents table already exists, skipping';
    END IF;
END $$;

-- 3. Create jobs table (no dependencies on users)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'jobs') THEN
        CREATE TABLE public.jobs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            job_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            description TEXT,
            location TEXT,
            url TEXT,
            source TEXT,
            tags TEXT[],
            salary_min FLOAT,
            salary_max FLOAT,
            employment_type TEXT,
            experience_level TEXT,
            vector_id TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );

        CREATE INDEX idx_jobs_job_id ON public.jobs(job_id);
        CREATE INDEX idx_jobs_company ON public.jobs(company);
        CREATE INDEX idx_jobs_source ON public.jobs(source);
        CREATE INDEX idx_jobs_created_at ON public.jobs(created_at DESC);

        ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "Jobs are publicly readable"
            ON public.jobs FOR SELECT
            USING (true);

        RAISE NOTICE 'Created jobs table';
    ELSE
        RAISE NOTICE 'Jobs table already exists, skipping';
    END IF;
END $$;

-- 4. Create bookmarks table (depends on users)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'bookmarks') THEN
        CREATE TABLE public.bookmarks (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
            job_id TEXT NOT NULL,
            title TEXT,
            company TEXT,
            location TEXT,
            description TEXT,
            posted_date DATE,
            source_url TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );

        CREATE INDEX idx_bookmarks_user_id ON public.bookmarks(user_id);
        CREATE INDEX idx_bookmarks_job_id ON public.bookmarks(job_id);

        ALTER TABLE public.bookmarks ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "Users can view their own bookmarks"
            ON public.bookmarks FOR SELECT
            USING (auth.uid() = user_id);

        CREATE POLICY "Users can insert their own bookmarks"
            ON public.bookmarks FOR INSERT
            WITH CHECK (auth.uid() = user_id);

        CREATE POLICY "Users can delete their own bookmarks"
            ON public.bookmarks FOR DELETE
            USING (auth.uid() = user_id);

        RAISE NOTICE 'Created bookmarks table';
    ELSE
        RAISE NOTICE 'Bookmarks table already exists, skipping';
    END IF;
END $$;

-- 5. Create applications table (depends on users)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'applications') THEN
        CREATE TABLE public.applications (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
            job_id TEXT NOT NULL,
            title TEXT,
            company TEXT,
            location TEXT,
            description TEXT,
            applied_at TIMESTAMPTZ DEFAULT NOW(),
            status TEXT DEFAULT 'applied',
            notes TEXT,
            source_url TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );

        CREATE INDEX idx_applications_user_id ON public.applications(user_id);
        CREATE INDEX idx_applications_job_id ON public.applications(job_id);
        CREATE INDEX idx_applications_status ON public.applications(status);

        ALTER TABLE public.applications ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "Users can view their own applications"
            ON public.applications FOR SELECT
            USING (auth.uid() = user_id);

        CREATE POLICY "Users can insert their own applications"
            ON public.applications FOR INSERT
            WITH CHECK (auth.uid() = user_id);

        CREATE POLICY "Users can update their own applications"
            ON public.applications FOR UPDATE
            USING (auth.uid() = user_id);

        CREATE POLICY "Users can delete their own applications"
            ON public.applications FOR DELETE
            USING (auth.uid() = user_id);

        RAISE NOTICE 'Created applications table';
    ELSE
        RAISE NOTICE 'Applications table already exists, skipping';
    END IF;
END $$;

-- 6. Create notifications table (depends on users)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'notifications') THEN
        CREATE TABLE public.notifications (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            job_id TEXT,
            match_score FLOAT,
            email_sent BOOLEAN DEFAULT FALSE,
            is_read BOOLEAN DEFAULT FALSE,
            read_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );

        CREATE INDEX idx_notifications_user_id ON public.notifications(user_id);
        CREATE INDEX idx_notifications_is_read ON public.notifications(is_read);
        CREATE INDEX idx_notifications_created_at ON public.notifications(created_at DESC);

        ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "Users can view their own notifications"
            ON public.notifications FOR SELECT
            USING (auth.uid() = user_id);

        CREATE POLICY "Users can update their own notifications"
            ON public.notifications FOR UPDATE
            USING (auth.uid() = user_id);

        CREATE POLICY "Users can delete their own notifications"
            ON public.notifications FOR DELETE
            USING (auth.uid() = user_id);

        RAISE NOTICE 'Created notifications table';
    ELSE
        RAISE NOTICE 'Notifications table already exists, skipping';
    END IF;
END $$;

-- 7. Create notification_settings table (depends on users)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'notification_settings') THEN
        CREATE TABLE public.notification_settings (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL UNIQUE REFERENCES public.users(id) ON DELETE CASCADE,
            email_enabled BOOLEAN DEFAULT TRUE,
            digest_frequency TEXT DEFAULT 'daily' CHECK (digest_frequency IN ('daily', 'weekly', 'disabled')),
            notify_new_matches BOOLEAN DEFAULT TRUE,
            notify_application_updates BOOLEAN DEFAULT TRUE,
            min_match_score FLOAT DEFAULT 0.85 CHECK (min_match_score >= 0.0 AND min_match_score <= 1.0),
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );

        CREATE INDEX idx_notification_settings_user_id ON public.notification_settings(user_id);

        ALTER TABLE public.notification_settings ENABLE ROW LEVEL SECURITY;

        CREATE POLICY "Users can view their own notification settings"
            ON public.notification_settings FOR SELECT
            USING (auth.uid() = user_id);

        CREATE POLICY "Users can insert their own notification settings"
            ON public.notification_settings FOR INSERT
            WITH CHECK (auth.uid() = user_id);

        CREATE POLICY "Users can update their own notification settings"
            ON public.notification_settings FOR UPDATE
            USING (auth.uid() = user_id);

        RAISE NOTICE 'Created notification_settings table';
    ELSE
        RAISE NOTICE 'Notification_settings table already exists, skipping';
    END IF;
END $$;

-- 8. Final verification
DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name IN ('users', 'documents', 'jobs', 'bookmarks', 'applications', 'notifications', 'notification_settings');
    
    RAISE NOTICE '============================================';
    RAISE NOTICE 'AlignCV Schema Setup Complete!';
    RAISE NOTICE 'Tables created/verified: % out of 7', table_count;
    RAISE NOTICE '============================================';
    RAISE NOTICE 'Tables: users, documents, jobs, bookmarks, applications, notifications, notification_settings';
    RAISE NOTICE 'All RLS policies enabled';
    RAISE NOTICE 'All indexes created';
    RAISE NOTICE '============================================';
END $$;
