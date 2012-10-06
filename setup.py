from fabric.api import run, sudo, cd, lcd, settings
from template import tput


def debian():
    # start setup under root
    with settings(user="root", no_keys=True):
        # update packages index
        run("aptitude update")

        # install favorite packages
        run("aptitude install -y sudo zsh git")

        # allow sudo for root, admin group, and sudo group
        # sudo group can use sudo without password
        with lcd("templates"), cd("/etc"):
            tput("sudoers", use_sudo=False, mode=0o440)

        # create user with zsh and sudo group
        run("useradd -ms /bin/zsh -G sudo vyacheslav")

        # rewrite authorization keys
        with lcd("templates/authorized_keys"), cd("/home/vyacheslav"):
            run("rm -rf .ssh")
            run("mkdir -m 0700 .ssh")
            tput("vyacheslav", ".ssh/authorized_keys", use_sudo=False, mode=0o400)
            run("chown vyacheslav:vyacheslav -R .ssh")

    # continue under my user
    # update dotfiles
    with cd("/home/vyacheslav"):
        sudo("git clone -n https://github.com/vslinko/dotfiles.git")
        sudo("mv dotfiles/.git .")
        sudo("rm -r dotfiles")
        sudo("git reset --hard")

    # upgrade system
    sudo("aptitude upgrade -y")

    # disable root password
    sudo("passwd -d root")


def dotdeb(php54=False):
    # add dotdeb key to aptitude as trusted
    if sudo("apt-key list | grep dotdeb", quiet=True).failed:
        sudo("wget -qO- http://www.dotdeb.org/dotdeb.gpg | apt-key add -")

    # copy dotdeb source list
    with lcd("templates/sources.list.d"), cd("/etc/apt/sources.list.d"):
        tput("dotdeb.list", php54=php54)

    # download new lists with available packages
    sudo("aptitude update")


def www_data():
    # try to create www-data directories
    sudo("mkdir -p /var/www/.ssh")

    # allow me to login as www-data
    with lcd("templates/authorized_keys"), cd("/var/www/.ssh"):
        tput("vyacheslav", "authorized_keys", mode=0o400)

    # repair modes and owners
    sudo("chmod 700 /var/www/.ssh")
    sudo("chown www-data:www-data -R /var/www")


def php(modules=None, **kwargs):
    # cli is required
    if not modules:
        modules = ["cli"]
    elif "cli" not in modules:
        modules.append("cli")

    # install modules
    sudo("aptitude install -y %s" % " ".join(map(lambda x: "php5-" + x, modules)))

    # redefine some global configuration variables
    with lcd("templates/php/conf.d"), cd("/etc/php5/conf.d"):
        tput("php.ini", "00-php.ini")

    # configure fpm if installed
    if "fpm" in modules:
        with lcd("templates/php"), cd("/etc/php5/fpm"):
            tput("php-fpm.conf", **kwargs)
            sudo("rm -r pool.d")

        # restart with new configuration
        sudo("service php5-fpm restart")


def nginx(template, package="light", **kwargs):
    # install nginx package
    sudo("aptitude install -y nginx-%s" % package)

    # copy configuration
    with lcd("templates/nginx/" + template), cd("/etc/nginx"):
        tput("nginx.conf", **kwargs)
        sudo("rm -r conf.d sites-available sites-enabled")

    # restart with new configuration
    sudo("service nginx restart")
