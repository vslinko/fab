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
