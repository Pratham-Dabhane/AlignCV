-- ============================================
-- ALIGNCV SUPABASE SCHEMA SETUP
-- Run this entire script in Supabase SQL Editor
-- ============================================

-- 1. Fix documents table column name to match frontend expectations (skip if already renamed)
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'documents' 
        AND column_name = 'filename'
    ) THEN
        ALTER TABLE public.documents RENAME COLUMN filename TO file_name;
    END IF;
END $$;

-- 2. Create bookmarks table
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
    END IF;
END $$;

-- 3. Create applications table
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
            applied_date DATE DEFAULT CURRENT_DATE,
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
    END IF;
END $$;

-- 3b. Create jobs table (for storing scraped job data)
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
    END IF;
END $$;

-- 4. Create notifications table
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'notifications') THEN
        CREATE TABLE public.notifications (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            job_id UUID,
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
    END IF;
END $$;

-- 5. Create notification_settings table
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
    END IF;
END $$;

-- 6. Verify all tables exist
DO $$
BEGIN
    RAISE NOTICE 'Schema setup complete!';
    RAISE NOTICE 'Tables created: bookmarks, applications, jobs, notifications, notification_settings';
    RAISE NOTICE 'Documents table updated: filename -> file_name';
END $$;

