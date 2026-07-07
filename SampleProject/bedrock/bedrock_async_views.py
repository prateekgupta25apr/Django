from prateek_gupta.LogManager import logger
from prateek_gupta.bedrock_async import (
    generate_embedding_for_image, generate_embedding_for_text)
from prateek_gupta.exceptions import ServiceException, module_lock_check
from prateek_gupta.utils import request_mapping
from project_utils import get_success_response, get_error_response


@request_mapping("POST")
async def generate_embedding_for_image_request(request):
    logger.info("Entering generate_embedding_for_image_request()")
    # noinspection PyBroadException
    try:
        module_lock_check("BEDROCK_ENABLE", "A")

        image_url = request.POST.get('image_url')
        embedding = await generate_embedding_for_image(image_url)
        response = get_success_response({
            "message": "Image embedding generated successfully",
            "embedding": embedding,
            "embedding_dimension": len(embedding),
        })
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing generate_embedding_for_image_request()")
    return response


@request_mapping("POST")
async def generate_embedding_for_text_request(request):
    logger.info("Entering generate_embedding_for_text_request()")
    # noinspection PyBroadException
    try:
        module_lock_check("BEDROCK_ENABLE", "A")

        text = request.POST.get('text')
        embedding = await generate_embedding_for_text(text)
        response = get_success_response({
            "message": "Text embedding generated successfully",
            "embedding": embedding,
            "embedding_dimension": len(embedding),
        })
    except ServiceException as e:
        response = get_error_response(e)
    except Exception:
        response = get_error_response(ServiceException())
    logger.info("Existing generate_embedding_for_text_request()")
    return response
