/**
 * Thumbnail utility functions
 * Handles course thumbnail URLs consistently across the application
 */

/**
 * Get thumbnail URL for a course
 * @param {Object} course - Course object
 * @returns {string|null} - Thumbnail URL or null
 */
export const getThumbnailUrl = (course) => {
  if (!course) return null;
  
  // If course has a thumbnail_url, check if it's a Supabase storage URL or external URL
  if (course.thumbnail_url) {
    // If it's a Supabase storage URL, use our backend API to serve it
    if (isSupabaseStorageUrl(course.thumbnail_url)) {
      return `http://localhost:8000/api/thumbnails/course/${course.id}`;
    } else {
      // For external URLs (like Unsplash), use them directly
      return course.thumbnail_url;
    }
  }
  
  return null;
};

/**
 * Check if a course has a valid thumbnail
 * @param {Object} course - Course object
 * @returns {boolean} - True if course has a thumbnail
 */
export const hasThumbnail = (course) => {
  return !!(course?.thumbnail_url && course.thumbnail_url.trim() !== '');
};

/**
 * Get fallback thumbnail component for courses without thumbnails
 * @param {string} size - Size class for the icon (e.g., 'w-12 h-12')
 * @returns {JSX.Element} - Fallback thumbnail component
 */
export const getFallbackThumbnail = (size = 'w-12 h-12') => {
  return (
    <div className={`w-full h-full flex items-center justify-center bg-gradient-to-br from-primary-100 to-secondary-100`}>
      <svg className={`${size} text-primary-500`} fill="currentColor" viewBox="0 0 20 20">
        <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    </div>
  );
};

/**
 * Thumbnail component with fallback
 * @param {Object} course - Course object
 * @param {string} className - CSS classes for the image
 * @param {string} alt - Alt text for the image
 * @returns {JSX.Element} - Thumbnail component
 */
export const CourseThumbnail = ({ course, className = "w-full h-full object-cover", alt }) => {
  const thumbnailUrl = getThumbnailUrl(course);
  const hasValidThumbnail = hasThumbnail(course);
  
  if (thumbnailUrl && hasValidThumbnail) {
    return (
      <>
        <img
          src={thumbnailUrl}
          alt={alt || course?.title || 'Course thumbnail'}
          className={className}
          onError={(e) => {
            // If image fails to load, show fallback
            e.target.style.display = 'none';
            const fallback = e.target.nextElementSibling;
            if (fallback) fallback.style.display = 'flex';
          }}
        />
        <div 
          className="w-full h-full flex items-center justify-center bg-gradient-to-br from-primary-100 to-secondary-100" 
          style={{ display: 'none' }}
        >
          <svg className="w-12 h-12 text-primary-500" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
      </>
    );
  }
  
  return getFallbackThumbnail();
};

/**
 * Check if a URL is a Supabase storage URL
 * @param {string} url - URL to check
 * @returns {boolean} - True if it's a Supabase storage URL
 */
export const isSupabaseStorageUrl = (url) => {
  return url && url.includes('/storage/v1/object/public/');
};

/**
 * Convert Supabase storage URL to backend API URL
 * @param {string} supabaseUrl - Original Supabase URL
 * @param {string} resourceId - Resource ID (course ID, etc.)
 * @param {string} resourceType - Type of resource ('course', etc.)
 * @returns {string} - Backend API URL
 */
export const convertToBackendUrl = (supabaseUrl, resourceId, resourceType) => {
  if (isSupabaseStorageUrl(supabaseUrl)) {
    return `http://localhost:8000/api/thumbnails/${resourceType}/${resourceId}`;
  }
  return supabaseUrl;
};
