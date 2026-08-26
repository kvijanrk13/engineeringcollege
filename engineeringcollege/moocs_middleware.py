from django.shortcuts import redirect


class MoocsExamLockMiddleware:
    """Keep a Gmail-verified MOOCS session inside the examination area."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        locked = request.session.get("moocs_exam_lock") is True
        exam_path = request.path in {"/MOOCS", "/MOOCS/", "/MOOCS/logout/"}
        asset_path = request.path.startswith(("/static/", "/media/"))
        asset_request = asset_path and request.headers.get("Sec-Fetch-Dest", "") != "document"
        if locked and not (exam_path or asset_request):
            return redirect("moocs")
        return self.get_response(request)
