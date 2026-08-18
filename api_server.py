"""
College Event Registration, Volunteer Allocation, and Participation Management System
REST API Server Module

This module implements the REST API endpoints for the event management system,
providing interfaces for event management, registration, volunteer allocation, and analytics.

Author: Manus AI
Date: August 31, 2024
"""

from flask import Flask, request, jsonify
from functools import wraps
import jwt
import json
from datetime import datetime, timedelta
from event_management_system import EventManagementSystem
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize system
system = EventManagementSystem()

# Authentication decorator
def token_required(f):
    """Decorator to check JWT token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            token = token.split(' ')[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['user_id']
        except Exception as e:
            return jsonify({'message': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated


# User Management Endpoints

@app.route('/api/users/register', methods=['POST'])
def register_user():
    """Register a new user."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'role', 'department', 'academic_year']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields'}), 400
        
        user = system.add_user(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            role=data['role'],
            department=data['department'],
            academic_year=data['academic_year']
        )
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 400


@app.route('/api/users/login', methods=['POST'])
def login_user():
    """User login endpoint."""
    try:
        data = request.get_json()
        
        if not data.get('email'):
            return jsonify({'message': 'Email is required'}), 400
        
        # In a real system, verify password here
        # For demo purposes, we'll generate a token
        token = jwt.encode({
            'user_id': data.get('user_id', 'demo-user'),
            'email': data['email'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'Login successful',
            'token': token
        }), 200
    
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 400


# Event Management Endpoints

@app.route('/api/events/create', methods=['POST'])
@token_required
def create_event(current_user):
    """Create a new event."""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'description', 'date', 'time', 'location', 
                          'capacity', 'category', 'volunteers_needed']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields'}), 400
        
        event = system.create_event(
            name=data['name'],
            description=data['description'],
            date=data['date'],
            time=data['time'],
            location=data['location'],
            capacity=int(data['capacity']),
            category=data['category'],
            volunteers_needed=int(data['volunteers_needed']),
            created_by=current_user
        )
        
        return jsonify({
            'message': 'Event created successfully',
            'event': event.to_dict()
        }), 201
    
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 400


@app.route('/api/events/<event_id>', methods=['GET'])
def get_event(event_id):
    """Get event details."""
    try:
        cursor = system.connection.cursor()
        cursor.execute('SELECT * FROM events WHERE event_id = ?', (event_id,))
        event = cursor.fetchone()
        
        if not event:
            return jsonify({'message': 'Event not found'}), 404
        
        return jsonify({
            'event_id': event[0],
            'name': event[1],
            'description': event[2],
            'date': event[3],
            'time': event[4],
            'location': event[5],
            'capacity': event[6],
            'category': event[7],
            'status': event[8]
        }), 200
    
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 400


@app.route('/api/events', methods=['GET'])
def list_events():
    """List all events."""
    try:
        cursor = system.connection.cursor()
        cursor.execute('SELECT * FROM events WHERE status != ?', ('cancelled',))
        events = cursor.fetchall()
        
        event_list = []
        for event in events:
            event_list.append({
                'event_id': event[0],
                'name': event[1],
                'date': event[3],
                'time': event[4],
                'location': event[5],
                'category': event[7],
                'status': event[8]
            })
        
        return jsonify({
            'total_events': len(event_list),
            'events': event_list
        }), 200
    
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 400


# Registration Endpoints

@app.route('/api/registrations/register', methods=['POST'])
@token_required
def register_for_event(current_user):
    """Register user for an event."""
    try:
        data = request.get_json()
        
        if not data.get('event_id'):
            return jsonify({'message': 'Event ID is required'}), 400
        
        success, message = system.register_user_for_event(current_user, data['event_id'])
        
        if success:
            return jsonify({'message': message}), 201
        else:
            return jsonify({'message': message}), 400
    
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 400


@app.route('/api/registrations/<event_id>', methods=['GET'])
def get_event_registrations(event_id):
    """Get registrations for an event."""
    try:
        cursor = system.connection.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM registrations 
            WHERE event_id = ? AND status = ?
        ''', (event_id, 'confirmed'))
        
        confirmed = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT COUNT(*) FROM registrations 
            WHERE event_id = ? AND status = ?
        ''', (event_id, 'waitlisted'))
        
        waitlisted = cursor.fetchone()[0]
        
        return jsonify({
            'event_id': event_id,
            'confirmed_registrations': confirmed,
            'waitlisted_registrations': waitlisted,
            'total_registrations': confirmed + waitlisted
        }), 200
    
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 400


# Volunteer Management Endpoints

@app.route('/api/volunteers/allocate', methods=['POST'])
@token_required
def allocate_volunteer(current_user):
    """Allocate a volunteer to an event."""
    try:
        data = request.get_json()
        
        required_fields = ['user_id', 'event_id', 'role', 'responsibilities']
        if not all(field in data for field in required_fields):
            return jsonify({'message': 'Missing required fields'}), 400
        
        success, message = system.allocate_volunteer(
            user_id=data['user_id'],
            event_id=data['event_id'],
            role=data['role'],
            responsibilities=data['responsibilities']
        )
        
        if success:
            return jsonify({'message': message}), 201
        else:
            return jsonify({'message': message}), 400
    
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 400


@app.route('/api/volunteers/<event_id>', methods=['GET'])
def get_event_volunteers(event_id):
    """Get volunteers for an event."""
    try:
        cursor = system.connection.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM volunteers 
            WHERE event_id = ?
        ''', (event_id,))
        
        volunteer_count = cursor.fetchone()[0]
        
        return jsonify({
            'event_id': event_id,
            'volunteer_count': volunteer_count
        }), 200
    
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 400


# Attendance Endpoints

@app.route('/api/attendance/checkin', methods=['POST'])
@token_required
def check_in_attendance(current_user):
    """Record attendance check-in."""
    try:
        data = request.get_json()
        
        if not data.get('event_id'):
            return jsonify({'message': 'Event ID is required'}), 400
        
        check_in_method = data.get('check_in_method', 'manual')
        
        success, message = system.record_attendance(
            user_id=current_user,
            event_id=data['event_id'],
            check_in_method=check_in_method
        )
        
        if success:
            return jsonify({'message': message}), 201
        else:
            return jsonify({'message': message}), 400
    
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 400


@app.route('/api/attendance/<event_id>', methods=['GET'])
def get_event_attendance(event_id):
    """Get attendance for an event."""
    try:
        cursor = system.connection.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM attendance 
            WHERE event_id = ?
        ''', (event_id,))
        
        attendance_count = cursor.fetchone()[0]
        
        return jsonify({
            'event_id': event_id,
            'attendance_count': attendance_count
        }), 200
    
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 400


# Analytics Endpoints

@app.route('/api/analytics/event/<event_id>', methods=['GET'])
def get_event_analytics(event_id):
    """Get analytics for an event."""
    try:
        analytics = system.get_event_analytics(event_id)
        return jsonify(analytics), 200
    
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 400


@app.route('/api/analytics/system', methods=['GET'])
def get_system_analytics():
    """Get overall system analytics."""
    try:
        statistics = system.get_system_statistics()
        return jsonify(statistics), 200
    
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 400


# Health Check Endpoint

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200


# Error Handlers

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'message': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'message': 'Internal server error'}), 500


if __name__ == '__main__':
    print("College Event Management System - REST API Server")
    print("=" * 60)
    print("Starting API server on http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=True, host='localhost', port=5000)
