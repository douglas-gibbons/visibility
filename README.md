visibility
==========

## Background
Software builds should be repeatable and transparent.  Often [Continuous Delivery](http://en.wikipedia.org/wiki/Continuous_delivery) workflows are 
built on top of tools such as Jenkins, which are great at task management, but less so at providing an overall view of workflows.  CI jobs may be
cleared away after a time, leaving the user clueless as to what version of code build what version of product.

 
## So, What is Visibility?

Visibility is an application designed to provide clear workflow dashboards and offer traceable product delivery:

[![ScreenShot](https://raw.github.com/zenly/visibility/master/screenshots/Visibility_Youtube_Video.png)](https://www.youtube.com/watch?v=cDcs_wEg3Dw)

##How does it do it

Visibility is a [Django project](https://www.djangoproject.com/). It has an API to feed a database
with build, deployment and test information from workflows.  This information can then be displayed on the web interface.

It's designed to be simple enough so that it can be modified for different purposes; for example, instead of just displaying
information it could also be used as a controller with a little extra coding. With that in mind, the code is written
as a standard Django project (hopefully) with no "clever" surprises. 



## Prerequisite

* Python (tested with 2.7) and Django 1.5
* git (so you can quickly download the code)

## Basic setup

* Grab the code with `git clone git://github.com/zenly/visibility.git`
* Change into the `visibility/src` directory
* Initiate a database with `python manage.py syncdb`
* Start up the application with `python manage.py runserver`
* Browse to [http://localhost:8000/](http://localhost:8000/)
* Check the help page on your instance at [http://localhost:8000/dash/help](http://localhost:8000/dash/help)

If you want to quickly see how it looks without fiddling with the API:

* Start up the application with `python manage.py runserver`
* Then, in another terminal run `python manage.py dummyrun`

This starts up a dummy continuous delivery pipeline; pretending to run builds, deployments and tests of a product in real time.
You should be able to see it working from [your local instance](http://localhost:8000/dash/pipeline?numpipes=20&product=Example+Pipeline).
This starts the `run` function from a new instance of `Dummy` found in `src/dash/tests/dummy.py`.  All this class does
is make a few calls to the API in real time so you can see how it might look with your own CD pipeline.

Running `python manage.py` causes Django to only listen on the default IP address; 127.0.0.1 which is not accessible from
other machines on your network. Optionally you could run `python manage.py 0.0.0.0:8000` to rectify this. For production
it is strongly recommended that a different web server such Apache is used.

Once you've had a play, you might want to:
* Start using the API (check the [docs](http://localhost:8000/dash/help#api) on your local instance).
* Change the timezone in src/settings.py from "TIME_ZONE = 'Europe/London'" to something appropriate for you
* Use [Apache with mod_wsgi](https://docs.djangoproject.com/en/1.5/howto/deployment/wsgi/modwsgi/)
* Change the [database](https://docs.djangoproject.com/en/1.5/ref/databases/)
* Fork the code and customise it!

## Debian / Ubunutu Packaging

Probably the quickest way to get started is to create and install the debian package.

Clone the code and run packaging/make_deb.sh

Deb packages can be instaled on the command line:

    sudo apt-get install -y gdebi-core
    gdebi <deb filename>


## License

Licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).
