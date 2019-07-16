import pickle
import graphviz
import base64
import uuid
from collections import Counter
import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn import tree

from object.FormAction import FormAction
from IO_log_cleaner import clean_inspection, read_data
from rule_engine.response_function import function_list as response_functions


# find pattern with "Name" field is the case id
# relate form action
def detect_pattern_with_case_id_field(cooked_io_log, case_id_field):
    # final_value the last observation equal with other form action's case id field
    case_id = list(set([i.final_value(case_id_field) for i in cooked_io_log]))

    cased_io_log = []
    pattern = []
    for i in case_id:
        inter = [i for i in filter(lambda x: x.final_value(case_id_field) == i, cooked_io_log)]
        inter.sort(key=lambda x: x["tb"])

        cased_io_log.append(inter[:2])

        if len(inter) == 2:
            pattern.append(tuple([i["frm"] for i in inter]))

    pattern = list(set(pattern))
    return pattern, cased_io_log


def gain_pattern_relate_io_log(one_pattern, cased_io_log):
    one_pattern_relate_fa = []

    for i in cased_io_log:
        if len(i) == 1:
            if i[0]["frm"] in one_pattern:
                one_pattern_relate_fa.append(i)
                continue
        inter_tuple = (i[0]["frm"], i[1]["frm"])
        if inter_tuple == one_pattern:
            one_pattern_relate_fa.append(i)
    return one_pattern_relate_fa


def find_condition_dtree(one_pattern, one_pattern_relate_fa):
    # obs table
    tabel = []
    for case in one_pattern_relate_fa:
        inter = case[0].flat_infor()
        if len(case) == 2:
            inter['label'] = case[1]["frm"]
        else:
            inter['label'] = "No"
        tabel.append(inter)

    table = pd.DataFrame(tabel).sort_values("label")
    label_name = list(table["label"].drop_duplicates())

    train = table.drop(["label", "fa_id", "frm", "tb", "tf"], axis=1).to_dict(orient='record')  # , "fread" + case_id_field

    dv_train = DictVectorizer(sparse=False)
    x_train = dv_train.fit_transform(train)

    d_tree = tree.DecisionTreeClassifier(criterion="entropy")
    d_tree.fit(x_train, list(table["label"]))

    dot_data = tree.export_graphviz(d_tree, out_file=None, feature_names=dv_train.feature_names_,
                                    class_names=label_name)
    graph = graphviz.Source(dot_data, filename="")
    chart_output = graph.pipe(format="png")

    pickle_infor = {
        'model': d_tree,
        'vector': dv_train,
        'pattern': one_pattern
    }

    result = {
        'name': '2'.join(one_pattern),
        'listen': one_pattern[0],
        'generate': one_pattern[1],
        "type_is": "simple",
        'condition_type': 'learned',
        'rule_id': str(uuid.uuid4()),
        'condition': {
            'info': pickle.dumps(pickle_infor),
            'pattern': one_pattern,
            'pic': base64.b64encode(chart_output).decode('utf-8'),
        }

    }
    return result


def find_response(one_rule, one_pattern_relate_fa):
    # generate the response link between fa
    # first see first count
    # this part could do more things, also could learn function between values
    candidate = [i for i in filter(lambda x: len(x) == 2, one_pattern_relate_fa)]
    result_link = []

    # this project, we only consider equal as we target function
    target_function = "equal"
    fun = response_functions[target_function]
    for i in candidate:
        left = i[0]
        right = i[1]
        for r in right["fwrite"].keys():
            for l in left["final_value"].keys():
                arg = {}
                left_value = fun([left["final_value"][l]], arg)
                right_value = right["fwrite"][r]
                if left_value == right_value:
                    inter = [{"listen": [["final_value", l]], "arg": {}}, target_function, ["fwrite", r]]
                    if inter not in result_link:
                        result_link.append(inter)
                    break
    one_rule["response"] = result_link
    return one_rule


def simple_rule_learner(cooked_io_log):
    cooked_io_log = [FormAction(i) for i in cooked_io_log]

    case_id_field = "Name"
    # clean_data, the log must have identifier
    cooked_io_log = [i for i in filter(lambda x:x.final_value(case_id_field) is not None, cooked_io_log)]
    pattern, cased_io_log = detect_pattern_with_case_id_field(cooked_io_log, case_id_field)
    rules = []
    for this_pattern in pattern:
        pattern_relate_fa = gain_pattern_relate_io_log(this_pattern, cased_io_log)
        this_rule = find_condition_dtree(this_pattern, pattern_relate_fa)
        this_rule = find_response(this_rule, pattern_relate_fa)
        rules.append(this_rule)

    return rules


if __name__ == '__main__':
    this_cooked_io_log = clean_inspection(read_data())
    g_rules = simple_rule_learner(this_cooked_io_log)
    print(g_rules)






# clf2 = pickle.loads(s)
# clf2.predict([x_train[0]])
# print(chart_output)
