import os
import fabric.api
import setup


# ensure relative paths will work
os.chdir(os.path.dirname(__file__))


@fabric.api.task
@fabric.api.hosts("staging.rithis.com")
def staging():
    """
    server for projects based on symfony2 and static html
    """
    setup.debian()
    setup.dotdeb()
    setup.www_data()
    setup.php(["apc", "curl", "fpm", "gd", "intl", "mcrypt", "mysql", "pgsql", "sqlite"])
    setup.nginx("staging")


@fabric.api.task
@fabric.api.hosts("happynewgift.rithis.com")
def happynewgift():
    """
    server for happynewgift.ru staging server
    """
#    setup.debian()
#    setup.redis()
#    setup.mongo()
    setup.nodejs()

@fabric.api.task
@fabric.api.hosts("happynewgift.rithis.com")
def happynewgift_deploy():
    from fabric.api import run, sudo, cd

    sudo("sv stop frontend")
    sudo("sv stop backend")

    with cd("happynewgift"):
        run("git pull")
        run("npm install")

    sudo("sv start backend")
    sudo("sv start frontend")
