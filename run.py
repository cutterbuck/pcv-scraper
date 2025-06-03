from package.app import app
from waitress import serve


if __name__ == '__main__':
    # serve(app.server, host="0.0.0.0", port=8080)
    app.run(debug=True, dev_tools_ui=True, use_reloader=False, port=8080)