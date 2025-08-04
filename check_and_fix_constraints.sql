-- Check and fix foreign key constraints on profiles table
-- Run this SQL in your Supabase SQL editor

-- First, let's see what constraints exist
SELECT 
    conname as constraint_name,
    contype as constraint_type,
    pg_get_constraintdef(oid) as constraint_definition
FROM pg_constraint 
WHERE conrelid = 'profiles'::regclass;

-- Remove the foreign key constraint that's causing issues
ALTER TABLE profiles DROP CONSTRAINT IF EXISTS profiles_id_fkey;

-- Also remove any other potential foreign key constraints
ALTER TABLE profiles DROP CONSTRAINT IF EXISTS profiles_user_id_fkey;
ALTER TABLE profiles DROP CONSTRAINT IF EXISTS fk_profiles_user_id;

-- Check constraints again after removal
SELECT 
    conname as constraint_name,
    contype as constraint_type,
    pg_get_constraintdef(oid) as constraint_definition
FROM pg_constraint 
WHERE conrelid = 'profiles'::regclass;
