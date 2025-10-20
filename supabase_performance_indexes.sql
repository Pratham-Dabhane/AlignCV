-- ============================================
-- AlignCV - Performance Indexes for Supabase
-- ============================================
-- Run this in Supabase SQL Editor to improve query performance
-- These indexes speed up common queries on user_id, created_at, and job_id

-- ============================================
-- Documents Table Indexes
-- ============================================
DO $$
BEGIN
    -- Index on user_id for fast user document lookups
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'documents' AND indexname = 'idx_documents_user_id'
    ) THEN
        CREATE INDEX idx_documents_user_id ON documents(user_id);
        RAISE NOTICE 'Created index: idx_documents_user_id';
    END IF;

    -- Index on created_at for sorting and filtering
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'documents' AND indexname = 'idx_documents_created_at'
    ) THEN
        CREATE INDEX idx_documents_created_at ON documents(created_at DESC);
        RAISE NOTICE 'Created index: idx_documents_created_at';
    END IF;

    -- Composite index for user_id + created_at (common query pattern)
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'documents' AND indexname = 'idx_documents_user_created'
    ) THEN
        CREATE INDEX idx_documents_user_created ON documents(user_id, created_at DESC);
        RAISE NOTICE 'Created index: idx_documents_user_created';
    END IF;
END $$;

-- ============================================
-- Jobs Table Indexes
-- ============================================
DO $$
BEGIN
    -- Index on job_id (TEXT field) for fast lookups
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'jobs' AND indexname = 'idx_jobs_job_id'
    ) THEN
        CREATE INDEX idx_jobs_job_id ON jobs(job_id);
        RAISE NOTICE 'Created index: idx_jobs_job_id';
    END IF;

    -- Index on created_at for sorting
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'jobs' AND indexname = 'idx_jobs_created_at'
    ) THEN
        CREATE INDEX idx_jobs_created_at ON jobs(created_at DESC);
        RAISE NOTICE 'Created index: idx_jobs_created_at';
    END IF;
END $$;

-- ============================================
-- Bookmarks Table Indexes
-- ============================================
DO $$
BEGIN
    -- Index on user_id for fast user bookmark lookups
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'bookmarks' AND indexname = 'idx_bookmarks_user_id'
    ) THEN
        CREATE INDEX idx_bookmarks_user_id ON bookmarks(user_id);
        RAISE NOTICE 'Created index: idx_bookmarks_user_id';
    END IF;

    -- Index on job_id for checking if job is bookmarked
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'bookmarks' AND indexname = 'idx_bookmarks_job_id'
    ) THEN
        CREATE INDEX idx_bookmarks_job_id ON bookmarks(job_id);
        RAISE NOTICE 'Created index: idx_bookmarks_job_id';
    END IF;

    -- Composite index for user_id + job_id (checking if user bookmarked specific job)
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'bookmarks' AND indexname = 'idx_bookmarks_user_job'
    ) THEN
        CREATE INDEX idx_bookmarks_user_job ON bookmarks(user_id, job_id);
        RAISE NOTICE 'Created index: idx_bookmarks_user_job';
    END IF;

    -- Index on created_at for sorting
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'bookmarks' AND indexname = 'idx_bookmarks_created_at'
    ) THEN
        CREATE INDEX idx_bookmarks_created_at ON bookmarks(created_at DESC);
        RAISE NOTICE 'Created index: idx_bookmarks_created_at';
    END IF;
END $$;

