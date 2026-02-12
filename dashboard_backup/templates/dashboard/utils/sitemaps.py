# faculty/dashboard/sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Faculty


class FacultySitemap(Sitemap):
    """Sitemap for faculty profile pages"""
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        """Return all active faculty members"""
        return Faculty.objects.filter(is_active=True)

    def lastmod(self, obj):
        """Return last modified date"""
        return obj.updated_at

    def location(self, obj):
        """Return URL for each faculty"""
        return reverse('faculty:faculty_detail', args=[obj.id])


class StaticPagesSitemap(Sitemap):
    """Sitemap for static pages"""
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        """List of static page names"""
        return [
            'faculty:home',
            'faculty:faculty_list',
            'faculty:exam_branch',
            'faculty:reports_dashboard',
            'faculty:help',
            'faculty:guide',
            'faculty:faq',
        ]

    def location(self, item):
        """Return URL for each static page"""
        return reverse(item)


class DashboardSitemap(Sitemap):
    """Sitemap for dashboard pages"""
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        """List of dashboard pages"""
        return [
            'faculty:dashboard',
            'faculty:reports_dashboard',
            'faculty:settings',
        ]

    def location(self, item):
        """Return URL for each dashboard page"""
        return reverse(item)


class ExamBranchSitemap(Sitemap):
    """Sitemap for exam branch section"""
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        """Exam branch pages"""
        return [
            'faculty:exam_branch',
            'faculty:exam_branch_faculty_list',
        ]

    def location(self, item):
        """Return URL for each exam branch page"""
        return reverse(item)


# Combined sitemaps dictionary
faculty_sitemaps = {
    'faculty': FacultySitemap,
    'static': StaticPagesSitemap,
    'dashboard': DashboardSitemap,
    'exambranch': ExamBranchSitemap,
}