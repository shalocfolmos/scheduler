# -*- coding: utf-8 -*-
from django.test import TestCase
# from django.utils.unittest.case import skip
import iosscheduler.models as model
from iosscheduler.job.ios_scheduler_job import *
import datetime


# class IosPackageVersionModelTest(TestCase):
#
#     def setUp(self):
#         author = model.Author(name='sam_test',email='sam_test1@gmail.com',phone="18621697984"
#             ,status='OK',cover='cover',home_page='homepage',author_app_id='100',icon="icon")
#         author.save()
#         package_model = model.IosPackage(title='start',package_name="game",summary="game summary",
#                                          description="game description",
#                                          package_type='iphone',
#                                          released_datetime= datetime.datetime.now(),
#                                         tags_text='a',status='ok0',download_count=0,ios_preview_url="ios_preview_url"
#                                         )
#         package_model.author=author
#         package_model.save()
#
#         package_version = model.IosPackageVersion(version_name='version_name'
#                 ,version_code=1,whatsnew='whatsnew',
#                 created_datetime=datetime.datetime.now(),
#                 updated_datetime=datetime.datetime.now(),
#                 released_datetime=datetime.datetime.now(),
#                 icon = 'icon',
#                 download = 'download',
#                 cover = 'cover',
#                 status='ok',user_center_is_enabled=False,
#                 di_download = 'dl_download',
#                 download_count = 1,
#                 concurrent_version_point = 1,
#                 sale_price = 1.0,
#                 concurrency_type = 'concurrency_type',
#                 support_device = 'support_device'
#         )
#         package_version.package = package_model
#         package_version.save()
#
#     def test_package_model(self):
#         package_version = model.IosPackageVersion.objects.filter(version_name = 'version_name').get()
#         self.assertTrue(package_version.version_name,'version_name')
#
#
#     def tearDown(self):
#         package_version = model.IosPackageVersion.objects.filter(version_name = 'version_name').get()
#         package = package_version.package
#         author = package.author
#         package_version.delete()
#         package.delete()
#         author.delete()

class ParseDataTest(TestCase):
    # def setUp(self):
    #     model.PackageVersion.objects.all().delete()
    #     model.Package.objects.all().delete()
    #     model.Author.objects.all().delete()
    #
    #     for i in range(2000):
    #         appId = model.AppIdList(appId="100"+str(i),main_class='main_class',
    #                         sub_class='sub_class',is_analysised_successful=False)
    #         appId.save(using="mysql")

    def test_process_app_id(self):
        process_app_id('849923632')

        # process_app_id(848275730)
        # author = model.Author.objects.get
        # self.assertIsNotNone(author.name)
