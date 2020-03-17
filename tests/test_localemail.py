from app import mail


def test_send_email(app):
    with app.app_context():
        mail.init_app(app)
        with mail.record_messages() as outbox:
            mail.send_message(subject='testing',
                            body='test',
                            recipients=['scottcho@qq.com'])
            assert len(outbox) == 1
            assert outbox[0].subject == "testing"
    