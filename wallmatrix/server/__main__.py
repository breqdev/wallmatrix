import threading
import io

from flask import Flask, request, render_template, jsonify, Response

from dotenv import load_dotenv
load_dotenv()


from wallmatrix.driver.driver import DriverEvent
from wallmatrix.driver.default import Driver


driver = Driver()

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


@app.route("/flash", methods=["POST"])
def flash():
    message = request.json.get("message")
    driver.message_queue.put(DriverEvent(action="FLASH_MESSAGE", message=message))
    return "OK", 200

@app.route("/preview")
def preview():
    buf = io.BytesIO()
    driver.image.save(buf, format="PNG")
    return Response(buf.getvalue(), mimetype="image/png")


app_thread = threading.Thread(target=app.run, kwargs={"threaded": False})
app_thread.start()


try:
    driver.loop()
finally:
    driver.teardown()
