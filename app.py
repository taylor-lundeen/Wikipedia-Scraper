from flask import Flask, render_template, request, send_file
from zipfile import ZipFile
from io import BytesIO
from scraper import get_article_by_url
import os

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        search_term = request.form.get("term")
        language_code = request.form.get("language")
        file_dir = "textfiles/"
        if len(os.listdir(file_dir)) > 0:
            for f in os.listdir(file_dir):
                os.remove(os.path.join(file_dir, f))
        error_message = get_article_by_url(search_term, language_code, checked=False)
        if len(os.listdir(file_dir)) == 1:
            for f in os.listdir(file_dir):
                file_path = os.path.join(file_dir, f)
                try:
                    return send_file(file_path, as_attachment=True)
                except Exception as e:
                    print(e)
        elif len(os.listdir(file_dir)) > 1:
            stream = BytesIO()
            zipfile_name = search_term + ".zip"
            with ZipFile(stream, "w") as zf:
                for f in os.listdir(file_dir):
                    file_path = os.path.join(file_dir, f)
                    try:
                        zf.write(file_path, f)
                    except Exception as e:
                        print(e)
            stream.seek(0)
            try:
                return send_file(stream, as_attachment=True, download_name=zipfile_name)
            except Exception as e:
                print(e)
        else:
            return render_template('index.html', errorMessage=error_message)
    else:
        return render_template('index.html', errorMessage='')

if __name__ == "__main__":
    app.run()