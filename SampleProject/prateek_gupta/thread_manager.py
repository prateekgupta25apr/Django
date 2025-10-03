from concurrent.futures import ThreadPoolExecutor

from prateek_gupta import post_destruct_method

executor = ThreadPoolExecutor(max_workers=5)


@post_destruct_method()
def thread_cleanup():
    executor.shutdown(wait=True)
    print("thread_cleanup called")