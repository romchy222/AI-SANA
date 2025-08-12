"""
Enhanced API endpoints for AI-SANA system
Provides specific functionality for each agent type
"""

from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
import os
import logging
from datetime import datetime

from enhanced_agents import (
    AIAbiturEnhanced, KadrAIEnhanced, UniNavEnhanced, 
    CareerNavigatorEnhanced, UniRoomEnhanced
)
from models import db, StudentRequest, DocumentTemplate, Schedule, JobPosting, HousingRoom

logger = logging.getLogger(__name__)

# Create blueprint for enhanced API
api_enhanced = Blueprint('api_enhanced', __name__, url_prefix='/api/enhanced')

# Initialize enhanced agent functionalities
abitur_enhanced = AIAbiturEnhanced()
kadrai_enhanced = KadrAIEnhanced()
uninav_enhanced = UniNavEnhanced()
career_enhanced = CareerNavigatorEnhanced()
uniroom_enhanced = UniRoomEnhanced()

# Helper function to get language from request
def get_language():
    return request.args.get('lang', session.get('language', 'ru'))

# AI-Abitur Enhanced Endpoints
@api_enhanced.route('/abitur/admission-info', methods=['GET'])
def get_admission_info():
    """Get comprehensive admission information"""
    try:
        language = get_language()
        info = abitur_enhanced.get_admission_info(language)
        return jsonify({'success': True, 'data': info})
    except Exception as e:
        logger.error(f"Error getting admission info: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_enhanced.route('/abitur/templates', methods=['GET'])
def get_admission_templates():
    """Get admission document templates"""
    try:
        language = get_language()
        templates = abitur_enhanced.get_application_templates(language)
        return jsonify({'success': True, 'data': templates})
    except Exception as e:
        logger.error(f"Error getting admission templates: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_enhanced.route('/abitur/track-application/<application_id>', methods=['GET'])
def track_application(application_id):
    """Track application status"""
    try:
        status = abitur_enhanced.track_application_status(application_id)
        return jsonify({'success': True, 'data': status})
    except Exception as e:
        logger.error(f"Error tracking application: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_enhanced.route('/abitur/program-requirements/<program_name>', methods=['GET'])
def get_program_requirements(program_name):
    """Get specific program requirements"""
    try:
        language = get_language()
        requirements = abitur_enhanced.get_program_requirements(program_name, language)
        return jsonify({'success': True, 'data': requirements})
    except Exception as e:
        logger.error(f"Error getting program requirements: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# KadrAI Enhanced Endpoints
@api_enhanced.route('/kadrai/procedures', methods=['GET'])
def get_hr_procedures():
    """Get HR procedures and regulations"""
    try:
        language = get_language()
        procedures = kadrai_enhanced.get_hr_procedures(language)
        return jsonify({'success': True, 'data': procedures})
    except Exception as e:
        logger.error(f"Error getting HR procedures: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_enhanced.route('/kadrai/leave-calendar', methods=['GET'])
def get_leave_calendar():
    """Get vacation/leave schedule"""
    try:
        language = get_language()
        department = request.args.get('department')
        calendar = kadrai_enhanced.get_leave_calendar(department, language)
        return jsonify({'success': True, 'data': calendar})
    except Exception as e:
        logger.error(f"Error getting leave calendar: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_enhanced.route('/kadrai/submit-request', methods=['POST'])
def submit_hr_request():
    """Submit HR-related request"""
    try:
        request_data = request.get_json()
        result = kadrai_enhanced.submit_hr_request(request_data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error submitting HR request: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_enhanced.route('/kadrai/templates', methods=['GET'])
def get_hr_templates():
    """Get HR document templates"""
    try:
        language = get_language()
        templates = kadrai_enhanced.get_templates(language)
        return jsonify({'success': True, 'data': templates})
    except Exception as e:
        logger.error(f"Error getting HR templates: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# UniNav Enhanced Endpoints
@api_enhanced.route('/uninav/schedule', methods=['GET'])
def get_current_schedule():
    """Get current class schedule"""
    try:
        language = get_language()
        group = request.args.get('group')
        schedule = uninav_enhanced.get_current_schedule(group, language)
        return jsonify({'success': True, 'data': schedule})
    except Exception as e:
        logger.error(f"Error getting schedule: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_enhanced.route('/uninav/exams', methods=['GET'])
def get_exam_schedule():
    """Get exam schedule"""
    try:
        language = get_language()
        group = request.args.get('group')
        exams = uninav_enhanced.get_exam_schedule(group, language)
        return jsonify({'success': True, 'data': exams})
    except Exception as e:
        logger.error(f"Error getting exam schedule: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_enhanced.route('/uninav/faculty-info', methods=['GET'])
def get_faculty_info():
    """Get faculty and instructor information"""
    try:
        language = get_language()
        faculty_name = request.args.get('faculty')
        info = uninav_enhanced.get_faculty_info(faculty_name, language)
        return jsonify({'success': True, 'data': info})
    except Exception as e:
        logger.error(f"Error getting faculty info: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_enhanced.route('/uninav/submit-request', methods=['POST'])
def submit_academic_request():
    """Submit academic-related request"""
    try:
        request_data = request.get_json()
        result = uninav_enhanced.submit_academic_request(request_data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error submitting academic request: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# CareerNavigator Enhanced Endpoints
@api_enhanced.route('/career/jobs', methods=['GET'])
def search_jobs():
    """Search for job postings"""
    try:
        language = get_language()
        skills = request.args.getlist('skills')
        location = request.args.get('location')
        job_type = request.args.get('job_type')
        
        jobs = career_enhanced.search_jobs(skills, location, job_type, language)
        return jsonify({'success': True, 'data': jobs})
    except Exception as e:
        logger.error(f"Error searching jobs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_enhanced.route('/career/recommendations', methods=['POST'])
def get_career_recommendations():
    """Get personalized career recommendations"""
    try:
        language = get_language()
        student_profile = request.get_json()
        recommendations = career_enhanced.get_career_recommendations(student_profile, language)
        return jsonify({'success': True, 'data': recommendations})
    except Exception as e:
        logger.error(f"Error getting career recommendations: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_enhanced.route('/career/resume-template', methods=['POST'])
def create_resume_template():
    """Generate resume template"""
    try:
        language = get_language()
        student_data = request.get_json()
        template = career_enhanced.create_resume_template(student_data, language)
        return jsonify({'success': True, 'data': {'template': template}})
    except Exception as e:
        logger.error(f"Error creating resume template: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_enhanced.route('/career/interview-tips', methods=['GET'])
def get_interview_tips():
    """Get interview preparation tips"""
    try:
        language = get_language()
        job_type = request.args.get('job_type')
        tips = career_enhanced.get_interview_tips(job_type, language)
        return jsonify({'success': True, 'data': tips})
    except Exception as e:
        logger.error(f"Error getting interview tips: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# UniRoom Enhanced Endpoints
@api_enhanced.route('/uniroom/available-rooms', methods=['GET'])
def get_available_rooms():
    """Get available dormitory rooms"""
    try:
        language = get_language()
        room_type = request.args.get('room_type')
        rooms = uniroom_enhanced.get_available_rooms(room_type, language)
        return jsonify({'success': True, 'data': rooms})
    except Exception as e:
        logger.error(f"Error getting available rooms: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_enhanced.route('/uniroom/submit-request', methods=['POST'])
def submit_housing_request():
    """Submit housing-related request"""
    try:
        request_data = request.get_json()
        result = uniroom_enhanced.submit_housing_request(request_data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error submitting housing request: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_enhanced.route('/uniroom/rules', methods=['GET'])
def get_housing_rules():
    """Get dormitory rules and regulations"""
    try:
        language = get_language()
        rules = uniroom_enhanced.get_housing_rules(language)
        return jsonify({'success': True, 'data': rules})
    except Exception as e:
        logger.error(f"Error getting housing rules: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_enhanced.route('/uniroom/occupancy-status', methods=['GET'])
def check_occupancy_status():
    """Check room occupancy status"""
    try:
        room_id = request.args.get('room_id', type=int)
        building = request.args.get('building')
        status = uniroom_enhanced.check_occupancy_status(room_id, building)
        return jsonify({'success': True, 'data': status})
    except Exception as e:
        logger.error(f"Error checking occupancy status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_enhanced.route('/uniroom/maintenance-schedule', methods=['GET'])
def get_maintenance_schedule():
    """Get maintenance and inspection schedule"""
    try:
        language = get_language()
        building = request.args.get('building')
        schedule = uniroom_enhanced.get_maintenance_schedule(building, language)
        return jsonify({'success': True, 'data': schedule})
    except Exception as e:
        logger.error(f"Error getting maintenance schedule: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# General request tracking endpoints
@api_enhanced.route('/requests/track/<request_id>', methods=['GET'])
def track_request(request_id):
    """Track any type of request by ID"""
    try:
        request_obj = StudentRequest.query.filter_by(request_id=request_id).first()
        if not request_obj:
            return jsonify({'success': False, 'error': 'Request not found'}), 404
        
        data = {
            'request_id': request_obj.request_id,
            'title': request_obj.title,
            'type': request_obj.request_type,
            'category': request_obj.category,
            'status': request_obj.status,
            'submitted_at': request_obj.submitted_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': request_obj.updated_at.strftime('%Y-%m-%d %H:%M'),
            'assigned_to': request_obj.assigned_to,
            'processing_notes': request_obj.processing_notes,
            'priority': request_obj.priority
        }
        
        if request_obj.due_date:
            data['due_date'] = request_obj.due_date.strftime('%Y-%m-%d')
        
        if request_obj.completed_at:
            data['completed_at'] = request_obj.completed_at.strftime('%Y-%m-%d %H:%M')
        
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        logger.error(f"Error tracking request: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_enhanced.route('/requests/my-requests', methods=['GET'])
def get_my_requests():
    """Get user's requests"""
    try:
        student_email = request.args.get('email')
        student_id = request.args.get('student_id')
        
        if not student_email and not student_id:
            return jsonify({'success': False, 'error': 'Email or student_id required'}), 400
        
        query = StudentRequest.query
        if student_email:
            query = query.filter_by(student_email=student_email)
        if student_id:
            query = query.filter_by(student_id=student_id)
        
        requests = query.order_by(StudentRequest.created_at.desc()).limit(20).all()
        
        data = []
        for req in requests:
            item = {
                'request_id': req.request_id,
                'title': req.title,
                'type': req.request_type,
                'category': req.category,
                'status': req.status,
                'submitted_at': req.submitted_at.strftime('%Y-%m-%d %H:%M'),
                'assigned_to': req.assigned_to,
                'priority': req.priority
            }
            data.append(item)
        
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        logger.error(f"Error getting user requests: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Document template endpoints
@api_enhanced.route('/templates/<agent_type>', methods=['GET'])
def get_agent_templates(agent_type):
    """Get templates for specific agent"""
    try:
        language = get_language()
        templates = DocumentTemplate.query.filter_by(
            agent_type=agent_type,
            is_active=True
        ).all()
        
        data = []
        for template in templates:
            item = {
                'id': template.id,
                'name': template.get_name(language),
                'category': template.category,
                'instructions': template.get_instructions(language),
                'required_fields': template.required_fields,
                'file_path': template.file_path
            }
            data.append(item)
        
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        logger.error(f"Error getting agent templates: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_enhanced.route('/templates/<int:template_id>/content', methods=['GET'])
def get_template_content(template_id):
    """Get template content for filling"""
    try:
        template = DocumentTemplate.query.get(template_id)
        if not template:
            return jsonify({'success': False, 'error': 'Template not found'}), 404
        
        language = get_language()
        data = {
            'id': template.id,
            'name': template.get_name(language),
            'content': template.template_content,
            'required_fields': template.required_fields,
            'instructions': template.get_instructions(language)
        }
        
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        logger.error(f"Error getting template content: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Statistics and analytics endpoints
@api_enhanced.route('/stats/requests', methods=['GET'])
def get_request_stats():
    """Get request statistics"""
    try:
        # Basic statistics
        total_requests = StudentRequest.query.count()
        pending_requests = StudentRequest.query.filter(
            StudentRequest.status.in_(['submitted', 'in_progress'])
        ).count()
        completed_requests = StudentRequest.query.filter_by(status='completed').count()
        
        # Requests by type
        request_types = db.session.query(
            StudentRequest.request_type,
            db.func.count(StudentRequest.id).label('count')
        ).group_by(StudentRequest.request_type).all()
        
        data = {
            'total_requests': total_requests,
            'pending_requests': pending_requests,
            'completed_requests': completed_requests,
            'by_type': {rt[0]: rt[1] for rt in request_types}
        }
        
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        logger.error(f"Error getting request stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Error handlers for the blueprint
@api_enhanced.errorhandler(400)
def bad_request(error):
    return jsonify({'success': False, 'error': 'Bad request'}), 400

@api_enhanced.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Resource not found'}), 404

@api_enhanced.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500