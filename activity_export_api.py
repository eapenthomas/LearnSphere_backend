"""
Activity Export API
Professional PDF export functionality for activity logs
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
import os
from datetime import datetime, timezone, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import tempfile
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

router = APIRouter()

@router.get("/export-activity-logs")
async def export_activity_logs(
    days: int = Query(30, ge=1, le=365, description="Number of days to include in the report"),
    format: str = Query("pdf", regex="^(pdf|csv)$", description="Export format")
):
    """Export activity logs as a professional PDF or CSV report"""
    try:
        # Calculate date range
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Fetch activity data
        activity_data = await get_activity_data(start_date, end_date)
        
        if format == "pdf":
            return await generate_pdf_report(activity_data, start_date, end_date)
        else:
            return await generate_csv_report(activity_data, start_date, end_date)
            
    except Exception as e:
        print(f"Error exporting activity logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_activity_data(start_date: datetime, end_date: datetime):
    """Fetch comprehensive activity data from the database"""
    
    activity_logs = []
    
    try:
        # Get user registrations
        users_response = supabase.table('profiles').select('''
            id, full_name, role, created_at, is_active, approval_status
        ''').gte('created_at', start_date.isoformat()).lte('created_at', end_date.isoformat()).order('created_at', desc=True).execute()
        
        for user in users_response.data or []:
            activity_logs.append({
                'timestamp': user['created_at'],
                'type': 'User Registration',
                'description': f"New {user['role']} account created: {user['full_name']}",
                'user': user['full_name'],
                'status': user.get('approval_status', 'active'),
                'category': 'Authentication'
            })
        
        # Get course activities
        courses_response = supabase.table('courses').select('''
            id, title, created_at,
            profiles!courses_teacher_id_fkey(full_name)
        ''').gte('created_at', start_date.isoformat()).lte('created_at', end_date.isoformat()).order('created_at', desc=True).execute()
        
        for course in courses_response.data or []:
            teacher_name = course.get('profiles', {}).get('full_name', 'Unknown Teacher') if course.get('profiles') else 'Unknown Teacher'
            activity_logs.append({
                'timestamp': course['created_at'],
                'type': 'Course Creation',
                'description': f"Course '{course['title']}' created by {teacher_name}",
                'user': teacher_name,
                'status': 'active',
                'category': 'Content Management'
            })
        
        # Get assignment submissions
        assignment_subs = supabase.table('assignment_submissions').select('''
            submitted_at, score, max_score,
            profiles:student_id(full_name),
            assignments:assignment_id(title)
        ''').gte('submitted_at', start_date.isoformat()).lte('submitted_at', end_date.isoformat()).order('submitted_at', desc=True).limit(100).execute()
        
        for sub in assignment_subs.data or []:
            student_name = sub.get('profiles', {}).get('full_name', 'Unknown Student') if sub.get('profiles') else 'Unknown Student'
            assignment_title = sub.get('assignments', {}).get('title', 'Unknown Assignment') if sub.get('assignments') else 'Unknown Assignment'
            score_text = f"Score: {sub.get('score', 0)}/{sub.get('max_score', 0)}" if sub.get('max_score') else "Submitted"
            
            activity_logs.append({
                'timestamp': sub['submitted_at'],
                'type': 'Assignment Submission',
                'description': f"{student_name} submitted '{assignment_title}' - {score_text}",
                'user': student_name,
                'status': 'completed',
                'category': 'Academic Activity'
            })
        
        # Get quiz submissions
        quiz_subs = supabase.table('quiz_submissions').select('''
            submitted_at, score, total_marks,
            profiles:student_id(full_name),
            quizzes:quiz_id(title)
        ''').gte('submitted_at', start_date.isoformat()).lte('submitted_at', end_date.isoformat()).order('submitted_at', desc=True).limit(100).execute()
        
        for sub in quiz_subs.data or []:
            student_name = sub.get('profiles', {}).get('full_name', 'Unknown Student') if sub.get('profiles') else 'Unknown Student'
            quiz_title = sub.get('quizzes', {}).get('title', 'Unknown Quiz') if sub.get('quizzes') else 'Unknown Quiz'
            score_text = f"Score: {sub.get('score', 0)}/{sub.get('total_marks', 0)}" if sub.get('total_marks') else "Completed"
            
            activity_logs.append({
                'timestamp': sub['submitted_at'],
                'type': 'Quiz Submission',
                'description': f"{student_name} completed '{quiz_title}' - {score_text}",
                'user': student_name,
                'status': 'completed',
                'category': 'Academic Activity'
            })
        
        # Sort all activities by timestamp
        activity_logs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return activity_logs[:200]  # Limit to most recent 200 activities
        
    except Exception as e:
        print(f"Error fetching activity data: {e}")
        return []

async def generate_pdf_report(activity_data, start_date, end_date):
    """Generate a professional PDF report with LearnSphere branding"""
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_file.close()
    
    try:
        # Create PDF document
        doc = SimpleDocTemplate(
            temp_file.name,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1e40af')
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#374151')
        )
        
        # Build content
        content = []
        
        # Title
        content.append(Paragraph("LearnSphere", title_style))
        content.append(Paragraph("Activity Logs Report", subtitle_style))
        content.append(Spacer(1, 20))
        
        # Report info
        report_info = f"""
        <b>Report Period:</b> {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}<br/>
        <b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
        <b>Total Activities:</b> {len(activity_data)}<br/>
        """
        content.append(Paragraph(report_info, styles['Normal']))
        content.append(Spacer(1, 30))
        
        # Activity summary
        if activity_data:
            # Create summary table
            summary_data = {}
            for activity in activity_data:
                category = activity.get('category', 'Other')
                summary_data[category] = summary_data.get(category, 0) + 1
            
            summary_table_data = [['Category', 'Count']]
            for category, count in summary_data.items():
                summary_table_data.append([category, str(count)])
            
            summary_table = Table(summary_table_data, colWidths=[3*inch, 1*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0'))
            ]))
            
            content.append(Paragraph("<b>Activity Summary</b>", styles['Heading3']))
            content.append(summary_table)
            content.append(Spacer(1, 30))
            
            # Detailed activity table
            content.append(Paragraph("<b>Detailed Activity Log</b>", styles['Heading3']))
            
            # Create activity table
            table_data = [['Date/Time', 'Type', 'User', 'Description']]
            
            for activity in activity_data[:50]:  # Limit to first 50 for PDF
                timestamp = datetime.fromisoformat(activity['timestamp'].replace('Z', '+00:00'))
                formatted_time = timestamp.strftime('%m/%d/%Y %I:%M %p')
                
                table_data.append([
                    formatted_time,
                    activity['type'],
                    activity['user'][:20] + '...' if len(activity['user']) > 20 else activity['user'],
                    activity['description'][:60] + '...' if len(activity['description']) > 60 else activity['description']
                ])
            
            activity_table = Table(table_data, colWidths=[1.5*inch, 1.2*inch, 1.3*inch, 3*inch])
            activity_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            
            content.append(activity_table)
        else:
            content.append(Paragraph("No activity data found for the selected period.", styles['Normal']))
        
        # Build PDF
        doc.build(content)
        
        # Return file response
        return FileResponse(
            temp_file.name,
            media_type='application/pdf',
            filename=f'learnsphere_activity_report_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}.pdf'
        )
        
    except Exception as e:
        # Clean up temp file on error
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        raise e

async def generate_csv_report(activity_data, start_date, end_date):
    """Generate a CSV report for activity logs"""

    import csv

    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w', newline='', encoding='utf-8')

    try:
        writer = csv.writer(temp_file)

        # Write header
        writer.writerow(['Date/Time', 'Type', 'Category', 'User', 'Description', 'Status'])

        # Write data
        for activity in activity_data:
            timestamp = datetime.fromisoformat(activity['timestamp'].replace('Z', '+00:00'))
            formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S')

            writer.writerow([
                formatted_time,
                activity['type'],
                activity['category'],
                activity['user'],
                activity['description'],
                activity['status']
            ])

        temp_file.close()

        # Return file response
        return FileResponse(
            temp_file.name,
            media_type='text/csv',
            filename=f'learnsphere_activity_report_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}.csv'
        )

    except Exception as e:
        temp_file.close()
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        raise e
