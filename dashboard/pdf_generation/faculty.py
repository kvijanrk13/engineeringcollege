"""Faculty PDF service boundary.

The implementation is still being migrated out of ``dashboard.views``. New code
should call these service functions, and migrated helpers should live in this
package instead of going back into the large views module.
"""


def build_faculty_profile_pdf_bytes(faculty):
    from dashboard import views as legacy_views

    return legacy_views.generate_faculty_pdf_bytes(faculty)


def persist_faculty_profile_pdf(faculty, pdf_bytes, uploaded_by=None):
    from dashboard import views as legacy_views

    return legacy_views.persist_faculty_pdf(faculty, pdf_bytes, uploaded_by=uploaded_by)


def build_faculty_profile_context(faculty):
    from dashboard import views as legacy_views

    return legacy_views.build_faculty_pdf_context(faculty)
