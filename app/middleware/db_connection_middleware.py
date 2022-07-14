from app.database import db_session


class DbSessionManager(object):

    def process_request(self, req, resp):
        db_session.connect()

    def process_response(self, req, resp, resource, req_succeeded):
        if not db_session.is_closed():
            db_session.close()
