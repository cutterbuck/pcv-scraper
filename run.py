from package.app import app
from package.etl import run_scheduler



if __name__ == '__main__':
    run_scheduler()
    # run_scraper()
    app.run_server(debug=True, dev_tools_ui=False, use_reloader=True)
