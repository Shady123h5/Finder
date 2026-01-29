    from flask import Flask, Response
    from threading import Thread
    import logging

    logging.getLogger('werkzeug').setLevel(logging.ERROR)

    app = Flask(__name__)

    @app.route('/')
    def home() -> Response:
        return Response("Bot is alive!", status=200, mimetype='text/plain')

    @app.route('/health')
    def health() -> Response:
        return Response("OK", status=200, mimetype='text/plain')

    def run() -> None:
        try:
            from waitress import serve
            serve(app, host='0.0.0.0', port=5000)
        except ImportError:
            app.run(host='0.0.0.0', port=5000, threaded=True)

    def keep_alive() -> None:
        Thread(target=run, daemon=True).start()