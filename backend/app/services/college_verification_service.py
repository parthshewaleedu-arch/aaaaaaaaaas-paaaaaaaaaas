"""College verification service"""

import secrets
from datetime import datetime, timedelta

from app.core.config import settings
from app.models.student import Student, VerificationStatus
from sqlalchemy.orm import Session


class CollegeVerificationService:
    """Service for handling college email verification."""

    @staticmethod
    def generate_verification_token() -> str:
        """Generate a secure random token for email verification."""
        return secrets.token_urlsafe(32)

    @staticmethod
    def send_verification_email(email: str, token: str) -> bool:
        """
        Send verification email to the student's college email.
        In a real application, this would integrate with an email service.
        For now, we'll just print to console (or log) and return True.
        """
        # In development, we can print the token to console for testing
        if settings.DEBUG:
            print(f"College verification email sent to {email}")
            print(f"Verification token: {token}")
            # In a real app, you would use an email service like SMTP, SendGrid, etc.
        # For now, we assume the email is sent successfully
        return True

    @staticmethod
    def request_verification(student_id: str, db: Session) -> bool:
        """
        Request college email verification for a student.
        Generates a token, stores it, and sends the verification email.
        """
        # Get the student
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return False

        # Generate token
        token = CollegeVerificationService.generate_verification_token()
        expires_at = datetime.utcnow() + timedelta(hours=24)  # Token valid for 24 hours

        # Store token and expiration
        student.email_verification_token = token
        student.email_verification_expires_at = expires_at
        db.commit()

        # Send email
        # We need the student's college email. This would be available via the user relationship.
        # For now, we'll assume we have a way to get the college email.
        # In a real app, we would get the email from the associated User model.
        # Since we don't have the user's email in the Student model directly, we need to get it via the user.
        # However, for simplicity in this service, we'll assume the email is passed or we have a method to get it.
        # Let's adjust: we'll get the email from the user relationship.
        if student.user and student.user.email:
            college_email = student.user.email
            CollegeVerificationService.send_verification_email(college_email, token)
            return True
        return False

    @staticmethod
    def verify_token(student_id: str, token: str, db: Session) -> bool:
        """
        Verify the token for college email verification.
        If valid, update the student's verification status and clear the token.
        """
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return False

        # Check if token matches and is not expired
        if (
            student.email_verification_token == token
            and student.email_verification_expires_at
            and student.email_verification_expires_at > datetime.utcnow()
        ):
            # Token is valid
            student.verification_status = VerificationStatus.VERIFIED
            student.verified_at = datetime.utcnow()
            # Clear the token fields
            student.email_verification_token = None
            student.email_verification_expires_at = None
            db.commit()
            return True
        else:
            # Token invalid or expired
            return False

    @staticmethod
    def resend_verification(student_id: str, db: Session) -> bool:
        """
        Resend the verification email.
        Generates a new token and sends the email.
        """
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            return False

        # Generate new token
        token = CollegeVerificationService.generate_verification_token()
        expires_at = datetime.utcnow() + timedelta(hours=24)

        # Update token and expiration
        student.email_verification_token = token
        student.email_verification_expires_at = expires_at
        db.commit()

        # Send email
        if student.user and student.user.email:
            college_email = student.user.email
            CollegeVerificationService.send_verification_email(college_email, token)
            return True
        return False
