from flask import Flask, render_template, request, redirect
import json
import copy

app = Flask(__name__)
data = open("static/interviewee.json", mode="r", encoding="utf-8")
data = json.load(data)

file = open("form_setting.json", mode="r")
setting = json.load(file)


@app.route('/')
def hello_world():
    return redirect('/interviewee_list')


@app.route('/interviewee_list')
def interviewee_list():
    inter_list = copy.deepcopy(data)
    tempalte = """
        Age: %i,<br />
        Gender: %s,<br />
        Result: %s
    """
    for i in inter_list:
        inter = tempalte % (i["Age"], i["Gender"], i["Result"])
        i["inter"] = inter
    return render_template("list.html", inter_list=inter_list)


@app.route('/interviewee_form')
def interviewee_form():
    name = request.args.get("name")
    for i in data:
        if i["Name"] == name:
            info = i
            break

    template = {
        "Name": "Frank",
        "Age": "28",
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

    template["Name"] = info["Name"]
    template["Age"] = info["Age"]
    template["Gender"][info["Gender"]] = "selected"
    template["Result"][info["Result"]] = "selected"

    return render_template("form.html", i=template)


@app.route('/receive_from', methods=['POST'])
def receive_from():
    if request.method == 'POST':
        form = request.form
        i = {
            "Name": form["Name"],
            "Age": int(form["Age"]),
            "Gender": form["Gender"],
            "Result": form["Result"],
        }
        for index, ori in enumerate(data):
            if ori["Name"] == form["Name"]:
                data.pop(index)
                data.insert(index, i)
                break
        return redirect("/interviewee_list")


@app.route('/reset', methods=['GET'])
def reset():
    global data
    data = open("static/interviewee.json", mode="r", encoding="utf-8")
    data = json.load(data)
    return redirect('/interviewee_list')


# @app.route('/form_setting', methods=['GET'])
# def form_setting():
#     if request.method == 'GET':
#         url = request.args.get("url")
#         match = [i for i in filter(lambda x: x["address"] in url, setting)]
#         if len(match) != 1:
#             return "None"
#         else:
#             match = match[0]
#         return json.dumps(match)


if __name__ == '__main__':
    app.run(debug=True,port=5001)
    data = open("static/interviewee.json", mode="r", encoding="utf-8")
    data = json.load(data)

    file = open("form_setting.json", mode="r")
    setting = json.load(file)

    # open action
    # [
    #     {
    #         "act": "click",
    #         "sleep": 0.3,
    #         "element_fetch": {
    #             "type": "xpath",
    #             "argument": "/html[1]/body[1]/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]/a[1]"
    #         }
    #     },
    #     {
    #         "act": "click",
    #         "sleep": 0.3,
    #         "element_fetch": {
    #             "type": "xpath",
    #             "argument": "/html[1]/body[1]/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[2]/a[1]"
    #         }
    #     }
    # ]
