from io import BytesIO

import pandas
import pandas as pd
from django.http import HttpResponse
from pandas import Timestamp

from prateek_gupta.exceptions import ServiceException
from prateek_gupta.utils import request_mapping
from utils import get_success_response


@request_mapping("GET")
async def extract_urls(request):
    try:
        # Define data
        data = {"Col 1": ["Key1", "Key2"], "Col 2": ["Value1", "Value2"]}

        # Create Pandas DataFrame
        df = pd.DataFrame(data)

        # Create an in-memory output file
        output = BytesIO()

        # Write DataFrame to an Excel file
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Sheet1")

        # Set file position to beginning
        output.seek(0)


        # Create HTTP response
        response = HttpResponse(output.read(),
                                content_type="application/vnd.openxmlformats-"
                                             "officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = 'attachment; filename="generated_file.xlsx"'


    except Exception:
        response = (ServiceException(error_id=ServiceException.UNKNOWN_ERROR)
                    .get_error_response())
    return response

@request_mapping("POST")
async def excel_to_json(request):
    # noinspection PyBroadException
    try:
        file = request.FILES.get('file')
        parsed_data=pandas.read_excel(file)
        data=dict()
        for row_id,row in parsed_data.iterrows():
            row_data = dict()
            for key,value in row.items():
                if str(value) in ['nan','NaT']:
                    value=""
                elif type(value) in [Timestamp]:
                    value=str(value)
                row_data[key]=value
            data["Row_"+str(int(str(row_id))+1)]=row_data
        response=get_success_response({"data":data})
    except ServiceException as e:
        response = e.get_error_response()
    except Exception:
        response = ServiceException().get_error_response()
    return response
