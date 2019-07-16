from flask import Flask, render_template, request, redirect
import json
import copy
import datetime

app = Flask(__name__)
data = open("static/interviewee.json", mode="r", encoding="utf-8")
data = json.load(data)


@app.route('/')
def hello_world():
    return redirect('/employee_list')


@app.route('/employee_list')
def employee_list():
    inter_list = copy.deepcopy(data)
    Type_is = ["table-warning", ""]
    for index, i in enumerate(inter_list):
        type_index = index % 2
        i["num"] = index + 1
        i["Type_is"] = Type_is[type_index]
    return render_template("list.html", inter_list=inter_list)


@app.route('/new_form')
def new_form():
    template = {
        "Name": "",
        "Age": "",
        "Gender": {
            "Male": "",
            "Female": "",
        },
        "Result": {
            "e": "",
            "p": "selected",
            "f": "",
        }
    }

    return render_template("form.html", i=template)


@app.route('/receive_from', methods=['POST'])
def receive_from():
    if request.method == 'POST':
        form = request.form
        i = {
            "Name": form["Name"],
            "Age": int(form["Age"]),
            "Gender": form["Gender"],
            "Date": str(datetime.datetime.now()).split(" ")[0]
        }
        data.insert(0, i)
        return redirect("/employee_list")


@app.route('/reset', methods=['GET'])
def reset():
    global data
    data = open("static/interviewee.json", mode="r", encoding="utf-8")
    data = json.load(data)
    return redirect('/employee_list')


if __name__ == '__main__':
    app.run(debug=True,port=5002)
    data = open("static/interviewee.json", mode="r", encoding="utf-8")
    data = json.load(data)
