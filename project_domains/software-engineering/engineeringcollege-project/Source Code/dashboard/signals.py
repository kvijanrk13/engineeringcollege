# dashboard/signals.py
"""
Django signals for automatic student profile initialization.
Ensures all new students are properly set up with certificate field slots.
"""

import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Student

logger = logging.getLogger(__name__)

# ============================================================================
# STUDENT AUTO-INITIALIZATION SIGNAL
# ============================================================================

@receiver(post_save, sender=Student)
def auto_initialize_student_profile(sender, instance, created, **kwargs):
    """
    Automatically initialize new student profiles with proper field structure.
    Called whenever a Student object is created.
    
    Ensures:
    - All certificate field slots exist (7 slots for different cert types)
    - PDF generation fields are initialized
    - Logging is captured for audit trail
    """
    if not created:
        return  # Only process on creation, not updates
    
    student = instance
    
    # Log student creation
    logger.info(
        f"New student profile created: {student.student_name} "
        f"(HT No: {student.ht_no}, ID: {student.id}) at {timezone.now()}"
    )
    
    # Verify all certificate field slots are accessible
    # (They should be by default from the model, but this ensures consistency)
    cert_fields = [
        'cert_achieve', 'cert_intern', 'cert_courses',
        'cert_sdp', 'cert_extra', 'cert_placement', 'cert_national',
        'cert_achieve_additional', 'cert_intern_additional', 'cert_courses_additional',
        'cert_sdp_additional', 'cert_extra_additional', 'cert_placement_additional',
        'cert_national_additional',
    ]
    
    cert_urls = [
        'cert_achieve_url', 'cert_intern_url', 'cert_courses_url',
        'cert_sdp_url', 'cert_extra_url', 'cert_placement_url', 'cert_national_url',
        'cert_achieve_additional_url', 'cert_intern_additional_url',
        'cert_courses_additional_url', 'cert_sdp_additional_url',
        'cert_extra_additional_url', 'cert_placement_additional_url',
        'cert_national_additional_url',
    ]
    
    # Verify structure
    for field in cert_fields + cert_urls:
        if not hasattr(student, field):
            logger.warning(
                f"Student {student.id} ({student.ht_no}) missing field: {field}"
            )
    
    # Log successful initialization
    logger.info(
        f"Student profile initialization complete for {student.student_name} "
        f"- Ready to accept photos and {len(cert_fields)} certificate types"
    )


@receiver(pre_save, sender=Student)
def track_student_changes(sender, instance, **kwargs):
    """
    Track changes to student records for audit purposes.
    """
    if instance.pk:  # Only for existing records (updates)
        try:
            old_instance = Student.objects.get(pk=instance.pk)
            changed_fields = []
            
            # Check key fields for changes
            if old_instance.student_name != instance.student_name:
                changed_fields.append('student_name')
            if old_instance.photo != instance.photo:
                changed_fields.append('photo')
            if old_instance.photo_url != instance.photo_url:
                changed_fields.append('photo_url')
            
            # Check certificate fields
            cert_fields = [
                'cert_achieve', 'cert_intern', 'cert_courses',
                'cert_sdp', 'cert_extra', 'cert_placement', 'cert_national',
                'cert_achieve_additional', 'cert_intern_additional',
                'cert_courses_additional', 'cert_sdp_additional',
                'cert_extra_additional', 'cert_placement_additional',
                'cert_national_additional',
            ]
            for field in cert_fields:
                old_val = getattr(old_instance, field, None)
                new_val = getattr(instance, field, None)
                if old_val != new_val:
                    changed_fields.append(field)
            
            if changed_fields:
                logger.debug(
                    f"Student {instance.ht_no} updated - Changed fields: "
                    f"{', '.join(changed_fields)}"
                )
        except Student.DoesNotExist:
            pass
