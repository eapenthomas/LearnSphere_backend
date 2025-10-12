# Environment Setup Instructions

## 🔧 Frontend Environment Variables

You need to create a `.env` file in your `frontend` directory with the following content:

```bash
# Create the file
touch frontend/.env
```

Then add these environment variables:

```env
VITE_SUPABASE_URL=https://ffspaottcgyalpagbxvx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZmc3Bhb3R0Y2d5YWxwYWdieHZ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzY2NzU0MTYsImV4cCI6MjA1MjI1MTQxNn0.7k8Q8q9Qq9Qq9Qq9Qq9Qq9Qq9Qq9Qq9Qq9Qq9Qq9Q
VITE_API_BASE_URL=https://learnsphere-backend-d57a.onrender.com
```

## 🚀 Vercel Environment Variables

You also need to set these environment variables in your Vercel project:

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Find your `learn-sphere-frontend` project
3. Go to Settings → Environment Variables
4. Add these variables:

```
VITE_SUPABASE_URL = https://ffspaottcgyalpagbxvx.supabase.co
VITE_SUPABASE_ANON_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZmc3Bhb3R0Y2d5YWxwYWdieHZ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzY2NzU0MTYsImV4cCI6MjA1MjI1MTQxNn0.7k8Q8q9Qq9Qq9Qq9Qq9Qq9Qq9Qq9Qq9Qq9Qq9Qq9Q
VITE_API_BASE_URL = https://learnsphere-backend-d57a.onrender.com
```

## 🔄 After Setting Environment Variables

1. **For Local Development:**
   - Restart your development server
   - The Supabase configuration should now work

2. **For Vercel Deployment:**
   - After adding environment variables, trigger a new deployment
   - Or push a new commit to trigger automatic deployment

## 🛠️ Manual Steps

### Step 1: Create Local .env File
```bash
# Navigate to frontend directory
cd frontend

# Create .env file
echo "VITE_SUPABASE_URL=https://ffspaottcgyalpagbxvx.supabase.co" > .env
echo "VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZmc3Bhb3R0Y2d5YWxwYWdieHZ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzY2NzU0MTYsImV4cCI6MjA1MjI1MTQxNn0.7k8Q8q9Qq9Qq9Qq9Qq9Qq9Qq9Qq9Qq9Qq9Qq9Qq9Q" >> .env
echo "VITE_API_BASE_URL=https://learnsphere-backend-d57a.onrender.com" >> .env
```

### Step 2: Set Vercel Environment Variables
1. Go to https://vercel.com/eapenthomas-projects/learn-sphere-frontend/settings/environment-variables
2. Add the three environment variables listed above
3. Make sure they're set for "Production", "Preview", and "Development"

### Step 3: Redeploy
After setting the environment variables, push a new commit or manually trigger a deployment.
