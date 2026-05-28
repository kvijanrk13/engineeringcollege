"""Student PDF service boundary.

The implementation is still being migrated out of ``dashboard.views``. New code
should call these service functions, and migrated helpers should live in this
package instead of going back into the large views module.
"""


def generate_student_profile_pdf(student, return_bytes=False, photo_override_path=None, certificate_override_assets=None):
    from dashboard import views as legacy_views

    return legacy_views.generate_student_pdf(
        student,
        return_bytes=return_bytes,
        photo_override_path=photo_override_path,
        certificate_override_assets=certificate_override_assets,
    )


def generate_student_profile_pdf_bytes(student):
    return generate_student_profile_pdf(student, return_bytes=True)
