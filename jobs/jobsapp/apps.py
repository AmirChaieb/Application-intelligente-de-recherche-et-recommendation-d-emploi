from django.apps import AppConfig
import threading


ch="""class JobsappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jobsapp'
    def ready(self):
        from .utils import scrape_novojob_selenium
        threading.Thread(target=scrape_novojob_selenium).start()"""
