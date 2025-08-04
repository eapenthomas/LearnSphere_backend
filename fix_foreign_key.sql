-- Fix foreign key constraint issue
-- Run this SQL in your Supabase SQL editor

-- Remove foreign key constraint that references auth.users
-- This allows us to use custom UUIDs for manual registration
ALTER TABLE profiles DROP CONSTRAINT IF EXISTS profiles_id_fkey;

-- Verify the constraint is removed
SELECT conname, contype 
FROM pg_constraint 
WHERE conrelid = 'profiles'::regclass;
