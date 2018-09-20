from flask import Flask, request, render_template
import subprocess

app = Flask(__name__)

@app.route('/')
def my_form():
    return render_template('my-form.html')

@app.route('/', methods=['POST'])
def hello():
    text = request.form['text']
    s = text.split(' ')
    cmd = ["python", "htrszng.py"]+s
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            stdin=subprocess.PIPE)
    out, err = p.communicate()
    return out

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050)

