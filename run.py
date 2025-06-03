from package.app import app


if __name__ == '__main__':
    # from waitress import serve
    # serve(app.server, host="0.0.0.0", port=8080)

    app.run(debug=True, dev_tools_ui=True, use_reloader=False, port=8080)