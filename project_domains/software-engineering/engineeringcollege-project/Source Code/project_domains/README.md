# Project Domains

Each folder owns the source code and metadata for one public project domain.

- Add a project entry to the domain's `projects.json`.
- Store that project's code in a subfolder using the same slug.
- Its canonical public URL will be `/projects/<domain-slug>/<project-slug>/`.
- The domain itself is available at `/projects/<domain-slug>/`.

Keep shared Django infrastructure in the main application. Keep domain-specific
project code, documentation, datasets, and assets inside the matching folder.
Domain and project URLs must remain under `/projects/`; do not add root-level
public domain routes.

## Paid ZIP downloads

Add a `zip` object to a project entry when PhonePe payment should unlock a ZIP:

```json
{
  "slug": "example-project",
  "name": "Example Project",
  "description": "Example description.",
  "zip": {
    "enabled": true,
    "amount_paise": 25000,
    "source": "project-folder"
  }
}
```

`amount_paise` controls the PhonePe amount. Use `project-folder` to package only
that project's folder, or `repository` when the ZIP must contain the full
EngineeringCollege source tree.
