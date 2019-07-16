import json
import copy
import pickle
from rule_engine.condition_function import function_list as condition_functions
from rule_engine.response_function import function_list as response_functions

rule = {
    "name": "interview2new",  # new of rule, it is unique
    # simple rule, just listen last fa, generate one fa; currently just focus on this one
    # complex fa will looking more and generate more
    "rule_id": "9a04dabb-c355-4cfc-8bfa-8965559843ea",
    "type_is": "simple",
    "listen": "Interviewee",  # form name, condition fa will happen on this form
    "generate": "New Employee",  # form name, generate fa will happen on this form
    "condition_type": "modeled",  # only two type, learned and modeled
    # a list of condition, which listen form should be satisfy, could be modeled, or
    # if it satisfy, it will trigger the response
    # [fread/fwrite, form_field, condition_function, value need put into the condition_function]
    #######################
    # this place could be a model from machine learning, each is auto learned, structure will be like commend below
    #        'condition': {
    #             'info': pickle.dumps(pickle_infor),
    #             'pattern': one_pattern,
    #             'pic': base64.b64encode(chart_output).decode('utf-8'),
    #          }
    #
    "condition": [
        ["fread", "Result", "equal", "Estimating"],
        ["fwrite", "Result", "equal", "Pass"]
    ],
    # a list of mapping, map a or a set of listen form's fields to a response form field
    # [source node, response function, target node]
    # source node: listen: a list, listen fa's field or a set of field,
    #              arg: a dict, key for response function, value is constant or a form filed value from listen fa
    "response": [
        [{"listen": [["final_value", "Name"]], "arg": {}}, "equal", ["fwrite", "Name"]],
        [{"listen": [["final_value", "Age"]], "arg": {}}, "equal", ["fwrite", "Age"]],
        [{"listen": [["final_value", "Gender"]], "arg": {}}, "equal", ["fwrite", "Gender"]]
    ]

}


class RuleTypeError(RuntimeError):
    def __init__(self, arg):
        self.args = arg


class SimpleRule:
    def __init__(self, rule):
        condition_dict = {
            "learned": self._learned_condition,
            "modeled": self._modeled_condition,
        }
        self.rule_id = rule["rule_id"]
        self.rule_info = rule
        self.condition = condition_dict[rule["condition_type"]]
        self.condition_info = rule["condition"]
        self.response_list = rule["response"]
        self.generate_form = rule["generate"]
        self.listen_form = rule["listen"]

        if rule["condition_type"] == "learned":
            # transfer model string into code
            self.condition_info["info"] = pickle.loads(self.condition_info["info"])

    def _learned_condition(self, input_fa):
        # run learned condition, predict
        model = self.condition_info["info"]["model"]
        result = self.condition_info["info"]["pattern"][1]
        vector = self.condition_info["info"]["vector"]

        input_fa = input_fa.flat_infor()
        x_data = vector.transform(input_fa)
        perdict_result = model.predict(x_data)[0]

        return perdict_result == result

    def _modeled_condition(self, fa):
        # satisfy the requirement
        if fa["frm"] != self.listen_form:
            return False

        for i in self.condition_info:
            if i[1] not in fa[i[0]]:
                return False
            left = fa[i[0]][i[1]]
            right = i[3]
            func = condition_functions[i[2]]
            if not func(left, right):
                return False
        return True

    def _response(self, fa):
        resp = {"fread": {},
                "fwrite": {},
                "u": "Robot",
                "frm": self.generate_form}

        for i in self.response_list:
            put_in = []
            for lis in i[0]["listen"]:
                put_in.append(fa[lis[0]][lis[1]])
            arg = i[0]["arg"]

            func = response_functions[i[1]]
            value = func(put_in, arg)

            read_write = i[2][0]
            filed = i[2][1]
            resp[read_write][filed] = value

        return resp

    def listen(self, fa):
        inter = self.condition(fa)
        if inter:
            return self._response(fa)
        return "NoResponse"


class SimpleListener:
    def __init__(self, rules):
        # support delete, add
        # current not support modify
        self.rules_info = [i for i in filter(lambda x: x["type_is"] == "simple", rules)]
        self.rules = [SimpleRule(i) for i in self.rules_info]
        self.listen_forms = [i["listen"] for i in self.rules_info]
        self.rule_id_list = [i["rule_id"] for i in self.rules_info]

    def add_one_rule(self, one_rule):
        if one_rule["type_is"] != "simple":
            raise RuleTypeError("Wrong Type Rule")
        self.rules.append(SimpleRule(one_rule))
        self.rule_id_list.append(one_rule["rule_id"])
        self.listen_forms.append(one_rule["listen"])
        return "success"

    def delete_rule(self, one_rule_id):
        if one_rule_id not in self.rule_id_list:
            return "success"
        index = self.rule_id_list.index(one_rule_id)
        self.rules.pop(index)
        self.listen_forms.pop(index)
        self.rule_id_list.pop(index)
        return "success"

    def listen(self, fa):
        # find satisfy rule
        inter = [i for i, frm in enumerate(self.listen_forms) if frm == fa["frm"]]
        match_form_rule = [self.rules[i] for i in inter]
        # find first match rule to response
        # this part need more clever
        for i in match_form_rule:
            resp_fa = i.listen(fa)
            if resp_fa != "NoResponse":
                return resp_fa

        return "NoResponse"


if __name__ == '__main__':
    from object.FormAction import FormAction
    file = open("form_setting.json", mode="r")
    setting = json.load(file)
    setting_dict = {}
    for i in setting:
        setting_dict[i["name"]] = i

    fa = {"fread": {"Name": "Sheldon", "Age": "38", "Gender": "Male", "Result": "Estimating"},
          "fwrite": {"Name": "Sheldon", "Age": "38", "Gender": "Male", "Result": "Pass"}, "tb": 1554364323000,
          "tf": 1554367060000, "u": "resource", "frm": "Interviewee"}

    sl = SimpleListener([rule])
    print(sl.listen(FormAction(fa)))
