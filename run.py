from app import app
from app.tgbot import main

from config import get_config
import threading


class FlaskThread(threading.Thread):
    def run(self) -> None:
        cfg = get_config()

        app.secret_key = 'secret key'
        app.run(
            port=80,
            host="0.0.0.0",
            debug=True,
            use_reloader=False
        )



if __name__ == "__main__":
    flask_thread = FlaskThread()
    flask_thread.start()

    main()








