import os
import tempfile
import jinja2
import fabric.api


def render(file, **kwargs):
    with open(file, "r") as s, tempfile.NamedTemporaryFile("w", delete=False) as d:
        d.write(jinja2.Template(s.read()).render(kwargs))
        return d.name


def tput(local_path=None, remote_path=None, use_sudo=None, mirror_local_mode=False, mode=None, **kwargs):
    if not remote_path:
        remote_path = local_path

    # render jinja2 template if exists
    template_path = os.path.join(fabric.api.env.lcwd, local_path + ".jinja2")
    if os.access(template_path, os.R_OK):
        local_path = render(template_path, **kwargs)
    elif not os.access(os.path.join(fabric.api.env.lcwd, local_path), os.R_OK):
        return False

    # automatically check for sudo is necessary
    if use_sudo is None:
        use_sudo = os.path.join(fabric.api.env.cwd, remote_path)[:6] != "/home/"

    # fix fabric bug when use_sudo and mode arguments is defined at same time
    if use_sudo and mode:
        result = fabric.api.put(local_path, remote_path, use_sudo, mirror_local_mode)
        fabric.api.sudo('chmod %o "%s"' % (mode, remote_path))
        return result

    return fabric.api.put(local_path, remote_path, use_sudo, mirror_local_mode, mode)
