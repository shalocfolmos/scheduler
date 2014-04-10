# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
import datetime

class AppIdList(models.Model):
    class Meta:
        db_table = 'appid_list'
    # id = models.IntegerField(primary_key=True,db_column='id')
    appId = models.CharField(db_column="appid",max_length=45)
    # main_class = models.CharField(db_column="mainclass",max_length=45)
    # is_free = models.IntegerField(db_column='isfree',max_length=4)
    # device = models.IntegerField(db_column='device',max_length=4)
    # sub_class = models.CharField(db_column="subclass",max_length=45)
    is_analysised_successful = models.BooleanField(db_column="is_analysised_successful")

class Author(models.Model):

    class Meta:
        db_table='warehouse_author'

    icon = models.CharField(max_length=100,blank=True,default='')

    cover = models.CharField(max_length=100,blank=True,default='')



    name = models.CharField(verbose_name=_('author name'),
                            max_length=64)

    email = models.EmailField(verbose_name=_('email'),
                              unique=True,default=str(datetime.datetime.now())+"@test_case.com")

    phone = models.CharField(verbose_name=_('phone'),
                             max_length=16,
                             blank=True,
                             null=True)

    home_page = models.URLField(blank=True,null=True)

    author_app_id = models.CharField(max_length=100,default='',blank=True)

    status = models.CharField(max_length=100)


class Package(models.Model):
    class Meta:
        db_table='warehouse_package'

    title = models.CharField(
        verbose_name=_('package title'),
        max_length=128)

    package_type_choices = (
        ('android','Android'),
        ('iphone','Iphone'),
        ('unknown','Unknown')
    )

    package_type = models.CharField(max_length=15,choices=package_type_choices,null=False,blank=False,default='android')

    package_name = models.CharField(
        verbose_name=_('package name'),
        unique=True,
        max_length=128)

    summary = models.CharField(
        verbose_name=_('summary'),
        max_length=255,
        null=False,
        default="",
        blank=True)

    description = models.TextField(
        verbose_name=_('description'),
        null=False,
        default="",
        blank=True)

    author = models.ForeignKey(Author, related_name='packages')

    released_datetime = models.DateTimeField(
        verbose_name=_('released time'),
        db_index=True,
        blank=True,
        null=True)

    created_datetime = models.DateTimeField(
        verbose_name=_('created time'),
        auto_now_add=True)

    updated_datetime = models.DateTimeField(
        verbose_name=_('updated time'),
        auto_now_add=True,auto_now=True)


    tags_text = models.CharField(max_length=255,
        default="",
        blank=True)

    download_count = models.PositiveIntegerField(
        verbose_name=_('package download count'),
        max_length=9,
        default=0,
        blank=True
    )


    status = models.CharField(max_length=100,verbose_name=_('status'),default='draft')


class IosPackage(Package):

    class Meta:
        db_table='warehouse_iospackage'

    # def __init__(self):
    #     Package.__init__(self)
    #     self.package_type = "Iphone"

    ios_preview_url = models.URLField(null=True,blank=True)
    ios_created_datetime = models.DateTimeField(
        verbose_name=_('created time'),
        auto_now_add=True)

    ios_updated_datetime = models.DateTimeField(
        verbose_name=_('updated time'),
        auto_now_add=True)



class PackageVersion(models.Model):

    class Meta:
        db_table = 'warehouse_packageversion'


    icon = models.CharField(
        max_length=100,
        blank=True
    )

    cover = models.CharField(
        max_length=100,
        blank=True
    )


    download = models.CharField(
        verbose_name=_('version file'),
        max_length=100,
        default='',
        blank=True)

    di_download = models.CharField(
        verbose_name=_('version file with data integration'),
        max_length=100,
        default='',
        blank=True
    )

    download_count = models.PositiveIntegerField(
        verbose_name=_('package version download count'),
        max_length=9,
        default=0,
        blank=True
    )

    package = models.ForeignKey(Package, related_name='versions')

    version_name = models.CharField(
        verbose_name=_('version name'),
        max_length=16,
        blank=False,
        null=False)

    version_code = models.IntegerField(
        verbose_name=_('version code'),
        blank=False,
        null=False)

    whatsnew = models.TextField(
        verbose_name=_("what's new"),
        default="",
        blank=True)

    file_size = models.CharField(
        max_length="50",
        default="",
        null=False,
        blank=True
    )

    status = models.CharField(max_length=100,default='draft', blank=True)

    released_datetime = models.DateTimeField(db_index=True, blank=True,
                                             null=True)

    created_datetime = models.DateTimeField(auto_now_add=True)

    updated_datetime = models.DateTimeField(auto_now=True, auto_now_add=True)


class IosPackageVersion(PackageVersion):
    # primary_id = models.AutoField(primary_key=True)
    # package_version_id = models.OneToOneField(PackageVersion,parent_link=True)

    class Meta:
        db_table='warehouse_iospackageversion'

    CONCURRENCY_TYPE = (
        ('UK','美金'),
        ('RMB','人民币')
    )

    appstore_id = models.CharField(
        max_length=50,
        unique=True,
        null=False,
        blank=False
    )

    user_center_is_enabled = models.BooleanField(default=False)
    concurrent_version_point = models.CharField(max_length=10,blank=True,null=True)
    sale_price = models.FloatField(default=0.00)
    concurrency_type = models.CharField(max_length=30,choices=CONCURRENCY_TYPE)
    support_device = models.CharField(max_length=300,blank=True,null=True)
    ios_created_datetime = models.DateTimeField(
        verbose_name=_('created time'),
        auto_now_add=True)

    ios_updated_datetime = models.DateTimeField(
        verbose_name=_('updated time'),
        auto_now=True)


class PackageVersionScreenshot(models.Model):
    version = models.ForeignKey(PackageVersion, related_name='screenshots')

    class Meta:
        db_table='warehouse_packageversionscreenshot'

    image = models.CharField(
        max_length=100,
        blank=False
    )

    alt = models.CharField(
        _('image alt'),
        max_length=30,
        blank=True)

    PLAT_FORM = (
        ('unknown','UNKNOWN'),
        ('ipadscreenshot','Ipad Screen Shot'),
        ('screenshot','Screen Shot')
    )

    apply_platform = models.CharField(null=True,blank=True,default='unknown',choices=PLAT_FORM
        ,max_length=30)

    ROTATE = (
        ( '-180', '-180'),
        ( '-90', '-90'),
        ( '0', '0'),
        ( '90', '90'),
        ( '180', '180'),
    )

    rotate = models.CharField(
        verbose_name=_('image rotate'),
        max_length=4,
        default=0,
        choices=ROTATE)


class FetchHistory(models.Model):
    app_id = models.CharField(max_length=50)
    fetch_type = models.CharField(max_length=50,db_column="ios_scheduler_fetch_type")
    fetch_process_log = models.CharField(max_length=100)
    created_time = models.DateTimeField(auto_now=True)
