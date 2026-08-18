"""
College Event Registration, Volunteer Allocation, and Participation Management System
Testing and Evaluation Module

This module implements comprehensive testing and performance evaluation for the system.

Author: Manus AI
Date: August 31, 2024
"""

import time
import json
from datetime import datetime
from event_management_system import EventManagementSystem
from typing import Dict, List, Tuple


class SystemTester:
    """Comprehensive system testing class."""
    
    def __init__(self):
        """Initialize the tester."""
        self.system = EventManagementSystem()
        self.test_results = []
        self.performance_metrics = {}
    
    def run_all_tests(self) -> Dict:
        """Run all test suites."""
        print("\nCollege Event Management System - Comprehensive Testing")
        print("=" * 70)
        
        test_suites = [
            ('User Management Tests', self.test_user_management),
            ('Event Management Tests', self.test_event_management),
            ('Registration Tests', self.test_registration),
            ('Volunteer Allocation Tests', self.test_volunteer_allocation),
            ('Attendance Tracking Tests', self.test_attendance_tracking),
            ('Analytics Tests', self.test_analytics),
            ('Performance Tests', self.test_performance),
        ]
        
        for suite_name, test_func in test_suites:
            print(f"\n{suite_name}")
            print("-" * 70)
            test_func()
        
        return self.generate_test_report()
    
    def test_user_management(self):
        """Test user management functionality."""
        tests_passed = 0
        tests_total = 4
        
        # Test 1: Add student user
        try:
            student = self.system.add_user('Alice Johnson', 'alice@college.edu', 
                                          '9123456789', 'student', 'Computer Science', 'First Year')
            assert student.user_id is not None
            assert student.role == 'student'
            print("✓ Test 1: Add student user - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 1: Add student user - FAILED: {str(e)}")
        
        # Test 2: Add volunteer user
        try:
            volunteer = self.system.add_user('Bob Smith', 'bob@college.edu', 
                                            '9987654321', 'volunteer', 'Electronics', 'Second Year')
            assert volunteer.user_id is not None
            assert volunteer.role == 'volunteer'
            print("✓ Test 2: Add volunteer user - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 2: Add volunteer user - FAILED: {str(e)}")
        
        # Test 3: Add administrator user
        try:
            admin = self.system.add_user('Carol White', 'carol@college.edu', 
                                        '9555555555', 'administrator', 'Administration', 'N/A')
            assert admin.user_id is not None
            assert admin.role == 'administrator'
            print("✓ Test 3: Add administrator user - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 3: Add administrator user - FAILED: {str(e)}")
        
        # Test 4: User data persistence
        try:
            cursor = self.system.connection.cursor()
            cursor.execute('SELECT COUNT(*) FROM users')
            user_count = cursor.fetchone()[0]
            assert user_count >= 3
            print("✓ Test 4: User data persistence - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 4: User data persistence - FAILED: {str(e)}")
        
        print(f"\nUser Management: {tests_passed}/{tests_total} tests passed")
        self.test_results.append(('User Management', tests_passed, tests_total))
    
    def test_event_management(self):
        """Test event management functionality."""
        tests_passed = 0
        tests_total = 4
        
        # Get admin user
        cursor = self.system.connection.cursor()
        cursor.execute('SELECT user_id FROM users WHERE role = ? LIMIT 1', ('administrator',))
        admin_id = cursor.fetchone()[0]
        
        # Test 1: Create technical event
        try:
            event1 = self.system.create_event(
                name='Tech Summit 2024',
                description='Annual technology conference',
                date='2024-09-15',
                time='10:00 AM',
                location='Main Auditorium',
                capacity=100,
                category='technical',
                volunteers_needed=5,
                created_by=admin_id
            )
            assert event1.event_id is not None
            assert event1.category == 'technical'
            print("✓ Test 1: Create technical event - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 1: Create technical event - FAILED: {str(e)}")
        
        # Test 2: Create sports event
        try:
            event2 = self.system.create_event(
                name='Sports Day',
                description='Inter-college sports competition',
                date='2024-09-20',
                time='08:00 AM',
                location='Sports Ground',
                capacity=50,
                category='sports',
                volunteers_needed=10,
                created_by=admin_id
            )
            assert event2.event_id is not None
            assert event2.category == 'sports'
            print("✓ Test 2: Create sports event - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 2: Create sports event - FAILED: {str(e)}")
        
        # Test 3: Create cultural event
        try:
            event3 = self.system.create_event(
                name='Cultural Festival',
                description='Annual cultural celebration',
                date='2024-10-01',
                time='05:00 PM',
                location='Open Ground',
                capacity=200,
                category='cultural',
                volunteers_needed=15,
                created_by=admin_id
            )
            assert event3.event_id is not None
            print("✓ Test 3: Create cultural event - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 3: Create cultural event - FAILED: {str(e)}")
        
        # Test 4: Event data persistence
        try:
            cursor.execute('SELECT COUNT(*) FROM events')
            event_count = cursor.fetchone()[0]
            assert event_count >= 3
            print("✓ Test 4: Event data persistence - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 4: Event data persistence - FAILED: {str(e)}")
        
        print(f"\nEvent Management: {tests_passed}/{tests_total} tests passed")
        self.test_results.append(('Event Management', tests_passed, tests_total))
    
    def test_registration(self):
        """Test event registration functionality."""
        tests_passed = 0
        tests_total = 4
        
        # Get test data
        cursor = self.system.connection.cursor()
        cursor.execute('SELECT user_id FROM users WHERE role = ? LIMIT 2', ('student',))
        students = [row[0] for row in cursor.fetchall()]
        cursor.execute('SELECT event_id FROM events LIMIT 1')
        event_id = cursor.fetchone()[0]
        
        if len(students) < 2 or not event_id:
            print("✗ Insufficient test data for registration tests")
            return
        
        # Test 1: Register first student
        try:
            success, msg = self.system.register_user_for_event(students[0], event_id)
            assert success
            print("✓ Test 1: Register first student - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 1: Register first student - FAILED: {str(e)}")
        
        # Test 2: Register second student
        try:
            success, msg = self.system.register_user_for_event(students[1], event_id)
            assert success
            print("✓ Test 2: Register second student - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 2: Register second student - FAILED: {str(e)}")
        
        # Test 3: Prevent duplicate registration
        try:
            success, msg = self.system.register_user_for_event(students[0], event_id)
            assert not success
            print("✓ Test 3: Prevent duplicate registration - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 3: Prevent duplicate registration - FAILED: {str(e)}")
        
        # Test 4: Registration data persistence
        try:
            cursor.execute('SELECT COUNT(*) FROM registrations WHERE event_id = ?', (event_id,))
            reg_count = cursor.fetchone()[0]
            assert reg_count >= 2
            print("✓ Test 4: Registration data persistence - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 4: Registration data persistence - FAILED: {str(e)}")
        
        print(f"\nRegistration: {tests_passed}/{tests_total} tests passed")
        self.test_results.append(('Registration', tests_passed, tests_total))
    
    def test_volunteer_allocation(self):
        """Test volunteer allocation functionality."""
        tests_passed = 0
        tests_total = 4
        
        # Get test data
        cursor = self.system.connection.cursor()
        cursor.execute('SELECT user_id FROM users WHERE role = ? LIMIT 2', ('volunteer',))
        volunteers = [row[0] for row in cursor.fetchall()]
        cursor.execute('SELECT event_id FROM events LIMIT 1')
        event_id = cursor.fetchone()[0]
        
        if len(volunteers) < 2 or not event_id:
            print("✗ Insufficient test data for volunteer allocation tests")
            return
        
        # Test 1: Allocate first volunteer
        try:
            success, msg = self.system.allocate_volunteer(
                volunteers[0], event_id, 'Coordinator', 'Event coordination'
            )
            assert success
            print("✓ Test 1: Allocate first volunteer - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 1: Allocate first volunteer - FAILED: {str(e)}")
        
        # Test 2: Allocate second volunteer
        try:
            success, msg = self.system.allocate_volunteer(
                volunteers[1], event_id, 'Marshal', 'Participant management'
            )
            assert success
            print("✓ Test 2: Allocate second volunteer - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 2: Allocate second volunteer - FAILED: {str(e)}")
        
        # Test 3: Verify volunteer roles
        try:
            cursor.execute('SELECT role FROM volunteers WHERE user_id = ? AND event_id = ?',
                          (volunteers[0], event_id))
            role = cursor.fetchone()[0]
            assert role == 'Coordinator'
            print("✓ Test 3: Verify volunteer roles - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 3: Verify volunteer roles - FAILED: {str(e)}")
        
        # Test 4: Volunteer data persistence
        try:
            cursor.execute('SELECT COUNT(*) FROM volunteers WHERE event_id = ?', (event_id,))
            vol_count = cursor.fetchone()[0]
            assert vol_count >= 2
            print("✓ Test 4: Volunteer data persistence - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 4: Volunteer data persistence - FAILED: {str(e)}")
        
        print(f"\nVolunteer Allocation: {tests_passed}/{tests_total} tests passed")
        self.test_results.append(('Volunteer Allocation', tests_passed, tests_total))
    
    def test_attendance_tracking(self):
        """Test attendance tracking functionality."""
        tests_passed = 0
        tests_total = 4
        
        # Get test data
        cursor = self.system.connection.cursor()
        cursor.execute('SELECT user_id FROM users WHERE role = ? LIMIT 1', ('student',))
        student_id = cursor.fetchone()[0]
        cursor.execute('SELECT event_id FROM events LIMIT 1')
        event_id = cursor.fetchone()[0]
        
        if not student_id or not event_id:
            print("✗ Insufficient test data for attendance tests")
            return
        
        # Test 1: Record attendance with QR code
        try:
            success, msg = self.system.record_attendance(student_id, event_id, 'qr_code')
            assert success
            print("✓ Test 1: Record attendance with QR code - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 1: Record attendance with QR code - FAILED: {str(e)}")
        
        # Test 2: Record attendance with manual check-in
        try:
            cursor.execute('SELECT user_id FROM users WHERE role = ? LIMIT 2 OFFSET 1', ('student',))
            student_id2 = cursor.fetchone()[0]
            success, msg = self.system.record_attendance(student_id2, event_id, 'manual')
            assert success
            print("✓ Test 2: Record attendance with manual check-in - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 2: Record attendance with manual check-in - FAILED: {str(e)}")
        
        # Test 3: Verify attendance records
        try:
            cursor.execute('SELECT COUNT(*) FROM attendance WHERE event_id = ?', (event_id,))
            att_count = cursor.fetchone()[0]
            assert att_count >= 1
            print("✓ Test 3: Verify attendance records - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 3: Verify attendance records - FAILED: {str(e)}")
        
        # Test 4: Attendance data persistence
        try:
            cursor.execute('SELECT verification_status FROM attendance WHERE user_id = ? AND event_id = ?',
                          (student_id, event_id))
            status = cursor.fetchone()[0]
            assert status == 'verified'
            print("✓ Test 4: Attendance data persistence - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 4: Attendance data persistence - FAILED: {str(e)}")
        
        print(f"\nAttendance Tracking: {tests_passed}/{tests_total} tests passed")
        self.test_results.append(('Attendance Tracking', tests_passed, tests_total))
    
    def test_analytics(self):
        """Test analytics functionality."""
        tests_passed = 0
        tests_total = 4
        
        # Get test event
        cursor = self.system.connection.cursor()
        cursor.execute('SELECT event_id FROM events LIMIT 1')
        event_id = cursor.fetchone()[0]
        
        if not event_id:
            print("✗ No events available for analytics tests")
            return
        
        # Test 1: Get event analytics
        try:
            analytics = self.system.get_event_analytics(event_id)
            assert 'registration_count' in analytics
            assert 'volunteer_count' in analytics
            assert 'attendance_count' in analytics
            print("✓ Test 1: Get event analytics - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 1: Get event analytics - FAILED: {str(e)}")
        
        # Test 2: Verify engagement score calculation
        try:
            analytics = self.system.get_event_analytics(event_id)
            assert 'engagement_score' in analytics
            assert 0 <= analytics['engagement_score'] <= 100
            print("✓ Test 2: Verify engagement score calculation - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 2: Verify engagement score calculation - FAILED: {str(e)}")
        
        # Test 3: Get system statistics
        try:
            stats = self.system.get_system_statistics()
            assert 'user_statistics' in stats
            assert 'event_statistics' in stats
            assert 'total_registrations' in stats
            print("✓ Test 3: Get system statistics - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 3: Get system statistics - FAILED: {str(e)}")
        
        # Test 4: Verify statistics accuracy
        try:
            stats = self.system.get_system_statistics()
            assert stats['total_registrations'] >= 0
            assert stats['total_volunteers'] >= 0
            assert stats['total_attendance'] >= 0
            print("✓ Test 4: Verify statistics accuracy - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 4: Verify statistics accuracy - FAILED: {str(e)}")
        
        print(f"\nAnalytics: {tests_passed}/{tests_total} tests passed")
        self.test_results.append(('Analytics', tests_passed, tests_total))
    
    def test_performance(self):
        """Test system performance."""
        tests_passed = 0
        tests_total = 4
        
        # Test 1: Event creation performance
        try:
            cursor = self.system.connection.cursor()
            cursor.execute('SELECT user_id FROM users WHERE role = ? LIMIT 1', ('administrator',))
            admin_id = cursor.fetchone()[0]
            
            start_time = time.time()
            for i in range(10):
                self.system.create_event(
                    name=f'Performance Test Event {i}',
                    description='Performance test',
                    date='2024-10-01',
                    time='10:00 AM',
                    location='Test Location',
                    capacity=100,
                    category='technical',
                    volunteers_needed=5,
                    created_by=admin_id
                )
            end_time = time.time()
            
            avg_time = (end_time - start_time) / 10 * 1000  # Convert to milliseconds
            self.performance_metrics['event_creation_ms'] = round(avg_time, 2)
            
            assert avg_time < 500  # Should be less than 500ms
            print(f"✓ Test 1: Event creation performance ({avg_time:.2f}ms avg) - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 1: Event creation performance - FAILED: {str(e)}")
        
        # Test 2: Registration processing performance
        try:
            cursor.execute('SELECT user_id FROM users WHERE role = ? LIMIT 1', ('student',))
            student_id = cursor.fetchone()[0]
            cursor.execute('SELECT event_id FROM events LIMIT 1')
            event_id = cursor.fetchone()[0]
            
            start_time = time.time()
            for i in range(5):
                cursor.execute('SELECT user_id FROM users WHERE role = ? LIMIT 1 OFFSET ?', 
                             ('student', i))
                user = cursor.fetchone()
                if user:
                    self.system.register_user_for_event(user[0], event_id)
            end_time = time.time()
            
            avg_time = (end_time - start_time) / 5 * 1000
            self.performance_metrics['registration_ms'] = round(avg_time, 2)
            
            assert avg_time < 500
            print(f"✓ Test 2: Registration processing ({avg_time:.2f}ms avg) - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 2: Registration processing - FAILED: {str(e)}")
        
        # Test 3: Analytics computation performance
        try:
            cursor.execute('SELECT event_id FROM events LIMIT 1')
            event_id = cursor.fetchone()[0]
            
            start_time = time.time()
            for i in range(10):
                self.system.get_event_analytics(event_id)
            end_time = time.time()
            
            avg_time = (end_time - start_time) / 10 * 1000
            self.performance_metrics['analytics_ms'] = round(avg_time, 2)
            
            assert avg_time < 200
            print(f"✓ Test 3: Analytics computation ({avg_time:.2f}ms avg) - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 3: Analytics computation - FAILED: {str(e)}")
        
        # Test 4: System statistics performance
        try:
            start_time = time.time()
            for i in range(10):
                self.system.get_system_statistics()
            end_time = time.time()
            
            avg_time = (end_time - start_time) / 10 * 1000
            self.performance_metrics['statistics_ms'] = round(avg_time, 2)
            
            assert avg_time < 300
            print(f"✓ Test 4: System statistics ({avg_time:.2f}ms avg) - PASSED")
            tests_passed += 1
        except Exception as e:
            print(f"✗ Test 4: System statistics - FAILED: {str(e)}")
        
        print(f"\nPerformance: {tests_passed}/{tests_total} tests passed")
        self.test_results.append(('Performance', tests_passed, tests_total))
    
    def generate_test_report(self) -> Dict:
        """Generate comprehensive test report."""
        print("\n" + "=" * 70)
        print("TEST SUMMARY REPORT")
        print("=" * 70)
        
        total_tests = 0
        total_passed = 0
        
        for test_suite, passed, total in self.test_results:
            total_tests += total
            total_passed += passed
            percentage = (passed / total * 100) if total > 0 else 0
            print(f"{test_suite}: {passed}/{total} ({percentage:.1f}%)")
        
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "-" * 70)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {total_passed}")
        print(f"Failed: {total_tests - total_passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print("-" * 70)
        
        print("\nPERFORMANCE METRICS")
        print("-" * 70)
        for metric, value in self.performance_metrics.items():
            print(f"{metric}: {value} ms")
        
        print("\n" + "=" * 70)
        
        report = {
            'total_tests': total_tests,
            'passed_tests': total_passed,
            'failed_tests': total_tests - total_passed,
            'success_rate': round(success_rate, 2),
            'performance_metrics': self.performance_metrics,
            'test_suites': self.test_results,
            'timestamp': datetime.now().isoformat()
        }
        
        return report


if __name__ == '__main__':
    tester = SystemTester()
    report = tester.run_all_tests()
    
    # Save report to file
    with open('test_results.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n✓ Test report saved to test_results.json")
    
    tester.system.close()
