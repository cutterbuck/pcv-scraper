from package.app import app
from waitress import serve
from package.scheduler import run_scheduler



if __name__ == '__main__':
    run_scheduler()

    serve(app.server, host="0.0.0.0", port=8080, threads=100)
    # app.run(debug=True, dev_tools_ui=True, use_reloader=False, port=8080)