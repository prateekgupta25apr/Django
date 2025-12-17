

def preprocessed_data(request):
    """This method will provide few commonly required data to the templates, which can be
    accessed by using double curly braces(i.e. {{}})"""
    return {
        "static": "pre_processor_data",
        "dynamic": request.method
    }
