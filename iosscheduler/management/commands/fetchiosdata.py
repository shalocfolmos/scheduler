# -*- coding: utf-8 -*-
from django.core.management import BaseCommand
import iosscheduler.job.ios_scheduler_job as scheduler_job


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.requires_model_validation = True
        scheduler_job.start_job(stdout=self.stdout)