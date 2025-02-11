from io import BytesIO

import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render

from prateek_gupta import request_mapping
from prateek_gupta.exceptions import ServiceException


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
