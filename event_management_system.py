"""
College Event Registration, Volunteer Allocation, and Participation Management System
Core Module - Main System Implementation

This module implements the complete event management system with event registration,
volunteer allocation, attendance tracking, and analytics functionality.

Author: Manus AI
Date: August 31, 2024
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
import hashlib
import uuid


@dataclass
class User:
    """Represents a system user (student, volunteer, or administrator)."""
    user_id: str
    name: str
    email: str
    phone: str
    role: str  # 'student', 'volunteer', 'administrator'
    department: str
    academic_year: str
    created_at: str
    
    def to_dict(self) -> Dict:
        """Convert user to dictionary."""
        return asdict(self)


@dataclass
class Event:
    """Represents a college event."""
    event_id: str
    name: str
    description: str
    date: str
    time: str
    location: str
    capacity: int
    category: str  # 'academic', 'cultural', 'sports', 'social', 'technical'
    status: str  # 'planned', 'ongoing', 'completed', 'cancelled'
    volunteers_needed: int
    created_by: str
    created_at: str
    
    def to_dict(self) -> Dict:
        """Convert event to dictionary."""
        return asdict(self)


@dataclass
class Registration:
    """Represents an event registration."""
    registration_id: str
    user_id: str
    event_id: str
    status: str  # 'confirmed', 'cancelled', 'waitlisted'
    registration_timestamp: str
    cancellation_timestamp: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert registration to dictionary."""
        return asdict(self)


@dataclass
class Volunteer:
    """Represents a volunteer assignment."""
    volunteer_id: str
    user_id: str
    event_id: str
    role: str
    responsibilities: str
    availability_status: str  # 'available', 'assigned', 'completed'
    assignment_timestamp: str
    
    def to_dict(self) -> Dict:
        """Convert volunteer to dictionary."""
        return asdict(self)


@dataclass
class Attendance:
    """Represents attendance record."""
    attendance_id: str
    user_id: str
    event_id: str
    check_in_timestamp: str
    check_in_method: str  # 'qr_code', 'manual', 'biometric'
    verification_status: str  # 'verified', 'pending'
    
    def to_dict(self) -> Dict:
        """Convert attendance to dictionary."""
        return asdict(self)


