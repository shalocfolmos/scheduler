# -*- coding: utf-8 -*-

import unittest
from http import client
import urllib.request
import iosscheduler.models as model
import json
import os
import queue
import concurrent.futures
import threading

_THREAD_POOL_SIZE = 5
_TASK_COUNT_FOR_EACH_EXECUTOR=100
_connection = client.HTTPSConnection('itunes.apple.com')
_base_dir = "/Users/sunsam/screen_shot_dir/"
_task_queue = queue.Queue(_TASK_COUNT_FOR_EACH_EXECUTOR)
_queue_lock = threading.Lock()
_std_out = None


def _make_fetch_hsitory(app_id,error_log):
    fetch_history = model.FetchHistory(app_id=app_id,fetch_type='error',fetch_process_log=error_log)
    fetch_history.save()

def _create_screen_shot_from_dict(dict,package_version):
    for screen_shot_key in dict.keys():
        try:
            screen_shot_url = dict[screen_shot_key]
            if _std_out:
                _std_out.write('start save screen shot' + str(package_version.appstore_id) + " url" + screen_shot_url)
            file_prefix = screen_shot_url[screen_shot_url.rfind("."):len(screen_shot_url)]
            file_name = screen_shot_key+file_prefix

            content_date = urllib.request.urlopen(screen_shot_url).read()
            content_file = open(_base_dir+package_version.appstore_id+"/screenshot/"+file_name
            ,'wb')
            content_file.write(content_date)

            packageVersionScreenShot = model.PackageVersionScreenshot(version=package_version,
                                           image=file_name,apply_platform='screenshot')
            packageVersionScreenShot.save()
        except Exception as e:
            _make_fetch_hsitory(package_version.appstore_id,'screen shot save'+file_name+' error '+str(e))
            if _std_out:
                _std_out.write('error save ipad screen shot' + str(package_version.appstore_id) + " url" + screen_shot_url+ " error" + str(e))

def _transfer_json_to_object(json_datajson_data):
    data = json_datajson_data["results"][0]
    artist_id = str(data["artistId"])
    artist_view_url = data["artistViewUrl"]
    artist_name = data["artistName"]
    author = model.Author(author_app_id=artist_id,home_page=artist_view_url,name=artist_name)
    iosPackage = model.IosPackage()
    iosPackage.description = data["description"]
    iosPackage.package_name = data["trackCensoredName"]
    iosPackage.title = data["trackCensoredName"]
    iosPackage.ios_preview_url = data["trackViewUrl"]

    packageVersion = model.IosPackageVersion()
    packageVersion.support_device = ".".join(data["supportedDevices"])
    packageVersion.user_center_is_enabled = data["isGameCenterEnabled"]
    packageVersion.sale_price=data["price"]
    packageVersion.version_name=str(data["version"])
    packageVersion.appstore_id = str(data["trackId"])
    packageVersion.concurrency_type = data["currency"]

    version_code_list = packageVersion.version_name.split(".")
    version_code_str = ''
    if len(version_code_list) == 2:
        version_code_list.append('0')

    for version_code in version_code_list:
        version_code_str+=(version_code.rjust(2,'0'))
    packageVersion.version_code = int(version_code_str)


    packageVersion.file_size = data["fileSizeBytes"]
    packageVersion.released_datetime = data["releaseDate"]
    packageVersion.concurrent_version_point = data["trackContentRating"]

    atwork_url_dict = {}
    for key in data.keys():
        if key.find("artworkUrl") != -1:
            size = key[key.rfind("Url")+3:len(key)]
            atwork_url_dict[size] = data[key]


    screen_shot_dict={}
    if len(data["screenshotUrls"]) >0:
        screen_shot_list = data["screenshotUrls"]
        for idx,screen_shot in enumerate(screen_shot_list):
            screen_shot_dict[str(packageVersion.appstore_id)+"_screen_"+str(idx)] = screen_shot

    ipad_screen_shot_dict = {}
    if len(data["ipadScreenshotUrls"])>0:
        ipad_screen_shot_list = data["ipadScreenshotUrls"]
        for idx,screen_shot in enumerate(screen_shot_list):
            ipad_screen_shot_dict[str(packageVersion.appstore_id)+"_ipadscreen_"+str(idx)] = screen_shot


    return [author,iosPackage,packageVersion,atwork_url_dict,screen_shot_dict,ipad_screen_shot_dict]


