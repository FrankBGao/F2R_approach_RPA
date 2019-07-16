import json
import copy

from movement.driverCenter import Driver
import time

one_activity = {
    "act": "click",
    "element_fetch": {
        "type": "xpath",
        "argument": "//button[@type='submit']"
    }
}


def variable_arrive():
    # this part need do more stuff
    return []


def no_variable_arrive(begin_route):
    result = {}
    motions = []
    for i in begin_route["motion"]:
        inter = copy.deepcopy(one_activity)
        inter["act"] = i["motion"]
        inter["element_fetch"]["argument"] = i["address"]
        motions.append(inter)
    result["motions"] = motions

    if begin_route["how_arrive"] == "get":
        result["how_arrive"] = begin_route["start_address"]

    return result


def deploy_form_action_simply(fa, setting_dict, drive):
    this_form_setting = setting_dict[fa["frm"]]
    begin_route = this_form_setting["begin_route"]
    finish_route = this_form_setting["finish_route"]

    ####################
    # arrive the form
    ####################
    if "motion_variable" not in begin_route:
        arrive = no_variable_arrive(begin_route)
    else:
        arrive = variable_arrive()

    ####################
    # deploy the form action writing
    ####################
    deploy_form_action_leave = []
    for i in fa["fwrite"].keys():
        fld_name = i
        fld_value = fa["fwrite"][fld_name]
        xpath = [i for i in filter(lambda x: x["name"] == fld_name, this_form_setting["form_field"])][0]
        xpath = xpath["address"]

        inter = copy.deepcopy(one_activity)
        inter["act"] = "send_keys"
        inter["send_keys"] = fld_value
        inter["element_fetch"]["argument"] = xpath

        deploy_form_action_leave.append(inter)
    ####################
    # finish and leave
    ####################
    finish_form_action = copy.deepcopy(one_activity)
    finish_form_action["act"] = finish_route["motion"]
    finish_form_action["element_fetch"]["argument"] = finish_route["address"]
    deploy_form_action_leave.append(finish_form_action)

    if "how_arrive" in arrive:
        drive.get(arrive["how_arrive"])
    drive.run_activities(arrive["motions"])
    drive.run_activities(deploy_form_action_leave)


if __name__ == '__main__':
    file = open("form_setting.json", mode="r")
    setting = json.load(file)
    setting_dict = {}
    for i in setting:
        setting_dict[i["name"]] = i

    fa = {"fread": {"Name": "", "Age": "", "Gender": "Female"},
          "fwrite": {"Name": "Willa Pickett", "Age": "16", "Gender": "Female"}, "tb": 1554306872000,
          "tf": 1554306873000,
          "u": "resource", "frm": "New Employee"}

    # robot do this work
    drive = Driver()
    deploy_form_action_simply(fa, setting_dict, drive)

    time.sleep(1000)



