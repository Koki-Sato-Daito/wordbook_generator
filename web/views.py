import datetime

from django.core.files.storage import default_storage
from django.views.generic import View, TemplateView
from django.shortcuts import render, redirect
import pandas as pd

from web.forms import UploadFileForm
from tasks.models import Task
from tasks.tasks import get_task_chain
from wordbook_generator.settings.base import MEDIA_URL


class FileManagerView(View):
    def get(self, request, *args, **kwargs):
        form = UploadFileForm()
        return render(request, 'web/upload.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            now_date = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            original_file = request.FILES['original_file']
            default_storage.save(now_date, original_file)
            task = Task.objects.create(original_file_path=now_date)

            chain = get_task_chain(task.id)
            async_result = chain.apply_async()
            task.async_result_id = async_result.task_id
            task.save()
            return redirect(f'/waiting_task/{task.id}/')
        return render(request, 'web/upload.html', {'form': form})


class DemoView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'web/demo.html')

    def post(self, request, *args, **kwargs):
        task = Task.objects.create(original_file_path="alice.html")

        chain = get_task_chain(task.id)
        async_result = chain.apply_async()
        task.async_result_id = async_result.task_id
        task.save()
        return redirect(f'/waiting_task/{task.id}/')


class WaitingTaskPage(TemplateView):
    template_name ='web/waiting_task.html'

    def get_context_data(self, task_id, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['task_id'] = task_id
        return ctx


class ResultTaskPage(TemplateView):
    template_name = 'web/result_task.html'

    def get_context_data(self, task_id, **kwargs):
        task = Task.objects.get(id=task_id)
        df = pd.read_csv(task.output_file_path, index_col=0)
        now= datetime.datetime.now()

        ctx = super().get_context_data(**kwargs)
        file_path =  task.output_file_path.replace('/var/www/wordbookge/media/', '')
        ctx['csv_download_path'] = f'{MEDIA_URL}{file_path}'
        ctx['csv_download_name'] = f'{now}.csv'
        ctx['data'] = df.head(50).to_dict(orient="records")
        return ctx