def _make_author(author, package_version):
    try:
        has_author = model.Author.objects.filter(author_app_id=author.author_app_id).all()
        if has_author:
            has_author.home_page = author.home_page
            has_author.name = author.name
            has_author.save()
            author = has_author
        else:
            author.save()
    except Exception as e:
        _make_fetch_hsitory(package_version.appstore_id, 'Save author error' + str(e))


def _make_package_icon(icon_dict, package, package_version):
    if len(icon_dict) > 0:
        package.icon = package_version.appstore_id + "_icon"
        for icon_key in icon_dict.keys():

            try:
                icon_url = icon_dict[icon_key]
                if _std_out:
                    _std_out.write('start get icon for ' + str(package_version.appstore_id) +
                        "file name" + icon_url)

                icon_data = urllib.request.urlopen(icon_url).read()

                if _std_out:
                    _std_out.write('get icon data successful ' + icon_url)

                f = open(_base_dir + package_version.appstore_id + "/" + package.icon +
                         icon_key + ".png", "wb")
                if _std_out:
                    _std_out.write('save icon data successful ' + _base_dir + package_version.appstore_id + "/" + package.icon +
                         icon_key + ".png")

                f.write(icon_data)
            except Exception as e:
                _make_fetch_hsitory(package_version.appstore_id, 'save icon ' + "/" + package.icon +
                                                                 icon_key + ".png" + ' error ' + str(e))


def _make_author(author, package_version):
    try:
        has_author = model.Author.objects.filter(author_app_id=author.author_app_id).all()
        if has_author:
            old_author = has_author[0]
            old_author.home_page = author.home_page
            old_author.name = author.name
            old_author.save()
            author = old_author
        else:
            author.save()
    except Exception as e:
        _make_fetch_hsitory(package_version.appstore_id, 'Save author error' + str(e))
        if _std_out:
            _std_out.write("save author error " + str(author.name) + str(e))
    return author


