from datetime import datetime

test_type = "tree-nlp"
now = datetime.now()
timestr = now.strftime("_%m-%d-%Y_%H-%M-%S")
file_name = '/' + test_type + timestr + '.csv'
print(file_name)