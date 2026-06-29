class AdminCSPExemptMiddleware:
    """Снимает заголовок CSP с админки.

    Unfold использует Alpine.js, которому нужен 'unsafe-eval'. Строгий CSP
    проекта блокирует его, из-за чего JS админки не инициализируется и поверх
    страницы остаётся невидимый оверлей, перехватывающий клики. Публичный сайт
    остаётся под строгим CSP — снимаем заголовок только на /admin/.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith('/admin'):
            response.headers.pop('Content-Security-Policy', None)
            response.headers.pop('Content-Security-Policy-Report-Only', None)
        return response