class EventManagementSystem:
    """Main event management system class."""
    
    def __init__(self, db_path: str = ':memory:'):
        """Initialize the system with database connection."""
        self.db_path = db_path
        self.connection = None
        self.initialize_database()
    
    def initialize_database(self):
        """Create database tables."""
        self.connection = sqlite3.connect(self.db_path)
        cursor = self.connection.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                role TEXT NOT NULL,
                department TEXT,
                academic_year TEXT,
                created_at TEXT
            )
        ''')
        
        # Events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                location TEXT NOT NULL,
                capacity INTEGER NOT NULL,
                category TEXT NOT NULL,
                status TEXT NOT NULL,
                volunteers_needed INTEGER,
                created_by TEXT NOT NULL,
                created_at TEXT,
                FOREIGN KEY (created_by) REFERENCES users(user_id)
            )
        ''')
        
        # Registrations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registrations (
                registration_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                event_id TEXT NOT NULL,
                status TEXT NOT NULL,
                registration_timestamp TEXT,
                cancellation_timestamp TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (event_id) REFERENCES events(event_id),
                UNIQUE(user_id, event_id)
            )
        ''')
        
        # Volunteers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS volunteers (
                volunteer_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                event_id TEXT NOT NULL,
                role TEXT NOT NULL,
                responsibilities TEXT,
                availability_status TEXT NOT NULL,
                assignment_timestamp TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (event_id) REFERENCES events(event_id)
            )
        ''')
        
        # Attendance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                event_id TEXT NOT NULL,
                check_in_timestamp TEXT,
                check_in_method TEXT,
                verification_status TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (event_id) REFERENCES events(event_id)
            )
        ''')
        
        # Analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                analytics_id TEXT PRIMARY KEY,
                event_id TEXT NOT NULL,
                registration_count INTEGER,
                volunteer_count INTEGER,
                attendance_count INTEGER,
                engagement_score REAL,
                update_timestamp TEXT,
                FOREIGN KEY (event_id) REFERENCES events(event_id)
            )
        ''')
        
        self.connection.commit()
    
    def add_user(self, name: str, email: str, phone: str, role: str, 
                 department: str, academic_year: str) -> User:
        """Add a new user to the system."""
        user_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        
        user = User(user_id, name, email, phone, role, department, academic_year, created_at)
        
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO users (user_id, name, email, phone, role, department, academic_year, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, name, email, phone, role, department, academic_year, created_at))
        self.connection.commit()
        
        return user
    
    def create_event(self, name: str, description: str, date: str, time: str,
                    location: str, capacity: int, category: str, 
                    volunteers_needed: int, created_by: str) -> Event:
        """Create a new event."""
        event_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        status = 'planned'
        
        event = Event(event_id, name, description, date, time, location, 
                     capacity, category, status, volunteers_needed, created_by, created_at)
        
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO events (event_id, name, description, date, time, location, capacity, 
                              category, status, volunteers_needed, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (event_id, name, description, date, time, location, capacity, 
              category, status, volunteers_needed, created_by, created_at))
        self.connection.commit()
        
        return event
    
    def register_user_for_event(self, user_id: str, event_id: str) -> Tuple[bool, str]:
        """Register a user for an event."""
        cursor = self.connection.cursor()
        
        # Check event capacity
        cursor.execute('SELECT capacity FROM events WHERE event_id = ?', (event_id,))
        event = cursor.fetchone()
        if not event:
            return False, "Event not found"
        
        capacity = event[0]
        
        # Count existing registrations
        cursor.execute('SELECT COUNT(*) FROM registrations WHERE event_id = ? AND status = ?',
                      (event_id, 'confirmed'))
        count = cursor.fetchone()[0]
        
        if count >= capacity:
            status = 'waitlisted'
        else:
            status = 'confirmed'
        
        registration_id = str(uuid.uuid4())
        registration_timestamp = datetime.now().isoformat()
        
        try:
            cursor.execute('''
                INSERT INTO registrations (registration_id, user_id, event_id, status, registration_timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (registration_id, user_id, event_id, status, registration_timestamp))
            self.connection.commit()
            return True, f"Registration successful. Status: {status}"
        except sqlite3.IntegrityError:
            return False, "User already registered for this event"
    
    def allocate_volunteer(self, user_id: str, event_id: str, role: str, 
                          responsibilities: str) -> Tuple[bool, str]:
        """Allocate a volunteer to an event."""
        volunteer_id = str(uuid.uuid4())
        assignment_timestamp = datetime.now().isoformat()
        availability_status = 'assigned'
        
        cursor = self.connection.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO volunteers (volunteer_id, user_id, event_id, role, responsibilities, 
                                       availability_status, assignment_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (volunteer_id, user_id, event_id, role, responsibilities, 
                  availability_status, assignment_timestamp))
            self.connection.commit()
            return True, f"Volunteer allocated successfully with ID: {volunteer_id}"
        except Exception as e:
            return False, f"Error allocating volunteer: {str(e)}"
    
    def record_attendance(self, user_id: str, event_id: str, 
                         check_in_method: str = 'manual') -> Tuple[bool, str]:
        """Record attendance for a participant."""
        attendance_id = str(uuid.uuid4())
        check_in_timestamp = datetime.now().isoformat()
        verification_status = 'verified'
        
        cursor = self.connection.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO attendance (attendance_id, user_id, event_id, check_in_timestamp, 
                                       check_in_method, verification_status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (attendance_id, user_id, event_id, check_in_timestamp, 
                  check_in_method, verification_status))
            self.connection.commit()
            return True, f"Attendance recorded successfully"
        except Exception as e:
            return False, f"Error recording attendance: {str(e)}"
    
    def get_event_analytics(self, event_id: str) -> Dict:
        """Get analytics for an event."""
        cursor = self.connection.cursor()
        
        # Count registrations
        cursor.execute('SELECT COUNT(*) FROM registrations WHERE event_id = ? AND status = ?',
                      (event_id, 'confirmed'))
        registration_count = cursor.fetchone()[0]
        
        # Count volunteers
        cursor.execute('SELECT COUNT(*) FROM volunteers WHERE event_id = ?', (event_id,))
        volunteer_count = cursor.fetchone()[0]
        
        # Count attendance
        cursor.execute('SELECT COUNT(*) FROM attendance WHERE event_id = ?', (event_id,))
        attendance_count = cursor.fetchone()[0]
        
        # Calculate engagement score (0-100)
        if registration_count > 0:
            engagement_score = (attendance_count / registration_count) * 100
        else:
            engagement_score = 0
        
        analytics = {
            'event_id': event_id,
            'registration_count': registration_count,
            'volunteer_count': volunteer_count,
            'attendance_count': attendance_count,
            'engagement_score': round(engagement_score, 2),
            'update_timestamp': datetime.now().isoformat()
        }
        
        return analytics
    
    def get_system_statistics(self) -> Dict:
        """Get overall system statistics."""
        cursor = self.connection.cursor()
        
        # Count users by role
        cursor.execute('SELECT role, COUNT(*) FROM users GROUP BY role')
        user_stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Count events by status
        cursor.execute('SELECT status, COUNT(*) FROM events GROUP BY status')
        event_stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Count registrations
        cursor.execute('SELECT COUNT(*) FROM registrations')
        total_registrations = cursor.fetchone()[0]
        
        # Count volunteers
        cursor.execute('SELECT COUNT(*) FROM volunteers')
        total_volunteers = cursor.fetchone()[0]
        
        # Count attendance
        cursor.execute('SELECT COUNT(*) FROM attendance')
        total_attendance = cursor.fetchone()[0]
        
        statistics = {
            'user_statistics': user_stats,
            'event_statistics': event_stats,
            'total_registrations': total_registrations,
            'total_volunteers': total_volunteers,
            'total_attendance': total_attendance,
            'timestamp': datetime.now().isoformat()
        }
        
        return statistics
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()


# Test the system
if __name__ == '__main__':
    print("College Event Management System - Core Module Test")
    print("=" * 60)
    
    # Initialize system
    system = EventManagementSystem()
    
    # Add users
    admin = system.add_user('Admin User', 'admin@college.edu', '9876543210', 
                           'administrator', 'Administration', 'N/A')
    print(f"✓ Added administrator: {admin.name}")
    
    student1 = system.add_user('John Doe', 'john@college.edu', '9123456789', 
                              'student', 'Computer Science', 'First Year')
    print(f"✓ Added student: {student1.name}")
    
    student2 = system.add_user('Jane Smith', 'jane@college.edu', '9987654321', 
                              'student', 'Electronics', 'Second Year')
    print(f"✓ Added student: {student2.name}")
    
    # Create events
    event1 = system.create_event(
        name='Tech Summit 2024',
        description='Annual technology conference for students',
        date='2024-09-15',
        time='10:00 AM',
        location='Main Auditorium',
        capacity=100,
        category='technical',
        volunteers_needed=5,
        created_by=admin.user_id
    )
    print(f"✓ Created event: {event1.name}")
    
    event2 = system.create_event(
        name='Sports Day',
        description='Annual inter-college sports competition',
        date='2024-09-20',
        time='08:00 AM',
        location='Sports Ground',
        capacity=50,
        category='sports',
        volunteers_needed=10,
        created_by=admin.user_id
    )
    print(f"✓ Created event: {event2.name}")
    
    # Register users for events
    success, msg = system.register_user_for_event(student1.user_id, event1.event_id)
    print(f"✓ {msg}")
    
    success, msg = system.register_user_for_event(student2.user_id, event1.event_id)
    print(f"✓ {msg}")
    
    # Allocate volunteers
    success, msg = system.allocate_volunteer(student1.user_id, event1.event_id, 
                                            'Coordinator', 'Event coordination and setup')
    print(f"✓ {msg}")
    
    success, msg = system.allocate_volunteer(student2.user_id, event2.event_id, 
                                            'Marshal', 'Participant management')
    print(f"✓ {msg}")
    
    # Record attendance
    success, msg = system.record_attendance(student1.user_id, event1.event_id, 'qr_code')
    print(f"✓ {msg}")
    
    success, msg = system.record_attendance(student2.user_id, event1.event_id, 'manual')
    print(f"✓ {msg}")
    
    # Get analytics
    analytics = system.get_event_analytics(event1.event_id)
    print(f"✓ Event analytics: {analytics['registration_count']} registrations, "
          f"{analytics['volunteer_count']} volunteers, "
          f"{analytics['attendance_count']} attendees")
    
    # Get system statistics
    stats = system.get_system_statistics()
    print(f"✓ System statistics: {stats['total_registrations']} registrations, "
          f"{stats['total_volunteers']} volunteers, "
          f"{stats['total_attendance']} attendance records")
    
    # Close system
    system.close()
    
    print("✓ System test completed successfully")
    print("=" * 60)
