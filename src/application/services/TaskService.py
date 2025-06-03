#from workers.tasks import ... 

class TaskService:
	def create_task(task, *args, **kwargs):
		task.delay(*args, **kwargs)