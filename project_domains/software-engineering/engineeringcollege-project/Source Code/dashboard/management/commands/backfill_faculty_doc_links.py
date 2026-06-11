from django.core.management.base import BaseCommand

from dashboard.models import CloudinaryUpload, Faculty, FDP, ResearchPublication


class Command(BaseCommand):
    help = (
        "Backfill missing ResearchPublication.proof_document_url and "
        "FDP.certificate_url values from faculty-level URLs and CloudinaryUpload records."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Persist changes. Without this flag, the command runs as a dry run.",
        )
        parser.add_argument(
            "--faculty-id",
            type=int,
            help="Only process one faculty record.",
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"]
        faculty_id = options.get("faculty_id")

        faculties = Faculty.objects.all().order_by("id")
        if faculty_id:
            faculties = faculties.filter(id=faculty_id)

        rp_updates = 0
        fdp_updates = 0

        for faculty in faculties:
            rp_updates += self._backfill_research_publications(faculty, apply_changes)
            fdp_updates += self._backfill_fdps(faculty, apply_changes)

        mode = "APPLIED" if apply_changes else "DRY RUN"
        self.stdout.write(self.style.SUCCESS(f"{mode} complete"))
        self.stdout.write(f"Research publication URLs updated: {rp_updates}")
        self.stdout.write(f"FDP certificate URLs updated: {fdp_updates}")

    def _backfill_research_publications(self, faculty, apply_changes):
        publications = list(
            ResearchPublication.objects.filter(faculty=faculty).order_by("created_at", "id")
        )
        missing = [pub for pub in publications if not (pub.proof_document_url or "").strip()]
        if not missing:
            return 0

        candidate_urls = []
        seen = set()

        faculty_url = (faculty.research_proof_url or "").strip()
        if faculty_url:
            candidate_urls.append(
                {
                    "url": faculty_url,
                    "academic_year": (faculty.research_proof_academic_year or "").strip(),
                    "source": "faculty.research_proof_url",
                }
            )
            seen.add(faculty_url)

        uploads = (
            CloudinaryUpload.objects.filter(faculty=faculty, upload_type="research_proof")
            .order_by("upload_date", "id")
        )
        for upload in uploads:
            url = (upload.cloudinary_url or "").strip()
            if url and url not in seen:
                candidate_urls.append(
                    {"url": url, "academic_year": "", "source": "CloudinaryUpload.research_proof"}
                )
                seen.add(url)

        updates = 0
        unused = candidate_urls[:]
        for pub in missing:
            selected = None
            pub_ay = (pub.academic_year or "").strip()

            if pub_ay:
                for item in unused:
                    if item["academic_year"] and item["academic_year"] == pub_ay:
                        selected = item
                        break

            if not selected and unused:
                selected = unused[0]

            if not selected:
                continue

            unused.remove(selected)
            updates += 1
            self.stdout.write(
                f"ResearchPublication {pub.id} <- {selected['source']} ({selected['url']})"
            )
            if apply_changes:
                pub.proof_document_url = selected["url"]
                pub.save(update_fields=["proof_document_url"])

        return updates

    def _backfill_fdps(self, faculty, apply_changes):
        fdps = list(FDP.objects.filter(faculty=faculty).order_by("created_at", "id"))
        missing = [fdp for fdp in fdps if not (fdp.certificate_url or "").strip()]
        if not missing:
            return 0

        candidate_urls = []
        seen = set()

        faculty_url = (faculty.fdp_certificate_url or "").strip()
        if faculty_url:
            candidate_urls.append(
                {
                    "url": faculty_url,
                    "academic_year": (faculty.fdp_certificate_academic_year or "").strip(),
                    "source": "faculty.fdp_certificate_url",
                }
            )
            seen.add(faculty_url)

        uploads = (
            CloudinaryUpload.objects.filter(faculty=faculty, upload_type="fdp_certificate")
            .order_by("upload_date", "id")
        )
        for upload in uploads:
            url = (upload.cloudinary_url or "").strip()
            if url and url not in seen:
                candidate_urls.append(
                    {"url": url, "academic_year": "", "source": "CloudinaryUpload.fdp_certificate"}
                )
                seen.add(url)

        updates = 0
        unused = candidate_urls[:]
        for fdp in missing:
            selected = None
            fdp_ay = (fdp.academic_year or "").strip()

            if fdp_ay:
                for item in unused:
                    if item["academic_year"] and item["academic_year"] == fdp_ay:
                        selected = item
                        break

            if not selected and unused:
                selected = unused[0]

            if not selected:
                continue

            unused.remove(selected)
            updates += 1
            self.stdout.write(f"FDP {fdp.id} <- {selected['source']} ({selected['url']})")
            if apply_changes:
                fdp.certificate_url = selected["url"]
                fdp.save(update_fields=["certificate_url"])

        return updates
