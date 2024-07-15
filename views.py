import io
import random
import string
import zipfile

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from .forms import DropForm
from .models import Drop


def home(request):
    return render(request, 'home.html')


class SuccessView(View):
    template_name = 'success.html'

    def get(self, request):
        form = DropForm()
        return render(request, self.template_name, {'form': form})


class SendView(View):
    template_name = 'send.html'

    def get(self, request):
        form = DropForm()
        return render(request, self.template_name, {'form': form, 'code': None})

    def post(self, request):
        form = DropForm(request.POST, request.FILES)
        if form.is_valid():
            # Generate a random 7-character code
            code = self.generate_random_code()
            files = request.FILES.getlist('file')  # Get a list of uploaded files

            # Create a new database entry for each file
            for file in files:
                new_drop = Drop(code=code, file=file)
                new_drop.save()

            messages.success(request, 'Files successfully uploaded!')
            return render(request, self.template_name, {'form': None, 'code': code})
        return render(request, self.template_name, {'form': form, 'code': None})

    def generate_random_code(self):
        # Generate a random 7-character/digit code
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(7))


class ReceiveView(View):
    template_name = 'receive.html'

    def get(self, request):
        return render(request, self.template_name, {'code_input': ''})

    def post(self, request):
        code_input = request.POST.get('code_input')
        try:
            drops = Drop.objects.filter(code=code_input)
            download_link = None

            if drops:
                # Create a ZIP file in memory
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w') as zipf:
                    for drop in drops:
                        with drop.file.open('rb') as file:
                            zipf.writestr(drop.file.name, file.read())

                # Save the ZIP file to the 'uploads/' directory
                zip_filename = f"uploads/{code_input}_files.zip"
                with open(zip_filename, 'wb') as zip_file:
                    zip_file.write(zip_buffer.getvalue())

                # Provide a direct link to download the ZIP file
                download_link = zip_filename  # Only the relative path to 'uploads/'

            return render(request, self.template_name,
                          {'code_input': code_input, 'drops': drops, 'download_link': download_link})
        except Drop.DoesNotExist:
            return HttpResponse("Files not found")
