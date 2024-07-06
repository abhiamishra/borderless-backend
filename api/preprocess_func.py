from fastapi import FastAPI, Depends, Body

def preprocess(data: dict = Body(...)):
    # Convert dictionary back to JSON string (optional)
  # print(data)
  # print(type(data))
  # print(data.keys())
  fieldsLst = data["data"]["fields"]
  inputDataJSON = {
    0:"isEnroll",
    1:"school",
    2:"major",
    3:"degreeLevel",
    4:"startDate",
    5:"isenrollAlt",
    6:"nameAlt",
    7:"isfullTime",
    8:"englishLevel",
    9:"isTOEFL",
    10:"TOEFLScore",
    11:"isEnrollEnglishCourse",
    12:"isResidence",
    13:"isFamily",
    14:"isEmployed",
    15:"hasAssets",
    16:"isReturn"}

#   inputValueLst = []
  finalInputData = {}
  for idx, field in enumerate(fieldsLst[1:]):

    value = ""
    if "options" in field.keys():
      # print(field)
      # print(field["value"])
      if field["value"] is None or len(field["value"]) == 0:
        value = None
      else:
        valueKey = field["value"][0]
        for option in field["options"]:
          if option["id"] == valueKey:
            value = option["text"]
    elif field["value"] is not None:
       value = field["value"]
       if value == 'Yes':
          value = True
       elif value == 'No':
          value = False
    else:
       value = None

    key = inputDataJSON[idx]
    finalInputData[key] = value

  return finalInputData


    
#     inputValueLst.append(value)


#   for idx, val in enumerate(inputValueLst):
#     key = inputDataJSON[idx]
#     if val == -1:
#        finalInputData[key] = None
#     else:
#         finalInputData[key] = val
