# Student And Faculty PDF Generation

This package is the ownership boundary for generated student and faculty PDFs.

Keep PDF-specific code here whenever possible:

- Header and static asset names.
- Student and faculty PDF template names.
- PDF rendering, uploaded photo resolution, and certificate/document merge helpers.
- Public service functions called by `dashboard.views`.

The current project still has legacy generation functions in `dashboard/views.py`.
When changing PDF behavior, move the affected helper into this package first, then
update `views.py` to call the package API. This keeps unrelated page changes from
accidentally affecting photo embedding or certificate merging.
