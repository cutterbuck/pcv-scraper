from package.app import app
from package.etl import run_scheduler



if __name__ == '__main__':
    run_scheduler()

    # from waitress import serve
    # serve(app.server, host="0.0.0.0", port=8080)

    app.run_server(debug=True, dev_tools_ui=False, use_reloader=False, port=8060)