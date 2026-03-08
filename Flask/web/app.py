from flask import Flask, render_template

app = Flask(__name__)

#@app.route("/")
#def home():
#    return '''
#    <!DOCTYPE html>
#    <html>
#    <head>
#         <title>Simple Flask App</title>
#    </head>
#    <body>
#         <h1>Hello from Flask App!</h1>
#         <p>This is a basic HTML response</p>
#    </body>
#   </html>
         
 #   '''

@app.route("/")
def home():
    return render_template("home.html")

# http://127.0.0.1:5000/hello
@app.route("/hello")
def hello():
    return "Hello Flask World!"

# http://127.0.0.1:5000/add/100/30
@app.route("/add/<int:a>/<int:b>")
def add(a,b):
    result = a + b
    return f'''
    <h1>Add Result</h1>
    <p>{a} + {b} = {result}</p>
    <hr>
'''

if __name__ == "__main__":
    print("starting the web application")
    app.run(debug=True)