-- ============================================
-- Applications Table Indexes
-- ============================================
DO $$
BEGIN
    -- Index on user_id for fast user application lookups
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'applications' AND indexname = 'idx_applications_user_id'
    ) THEN
        CREATE INDEX idx_applications_user_id ON applications(user_id);
        RAISE NOTICE 'Created index: idx_applications_user_id';
    END IF;

    -- Index on job_id for checking applications per job
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'applications' AND indexname = 'idx_applications_job_id'
    ) THEN
        CREATE INDEX idx_applications_job_id ON applications(job_id);
        RAISE NOTICE 'Created index: idx_applications_job_id';
    END IF;

    -- Composite index for user_id + job_id (checking if user applied to specific job)
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'applications' AND indexname = 'idx_applications_user_job'
    ) THEN
        CREATE INDEX idx_applications_user_job ON applications(user_id, job_id);
        RAISE NOTICE 'Created index: idx_applications_user_job';
    END IF;

    -- Index on status for filtering (applied, interviewing, rejected, etc.)
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'applications' AND indexname = 'idx_applications_status'
    ) THEN
        CREATE INDEX idx_applications_status ON applications(status);
        RAISE NOTICE 'Created index: idx_applications_status';
    END IF;

    -- Composite index for user_id + status (user's applications by status)
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'applications' AND indexname = 'idx_applications_user_status'
    ) THEN
        CREATE INDEX idx_applications_user_status ON applications(user_id, status);
        RAISE NOTICE 'Created index: idx_applications_user_status';
    END IF;

    -- Index on applied_at for sorting
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'applications' AND indexname = 'idx_applications_applied_at'
    ) THEN
        CREATE INDEX idx_applications_applied_at ON applications(applied_at DESC);
        RAISE NOTICE 'Created index: idx_applications_applied_at';
    END IF;
END $$;

-- ============================================
-- Notifications Table Indexes
-- ============================================
DO $$
BEGIN
    -- Index on user_id for fast user notification lookups
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'notifications' AND indexname = 'idx_notifications_user_id'
    ) THEN
        CREATE INDEX idx_notifications_user_id ON notifications(user_id);
        RAISE NOTICE 'Created index: idx_notifications_user_id';
    END IF;

    -- Index on is_read for filtering unread notifications
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'notifications' AND indexname = 'idx_notifications_is_read'
    ) THEN
        CREATE INDEX idx_notifications_is_read ON notifications(is_read);
        RAISE NOTICE 'Created index: idx_notifications_is_read';
    END IF;

    -- Composite index for user_id + is_read (user's unread notifications)
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'notifications' AND indexname = 'idx_notifications_user_read'
    ) THEN
        CREATE INDEX idx_notifications_user_read ON notifications(user_id, is_read);
        RAISE NOTICE 'Created index: idx_notifications_user_read';
    END IF;

    -- Index on created_at for sorting
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'notifications' AND indexname = 'idx_notifications_created_at'
    ) THEN
        CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);
        RAISE NOTICE 'Created index: idx_notifications_created_at';
    END IF;

    -- Composite index for user_id + created_at (user's notifications sorted by date)
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'notifications' AND indexname = 'idx_notifications_user_created'
    ) THEN
        CREATE INDEX idx_notifications_user_created ON notifications(user_id, created_at DESC);
        RAISE NOTICE 'Created index: idx_notifications_user_created';
    END IF;
END $$;

-- ============================================
-- Notification Settings Table Indexes
-- ============================================
DO $$
BEGIN
    -- Index on user_id (should be unique already via constraint, but explicit index helps)
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'notification_settings' AND indexname = 'idx_notification_settings_user_id'
    ) THEN
        CREATE INDEX idx_notification_settings_user_id ON notification_settings(user_id);
        RAISE NOTICE 'Created index: idx_notification_settings_user_id';
    END IF;
END $$;

-- ============================================
-- Users Table Indexes
-- ============================================
DO $$
BEGIN
    -- Index on email for fast login lookups (should already exist from unique constraint)
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'users' AND indexname = 'idx_users_email'
    ) THEN
        CREATE INDEX idx_users_email ON users(email);
        RAISE NOTICE 'Created index: idx_users_email';
    END IF;

    -- Index on created_at for sorting
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'users' AND indexname = 'idx_users_created_at'
    ) THEN
        CREATE INDEX idx_users_created_at ON users(created_at DESC);
        RAISE NOTICE 'Created index: idx_users_created_at';
    END IF;
END $$;

-- ============================================
-- Analyze Tables (Update Statistics)
-- ============================================
-- This helps PostgreSQL query planner make better decisions
ANALYZE documents;
ANALYZE jobs;
ANALYZE bookmarks;
ANALYZE applications;
ANALYZE notifications;
ANALYZE notification_settings;
ANALYZE users;

-- ============================================
-- DONE!
-- ============================================
-- All indexes created successfully.
-- Your queries should now be significantly faster.
