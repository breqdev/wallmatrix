import threading

from flask import Flask, request, render_template, jsonify

from dotenv import load_dotenv
load_dotenv()


from wallmatrix.driver import DriverEvent
from wallmatrix.driver.default import Driver


driver = Driver()
driver.setup()

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/sources", methods=["GET", "POST"])
def sources():
    if request.method == "GET":
        return jsonify({
            "current": driver.current_source,
            "all": {
                import_name: source.SOURCE_NAME
                for import_name, source in driver.sources.items()
            }
        })
    elif request.method == "POST":
        source_name = request.json.get("source")

        if source_name in driver.sources:
            driver.message_queue.put(DriverEvent(action="SOURCE_CHANGED", source=source_name))
            return "OK", 200
        else:
            return "Source not found", 404


app_thread = threading.Thread(target=app.run, kwargs={"threaded": False})
app_thread.start()


try:
    driver.loop()
finally:
    driver.teardown()