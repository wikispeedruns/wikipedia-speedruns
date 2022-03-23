from flask import request

from util.decorators import check_request_json

# TODO make this more flexible w.r.t validation and stuff
# TODO better error checking
# TODO figure out a better way to use checkreques json
# TODO figure out how to clean up resutls
#      see warning here: https://docs.celeryq.dev/en/stable/reference/celery.result.html#celery.result.AsyncResult
def register_async_endpoint(bp, baseUrl, task, parse_request):

    # Workaround because flask doesn't want endpoint functions with the same name
    def rename(func):
        func.__name__ += "_" + task.__name__
        return func

    @bp.post(baseUrl)
    @rename
    def start_task():
        result = parse_request(task, request)
        return {
            "task_id": result.id
        }

    @bp.post(baseUrl + "/result")
    @check_request_json({"task_id": str})
    @rename
    def poll_task_result():
        task_id = request.json['task_id']
        result = task.AsyncResult(task_id)

        if result.ready():
            return {
                "status": "complete",
                "result": result.get()
            }

        else:
            return {
                "status": "pending"
            }


