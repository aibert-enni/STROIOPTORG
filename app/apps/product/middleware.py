from django.contrib.sessions.middleware import SessionMiddleware


class SaveOldSessionKeyMiddleware(SessionMiddleware):

    def __call__(self, request):
        session_key = request.session.session_key

        if session_key:
            old_key = request.session.get('old_session')
            if old_key != session_key:
                request.session['old_session'] = session_key

        return self.get_response(request)