# do not use this code

# import json
# from scrapy import Selector
#
# data = open("data.json")
# data = json.load(data)
#
# form_setting = open("form_setting.json")
# form_setting = json.load(form_setting)
#
# inter_html = data["html"]
# inter_html = "<html><body>" + inter_html
# inter_html = inter_html + "</html></body>"
#
# response = Selector(text=inter_html)
# #  xpath = '/html/body/div/div[2]/div[2]/form/div[1]/input'
# xpath = '/html/body/div/div[2]/div[2]/form/div[3]/select/option[1]'
# field = response.xpath(xpath)
# field_value = field.attrib["value"]
# print(field)
# input, need to find the attribute from input tag
# select, need to find every option, and find a select option. it has a attrib, key is the selected