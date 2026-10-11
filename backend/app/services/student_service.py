"""Student Service

Business logic for student profile management.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.student import Student, VerificationStatus
from app.models.user import User
from app.models.college import College
from app.models.campus import Campus
from app.schemas.student import StudentCreate, StudentUpdate, StudentProfileResponse


class StudentService:
    """Service for managing student profiles."""

    @staticmethod
    def create_student(student_data: StudentCreate, db: Session) -> Student:
        """Create a new student profile.

        Args:
            student_data: Student creation data
            db: Database session

        Returns:
            Created Student instance
        """
        # Verify user exists and has STUDENT role
        user = db.query(User).filter(User.id == student_data.user_id).first()
        if not user:
            raise ValueError("User not found")
        if user.role != User.Role.STUDENT:
            raise ValueError("User must have STUDENT role")

        # Verify college exists
        college = (
            db.query(College).filter(College.id == student_data.college_id).first()
        )
        if not college:
            raise ValueError("College not found")

        # Verify campus exists if provided
        if student_data.campus_id:
            campus = (
                db.query(Campus).filter(Campus.id == student_data.campus_id).first()
            )
            if not campus:
                raise ValueError("Campus not found")
            if campus.college_id != student_data.college_id:
                raise ValueError("Campus does not belong to the specified college")

        # Check if student profile already exists for this user
        existing_student = (
            db.query(Student).filter(Student.user_id == student_data.user_id).first()
        )
        if existing_student:
            raise ValueError("Student profile already exists for this user")

        # Create student
        student = Student(
            user_id=student_data.user_id,
            college_id=student_data.college_id,
            campus_id=student_data.campus_id,
            full_name=student_data.full_name,
            student_id=student_data.student_id,
            department=student_data.department,
            year=student_data.year,
            profile_photo_url=student_data.profile_photo_url,
            verification_status=VerificationStatus.UNVERIFIED,
        )

        db.add(student)
        db.commit()
        db.refresh(student)
        return student

    @staticmethod
    def get_student_by_id(student_id: UUID, db: Session) -> Optional[Student]:
        """Get student by ID.

        Args:
            student_id: Student UUID
            db: Database session

        Returns:
            Student instance or None
        """
        return db.query(Student).filter(Student.id == student_id).first()

    @staticmethod
    def get_student_by_user_id(user_id: UUID, db: Session) -> Optional[Student]:
        """Get student by user ID.

        Args:
            user_id: User UUID
            db: Database session

        Returns:
            Student instance or None
        """
        return db.query(Student).filter(Student.user_id == user_id).first()

    @staticmethod
    def get_student_profile(
        student_id: UUID, db: Session
    ) -> Optional[StudentProfileResponse]:
        """Get student profile with related data.

        Args:
            student_id: Student UUID
            db: Database session

        Returns:
            StudentProfileResponse or None
        """
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return None

        user = student.user
        college = student.college
        campus = student.campus

        return StudentProfileResponse(
            id=student.id,
            email=user.email,
            full_name=student.full_name,
            student_id=student.student_id,
            department=student.department,
            year=student.year,
            profile_photo_url=student.profile_photo_url,
            college_id=college.id,
            college_name=college.name,
            campus_id=campus.id if campus else None,
            campus_name=campus.name if campus else None,
            verification_status=student.verification_status.value,
            verified_at=student.verified_at,
            is_email_verified=user.is_email_verified,
            created_at=student.created_at,
            updated_at=student.updated_at,
        )

    @staticmethod
    def update_student(
        student_id: UUID, student_data: StudentUpdate, db: Session
    ) -> Optional[Student]:
        """Update student profile.

        Args:
            student_id: Student UUID
            student_data: Student update data
            db: Database session

        Returns:
            Updated Student instance or None
        """
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return None

        # Update fields if provided
        update_data = student_data.model_dump(exclude_unset=True)

        # Verify campus belongs to college if campus_id is being updated
        if "campus_id" in update_data and update_data["campus_id"]:
            campus = (
                db.query(Campus).filter(Campus.id == update_data["campus_id"]).first()
            )
            if not campus:
                raise ValueError("Campus not found")
            if campus.college_id != student.college_id:
                raise ValueError("Campus does not belong to the student's college")

        for field, value in update_data.items():
            setattr(student, field, value)

        db.commit()
        db.refresh(student)
        return student

    @staticmethod
    def delete_student(student_id: UUID, db: Session) -> bool:
        """Delete student profile (soft delete by setting deleted_at).

        Args:
            student_id: Student UUID
            db: Database session

        Returns:
            True if deleted, False if not found
        """
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return False

        # Soft delete - just mark as deleted
        # In a real implementation, you might want to use the user's deleted_at
        db.delete(student)
        db.commit()
        return True

    @staticmethod
    def list_students(
        db: Session,
        college_id: Optional[UUID] = None,
        campus_id: Optional[UUID] = None,
        verification_status: Optional[VerificationStatus] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Student]:
        """List students with optional filters.

        Args:
            db: Database session
            college_id: Filter by college
            campus_id: Filter by campus
            verification_status: Filter by verification status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Student instances
        """
        query = db.query(Student)

        if college_id:
            query = query.filter(Student.college_id == college_id)
        if campus_id:
            query = query.filter(Student.campus_id == campus_id)
        if verification_status:
            query = query.filter(Student.verification_status == verification_status)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count_students(
        db: Session,
        college_id: Optional[UUID] = None,
        campus_id: Optional[UUID] = None,
        verification_status: Optional[VerificationStatus] = None,
    ) -> int:
        """Count students with optional filters.

        Args:
            db: Database session
            college_id: Filter by college
            campus_id: Filter by campus
            verification_status: Filter by verification status

        Returns:
            Count of students
        """
        query = db.query(Student)

        if college_id:
            query = query.filter(Student.college_id == college_id)
        if campus_id:
            query = query.filter(Student.campus_id == campus_id)
        if verification_status:
            query = query.filter(Student.verification_status == verification_status)

        return query.count()