def process_app_id(app_id):
    try:
        data = urllib.request.urlopen("https://itunes.apple.com/lookup?id="+str(app_id)).read()
    except Exception as e:
        if _std_out:
            _std_out.write('fetch app json error ' + str(app_id)+str(e))
        _make_fetch_hsitory(app_id,'fetch app json error '+str(e))
        raise e

    if data:
        if _std_out:
            _std_out.write('start transfer data')
        json_data = str(data.strip(),'UTF-8')
        parseResult = _transfer_json_to_object(json.loads(json_data))

        if _std_out:
            _std_out.write('parse end' + str(app_id))



        author = parseResult[0]
        package = parseResult[1]
        package_version = parseResult[2]
        icon_dict = parseResult[3]
        os.chdir(_base_dir)

        try:
            if not os.path.exists(str(package_version.appstore_id)+"/screenshot"):
                os.makedirs(str(package_version.appstore_id)+"/screenshot")
        except Exception as e:
            _make_fetch_hsitory(package_version.appstore_id,'Create table error'+str(e))
            if _std_out:
                _std_out.write('exception ' + str(app_id)+ str(e))

        if _std_out:
            _std_out.write('start make author ' + str(app_id))

        author = _make_author(author, package_version)

        _make_package_icon(icon_dict, package, package_version)

        target_package = None
        if _std_out:
            _std_out.write('start save package ' + str(app_id))
        try:
            old_package_list = model.IosPackage.objects.filter(package_name = package.package_name).all()
            if old_package_list:
                old_package = old_package_list[0]
                old_package.description = package.description
                old_package.package_name = package.package_name
                old_package.title = package.title
                old_package.ios_preview_url = package.ios_preview_url
                old_package.icon = package.icon
                if _std_out:
                    _std_out.write("author id %s"%str(author.id))
                old_package.author=author
                old_package.save()
                target_package = old_package
            else:
                if _std_out:
                    _std_out.write("author id %s"%str(author.id))
                package.author=author
                package.save()
                target_package = package
        except Exception as e:
            if _std_out:
                _std_out.write('error save package' + str(app_id) + str(e))
            _make_fetch_hsitory(package_version.appstore_id,'package save error '+str(e))


        try:
            if _std_out:
                    _std_out.write('start save package version1' + str(app_id))
            old_package_version_list = model.IosPackageVersion.objects.filter(appstore_id=package_version.appstore_id).all()
            if old_package_version_list:
                if _std_out:
                    _std_out.write('start save package version3' + str(app_id))
                old_package_version = old_package_version_list[0]
                old_package_version.support_device = package_version.support_device
                old_package_version.user_center_is_enabled = package_version.user_center_is_enabled
                old_package_version.sale_price = package_version.sale_price
                old_package_version.concurrency_type = package_version.concurrency_type
                old_package_version.file_size = package_version.file_size
                old_package_version.released_datetime = package_version.released_datetime
                old_package_version.concurrent_version_point = package_version.concurrent_version_point
                old_package_version.package=target_package
                old_package_version.save()
                target_package_version = old_package_version
            else:
                if _std_out:
                    _std_out.write('start save package version2' + str(app_id))
                package_version.package=target_package
                package_version.save()
                package_version.save()
                target_package_version = package_version
        except Exception as e:
            if _std_out:
                _std_out.write('error save package version' + str(app_id) + str(e))
            _make_fetch_hsitory(package_version.appstore_id,'package_version save error '+str(e))


        screen_shot_dict = parseResult[4]
        ipad_screen_shot_dict = parseResult[5]

        if _std_out:
            _std_out.write('start save screen shot' + str(app_id))
        if len(screen_shot_dict)>0:
            _create_screen_shot_from_dict(dict=screen_shot_dict,
                                         package_version=target_package_version)
        if _std_out:
                _std_out.write('start save ipad screen shot' + str(app_id))
        if len(ipad_screen_shot_dict)>0:
             _create_screen_shot_from_dict(dict=ipad_screen_shot_dict,
                                         package_version=target_package_version)


def _start_load_data():
    while True:
        _queue_lock.acquire()
        app_id = _task_queue.get(block=True)
        _queue_lock.release()
        if _std_out:
            _std_out.write('start process %s ' % app_id)
        try:
            process_app_id(app_id)
            if _std_out:
                _std_out.write('process %s successful' % app_id)

            try:
                app = model.AppIdList.objects.using("mysql").filter(appId=app_id).get()
                app.is_analysised_successful = True
                app.save()
            except Exception as e:
                if _std_out:
                    _std_out.write('change app status error' + str(app_id) + str(e))
        except Exception as e:
            _std_out.write('error process %s exception:%s' % (app_id,str(e)))





def start_job(stdout=None):
    global _std_out
    _std_out = stdout
    processed_count = 0
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=_THREAD_POOL_SIZE)
    for i in range(_THREAD_POOL_SIZE):
        executor.submit(_start_load_data)
    try:
        should_process_count = model.AppIdList.objects.filter(is_analysised_successful = False).using("mysql").count()
        if stdout:
            stdout.write(str(should_process_count))
    except Exception as e:
        stdout.write(e)

    while processed_count <= should_process_count:
        try:
            app_id_list = model.AppIdList.objects.using("mysql").filter(is_analysised_successful = False)[processed_count:processed_count+_TASK_COUNT_FOR_EACH_EXECUTOR]
            for app_id in app_id_list:
                _task_queue.put(app_id.appId)
            while(not _task_queue.empty()):
                pass
            processed_count+=_TASK_COUNT_FOR_EACH_EXECUTOR
        except Exception as e:
            if stdout:
                stdout.write(str(e))
    _make_fetch_hsitory('000000','SHUT DOWN EXECUTOR')
    executor.shutdown(wait=False)
