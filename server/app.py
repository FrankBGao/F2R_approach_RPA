from flask import Flask, request, jsonify, render_template, redirect
import json
import uuid
from datetime import datetime

from movement.driverCenter import Driver
from Translator import deploy_form_action_simply
from RuleEngine import SimpleListener
from RuleLearner import simple_rule_learner
from object.FormAction import FormAction
from IO_log_cleaner import clean_inspection, read_data

app = Flask(__name__)
port = "8000"

# form setting
file = open("form_setting.json", mode="r")
setting = json.load(file)
setting_dict = {}
for i in setting:
    setting_dict[i["name"]] = i

# rule
file = open("rule.json", mode="r")
rule_db = json.load(file)
rule_db_id_list = [i["rule_id"] for i in rule_db]
sl = SimpleListener(rule_db)

# running staff
cooked_io_log = []


#driver
drive = Driver()


@app.route('/')
def hello_world():
    return redirect("/show_rules")


@app.route('/reset')
def reset():
    what = request.args.get("what")
    if what == 'data':
        file_data = open("data.json", mode="w")
        file_data_template = open("data_ac.json", mode="r")
        file_data_template = file_data_template.read()
        file_data.write(file_data_template)
        file_data.close()
        return redirect("/show_iolog")
    if what == "rule":
        global rule_db, rule_db_id_list, sl
        file_rule = open("rule.json", mode="r")
        rule_db = json.load(file_rule)
        rule_db_id_list = [i["rule_id"] for i in rule_db]
        sl = SimpleListener(rule_db)
        return redirect("/show_rules")
    return redirect("/show_rules")


def read_clean_io_log():
    global cooked_io_log
    cooked_io_log = clean_inspection(read_data("data.json"))
    cooked_io_log.sort(key=lambda x: x["tb"], reverse=True)
    return cooked_io_log


def convert_timestamp(timestamp):
    timestamp = timestamp / 1000
    dt_object = datetime.fromtimestamp(timestamp)
    return str(dt_object)


###############################################################################
# Ear, IO-Log server
###############################################################################
@app.route('/form_setting', methods=['GET'])
def form_setting():
    """
    Ear
    send form setting to extension
    :return:
    """
    if request.method == 'GET':
        url = request.args.get("url")
        match = [i for i in filter(lambda x: x["address"] in url, setting)]
        if len(match) != 1:
            match = {"NotAllow": True}
        else:
            match = match[0]
            for i in match["form_field"]:
                inter = i["address"].split("/")[-1]
                if inter == "select":
                    inter = "input"
                i["tag"] = inter
            match["NotAllow"] = False
            match["fa_id"] = str(uuid.uuid4())

        res = jsonify(match)
        res.headers['Access-Control-Allow-Origin'] = '*'
        return res


@app.route('/receive_form_action', methods=['POST'])
def receive_form_action():
    """
    Ear
    recieve form action from extension,
    """
    if request.method == 'POST':
        fa = request.form["data"]

        # store data
        store_data = fa
        form_json = open("data.json", mode="a")
        store_data = store_data + ","
        form_json.write(store_data)
        form_json.close()
        # listen and response

        fa = FormAction(json.loads(fa))
        resp = sl.listen(fa)
        if resp != "NoResponse":
            deploy_form_action_simply(resp, setting_dict, drive)

        return "success"


###############################################################################
# pages
###############################################################################
# rule
@app.route('/show_rules')
def show_rules():
    """
    Brain
    the page of robot brain, rule
    """
    rule_list = []
    des_templete = """
    Listen: %s<br />
    Generate: %s<br />
    Type: %s<br />
    From: %s<br />
    """
    for i in rule_db:
        inter = {
            "Name": i["name"],
            "Id": i["rule_id"],
            "Desp": des_templete % (i["listen"], i["generate"], i["type_is"], i["condition_type"])
        }
        rule_list.append(inter)

    return render_template('rule.html', rule_list=rule_list)  # , chart_output=rule["condition"]['pic']


def draw_condition(type_is, infor, listen):
    if type_is == "learned":
        return infor["pic"]
    template = "%i. %s %s %s"
    result = "Form " + listen + " should"
    index = 1
    for i in infor:
        inter = template % (index, i[0] + "-" + i[1], i[2], i[3])
        result = result + "<br />" + inter
        index += 1

    return result


def draw_response(infor, listen, generate):
    # this place should use form field id, rather form field name
    template_link = "%s--  %s  -->%s"
    result = "graph LR\nlinkStyle default interpolate basis"
    l_node = "subgraph " + listen
    r_node = "subgraph " + generate
    for i in infor:
        left = i[0]["listen"]
        relation = i[1]
        right = i[2][1]
        for l in left:
            one_link = template_link % (listen[0] + "-" + l[1], relation, generate[0] + "-" + right)
            result = result + "\n" + one_link
            l_node = l_node + "\n" + listen[0] + "-" + l[1]
            r_node = r_node + "\n" + generate[0] + "-" + right

    result = result + "\n" + l_node + "\nend\n" + r_node + "\nend"
    return result


