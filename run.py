from package.app import app
from package.scheduler import run_scheduler


if __name__ == '__main__':
    # run_scheduler()

    # from waitress import serve
    # serve(app.server, host="0.0.0.0", port=8080)

    app.run(debug=True, dev_tools_ui=True, use_reloader=True, port=8080)