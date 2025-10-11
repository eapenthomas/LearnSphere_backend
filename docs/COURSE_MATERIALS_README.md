# LearnSphere Course Materials System

A comprehensive file management system for course materials with AWS S3 storage and Supabase metadata management.

## 🚀 Features

- **Multi-file Upload**: Upload multiple files simultaneously
- **AWS S3 Integration**: Secure cloud storage with organized folder structure
- **Permission-based Access**: Teachers manage, students view enrolled course materials
- **Metadata Storage**: File information stored in Supabase with relationships
- **Presigned URLs**: Secure download links with expiration
- **Soft Delete**: Materials are deactivated, not permanently deleted
- **File Type Support**: PDF, DOC, images, videos, and more

## 📁 File Structure

```
backend/
├── course_materials_schema.sql     # Database schema and policies
├── s3_utils.py                    # AWS S3 utility functions
├── course_permissions.py          # Permission verification utilities
├── course_materials_routes.py     # FastAPI route handlers
├── test_course_materials.py       # Comprehensive test suite
└── COURSE_MATERIALS_README.md     # This documentation
```

## 🗄️ Database Schema

### course_materials Table

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| course_id | UUID | Foreign key to courses table |
| file_name | TEXT | Original filename |
| file_url | TEXT | S3 URL of the file |
| file_size | BIGINT | File size in bytes |
| file_type | TEXT | MIME type |
| uploaded_by | UUID | Foreign key to profiles table |
| uploaded_at | TIMESTAMP | Upload timestamp |
| updated_at | TIMESTAMP | Last update timestamp |
| description | TEXT | Optional file description |
| is_active | BOOLEAN | Soft delete flag |

### Relationships

- `course_id` → `courses.id` (CASCADE DELETE)
- `uploaded_by` → `profiles.id` (CASCADE DELETE)

## ☁️ AWS S3 Structure

Files are organized in S3 with the following structure:

```
bucket-name/
└── courses/
    └── {course_id}/
        ├── 20241210_143022_a1b2c3d4_document.pdf
        ├── 20241210_143055_e5f6g7h8_presentation.pptx
        └── 20241210_143120_i9j0k1l2_video.mp4
```

### File Naming Convention

`{timestamp}_{unique_id}_{original_filename}`

- **timestamp**: YYYYMMDD_HHMMSS format
- **unique_id**: 8-character UUID segment
- **original_filename**: User's original filename

## 🔧 Setup Instructions

### 1. Environment Variables

Add to your `.env` file:

```env
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_id_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key_here
AWS_S3_BUCKET_NAME=learnsphere-course-materials
AWS_S3_REGION=us-east-1

# Supabase Configuration (existing)
SUPABASE_URL=your_supabase_url_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here
```

### 2. Install Dependencies

```bash
pip install boto3 botocore
```

### 3. Database Setup

Run the SQL schema in your Supabase SQL editor:

```bash
# Execute the contents of course_materials_schema.sql
```

### 4. AWS S3 Setup

1. Create an S3 bucket (e.g., `learnsphere-course-materials`)
2. Configure bucket permissions for your AWS credentials
3. Optionally set up CORS if needed for direct browser uploads

### 5. Test the Setup

```bash
python test_course_materials.py
```

## 📡 API Endpoints

### Upload Materials

```http
POST /courses/{course_id}/materials
Content-Type: multipart/form-data

files: [file1, file2, ...]
description: "Optional description"
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully uploaded 2 file(s)",
  "materials": [
    {
      "id": "uuid",
      "course_id": "uuid",
      "file_name": "document.pdf",
      "file_url": "https://bucket.s3.region.amazonaws.com/courses/uuid/file.pdf",
      "file_size": 1024000,
      "file_type": "application/pdf",
      "uploaded_by": "uuid",
      "uploaded_at": "2024-12-10T14:30:22Z",
      "description": "Course syllabus"
    }
  ]
}
```

### List Materials

```http
GET /courses/{course_id}/materials
```

**Response:**
```json
{
  "success": true,
  "materials": [...],
  "total_count": 5
}
```

### Get Download URL

```http
GET /courses/{course_id}/materials/{material_id}/download
```

**Response:**
```json
{
  "success": true,
  "download_url": "https://presigned-url...",
  "file_name": "document.pdf",
  "expires_in": 3600
}
```

### Delete Material

```http
DELETE /courses/{course_id}/materials/{material_id}
```

**Response:**
```json
{
  "success": true,
  "message": "Course material deleted successfully"
}
```

## 🔒 Permissions

### Teachers
- ✅ Upload materials to their own courses
- ✅ View materials for their own courses
- ✅ Delete materials from their own courses
- ✅ Generate download URLs for their course materials

### Students
- ✅ View materials for enrolled courses
- ✅ Generate download URLs for enrolled course materials
- ❌ Upload materials
- ❌ Delete materials

### Security Features
- Course ownership verification
- Student enrollment verification
- File size limits (100MB max)
- Presigned URLs with expiration
- Soft delete for audit trails

## 🧪 Testing

### Run Tests

```bash
# Basic environment and connection tests
python test_course_materials.py

# View API documentation
python test_course_materials.py --docs
```

### Manual Testing

1. **Upload Test:**
   ```bash
   curl -X POST "http://localhost:8000/courses/{course_id}/materials" \
        -F "files=@test.pdf" \
        -F "description=Test upload"
   ```

2. **List Test:**
   ```bash
   curl "http://localhost:8000/courses/{course_id}/materials"
   ```

3. **Download Test:**
   ```bash
   curl "http://localhost:8000/courses/{course_id}/materials/{material_id}/download"
   ```

## 🚨 Error Handling

The system provides comprehensive error handling:

- **400 Bad Request**: Invalid file, missing parameters
- **403 Forbidden**: Permission denied, not enrolled/owner
- **404 Not Found**: Course/material not found
- **500 Internal Server Error**: S3/database errors

## 📈 Performance Considerations

- **File Size Limit**: 100MB per file
- **Upload Limit**: 10 files per request
- **Presigned URL Expiry**: 1 hour default
- **Database Indexing**: Optimized queries with proper indexes

## 🔄 Integration with Frontend

The backend is ready for frontend integration. You'll need to:

1. Implement proper authentication in `get_current_user()`
2. Add file upload UI components
3. Handle multipart form data
4. Display download links using presigned URLs

## 🛠️ Maintenance

### Monitoring
- Monitor S3 storage usage
- Track upload/download metrics
- Review error logs regularly

### Cleanup
- Implement periodic cleanup of soft-deleted materials
- Monitor and clean up orphaned S3 files
- Archive old course materials

## 📞 Support

For issues or questions:
1. Check the test results: `python test_course_materials.py`
2. Verify environment variables are set correctly
3. Ensure AWS credentials have proper S3 permissions
4. Check Supabase database connectivity