@app.route('/rule_detail')
def rule_detail():
    """
    API for interface, detail button
    """
    id_is = request.args.get("id_is")
    this_rule = [i for i in filter(lambda x: x["rule_id"] == id_is, rule_db)][0]

    result = {
        "condition_type": this_rule["condition_type"],
        "condition": draw_condition(this_rule["condition_type"], this_rule["condition"], this_rule["listen"]),
        "response": draw_response(this_rule["response"], this_rule["listen"], this_rule["generate"])
    }

    return jsonify(result)


@app.route('/delete_rule')
def delete_rule():
    """
    API for interface, delete button
    """
    id_is = request.args.get("id_is")
    sl.delete_rule(id_is)

    index = rule_db_id_list.index(id_is)
    rule_db_id_list.pop(index)
    rule_db.pop(index)
    return "success"


@app.route('/learn_rule')
def learn_rule():
    """
    API for interface, learn button
    trigger the learning process
    """
    this_cooked_io_log = read_clean_io_log()
    new_rules = simple_rule_learner(this_cooked_io_log)
    for one_rule in new_rules:
        sl.add_one_rule(one_rule)
        rule_db_id_list.append(one_rule["rule_id"])
    rule_db.extend(new_rules)
    return redirect('/show_rules')


# form setting
@app.route('/show_form_setting')
def show_form_setting():
    """
    Brain
    the page of robot brain, setting
    """
    setting_list = []
    type_is = ["table-warning", ""]
    for index, i in enumerate(setting):
        type_index = index % 2
        inter = {
            "num": index + 1,
            "Name": i["name"],
            "Type_is": type_is[type_index]
        }
        setting_list.append(inter)

    return render_template('setting.html', inter_list=setting_list)


@app.route('/setting_detail')
def setting_detail():
    """
    API for interface, detail button, form setting
    """
    id_is = request.args.get("id_is")
    this_rule = [i for i in filter(lambda x: x["name"] == id_is, setting)][0]
    return jsonify(this_rule)


# io_log
@app.route('/show_iolog')
def show_iolog():
    """
    Brain
    the page of robot brain, io_log
    """
    cooked_io_log = read_clean_io_log()

    io_log = []
    type_is = ["table-warning", ""]
    for index, i in enumerate(cooked_io_log):
        type_index = index % 2
        inter = {
            "num": index + 1,
            "frm": i["frm"],
            "tb": convert_timestamp(i["tb"]),
            "fa_id": i["fa_id"],
            "Type_is": type_is[type_index]
        }
        io_log.append(inter)

    return render_template('iolog.html', inter_list=io_log)


@app.route('/fa_detail')
def fa_detail():
    """
    API for interface, detail button, io_log
    """
    global cooked_io_log
    if len(cooked_io_log) == 0:
        cooked_io_log = read_clean_io_log()
    id_is = request.args.get("id_is")
    this_fa = [i for i in filter(lambda x: x["fa_id"] == id_is, cooked_io_log)][0]
    this_fa = FormAction(this_fa)
    this_fa = this_fa.infor_dict
    this_fa.pop("final_value")
    return jsonify(this_fa)


@app.route('/clean_log')
def clean_log():
    file_data = open("data.json", mode="w")
    file_data.write("")
    file_data.close()
    return redirect("/show_iolog")


@app.route('/refresh_io_log')
def refresh_io_log():
    return redirect("/show_iolog")
    # cooked_io_log = read_clean_io_log()
    #
    # io_log = []
    # type_is = ["table-warning", ""]
    # for index, i in enumerate(cooked_io_log):
    #     type_index = index % 2
    #     inter = {
    #         "num": index + 1,
    #         "frm": i["frm"],
    #         "tb": convert_timestamp(i["tb"]),
    #         "fa_id": i["fa_id"],
    #         "Type_is": type_is[type_index]
    #     }
    #     io_log.append(inter)
    # return jsonify(io_log)


#drive.get("localhost:" + port + "/show_rules")

if __name__ == '__main__':
    # file = open("form_setting.json", mode="r")
    # setting = json.load(file)
    #
    # setting_dict = {}
    # for i in setting:
    #     setting_dict[i["name"]] = i
    #
    # # rule
    # file = open("rule.json", mode="r")
    # rule = json.load(file)
    #
    # sl = SimpleListener(rule)
    #

    app.run(port=port)


