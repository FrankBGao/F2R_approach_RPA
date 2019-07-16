import copy
from sklearn.feature_extraction import DictVectorizer


class FormAction:
    def __init__(self, infor_dict):
        self.final_value_dict = {}
        self.infor_dict = self.clean_fa(infor_dict)
        self.behavior = self.gain_behavior()
        self.dom_read = ""
        self.dom_write = ""

    # remove no information form field from fa
    def clean_fa(self, fa):
        # the final observation
        self.final_value_dict = copy.deepcopy(fa["fwrite"])

        keys = list(fa["fwrite"].keys())
        for i in keys:
            if fa["fread"][i] == fa["fwrite"][i]:
                fa["fwrite"].pop(i)

        keys = list(fa["fread"].keys())
        for i in keys:
            if fa["fread"][i] == "":
                fa["fread"].pop(i)
        fa["final_value"] = self.final_value_dict
        return fa

    def final_value(self, item):
        if item in self.final_value_dict:
            return self.final_value_dict[item]
        return None

    def __getitem__(self, item):
        return self.infor_dict.get(item)

    def gain_behavior(self):
        fa = self.infor_dict
        self.dom_read = set(fa["fread"].keys())
        self. dom_write = set(fa["fwrite"].keys())

        if len(self.dom_write) == 0:
            return "Inspection"
        if len(self.dom_read) == 0:
            return "Fill"
        return "Update"

    def flat_infor(self):
        fread = self.infor_dict["fread"]
        inter = dict()
        for i in fread.keys():
            inter["fread" + i] = fread[i]

        fwrite = self.infor_dict["fwrite"]
        for i in fwrite.keys():
            inter["fwrite" + i] = fwrite[i]

        for i in ["fa_id", "frm", "tb", "tf", "u"]:
            inter[i] = self.infor_dict[i]
        return inter

    # # for sklearn
    # def vector_fa_infor(self, fa_flat_vector):
    #     x_train = fa_flat_vector.fit_transform(self.flat_infor())
    #     return x_train


if __name__ == '__main__':
    a = {
        "fread": {
            "Name": "Frank",
            "Age": "28",
            "Gender": "Male",
            "Result": "Estimating"
        },
        "fwrite": {
            "Name": "Frank",
            "Age": "28",
            "Gender": "Male",
            "Result": "Pass"
        },
        "tb": 1554903763000,
        "tf": 1554903780000,
        "u": "resource",
        "frm": "Interviewee",
        "fa_id": "37cdcfb6-0aa7-4b48-8e51-39216b9db289"
    }
    fa = FormAction(a)
    fa_flat_vector = DictVectorizer(sparse=False)
    print(fa.final_value("Name"))
    print(fa["final_value"]["Name"])
    print(fa["frm"])
    bb = "frm" in fa.dom_read
    print(a)
