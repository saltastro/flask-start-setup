import os
import tempfile
import time

from fabric.api import local, env, run, sudo

from config import Config

# get variables
prefix = Config.environment_variable_prefix()
host = os.environ[prefix + 'DEPLOY_HOST']
deploy_user = os.environ.get(prefix + 'DEPLOY_USER', 'deploy')
deploy_user_group = os.environ.get(prefix + 'DEPLOY_USER_GROUP', deploy_user)
repository = os.environ[prefix + 'DEPLOY_GIT_REPOSITORY']
app_dir_name = os.environ[prefix + 'DEPLOY_APP_DIR_NAME']
web_user = os.environ.get(prefix + 'DEPLOY_WEB_USER', 'www-data')
web_user_group = os.environ.get(prefix + 'DEPLOY_WEB_USER_GROUP', 'www-data')
domain_name = os.environ.get(prefix + 'DEPLOY_DOMAIN_NAME', host)
bokeh_server_port = os.environ.get(prefix + 'DEPLOY_BOKEH_SERVER_PORT', 5100)

site_dir = '$HOME/' + app_dir_name

env.hosts = ['{username}@{host}'.format(username=deploy_user, host=host)]


def upgrade_libs():
    sudo('apt-get update')
    sudo('apt-get upgrade')


def update_supervisor():
    # Python files to load into the Bokeh server
    files = [f for f in os.listdir('bokeh_server') if f.lower().endswith('.py')]

    # replace placeholders
    sed = 'sed -e" s=---SITE_PATH---={site_dir}=g"' \
          '    -e "s=---WEB_USER---={web_user}=g"' \
          '    -e "s=---HOST---={host}=g"' \
          '    -e "s=---BOKEH_SERVER_PORT---={bokeh_server_port}=g"' \
          '    -e "s=---FILES---={files}=g"' \
          '    {site_dir}/supervisor.conf '.format(
        site_dir=site_dir,
        web_user=web_user,
        host=domain_name,
        bokeh_server_port=bokeh_server_port,
        files=' '.join(files))
    sudo('{sed} > /etc/supervisor/conf.d/{domain_name}.conf'.format(
        sed=sed,
        domain_name=domain_name))
    sudo('service supervisor restart')


def update_nginx_conf():
    static_dir = site_dir + '/app/static'
    sudo('sed s=---DOMAIN_NAME---={domain_name}= {site_dir}/nginx.conf | sed s=---STATIC_DIR---={static_dir}= '
         '> /etc/nginx/sites-available/{domain_name}'.format(domain_name=domain_name,
                                                             site_dir=site_dir,
                                                             static_dir=static_dir))
    sudo('ln -sf /etc/nginx/sites-available/{domain_name} /etc/nginx/sites-enabled/{domain_name}'.format(
        domain_name=domain_name))
    sudo('service nginx restart')


def update_environment_variables_file():
    """Update the environment variables file on the server.

    The file is rendered readable to the deploy user and the web user.
    """
    settings = Config.settings('production')
    environment_variables = dict(
        DATABASE_URI=settings['database_uri'],
        LOGGING_FILE_BASE_PATH=settings['logging_file_base_path'],
        LOGGING_FILE_LOGGING_LEVEL=settings['logging_file_logging_level_name'],
        LOGGING_FILE_MAX_BYTES=settings['logging_file_max_bytes'],
        LOGGING_FILE_BACKUP_COUNT=settings['logging_file_backup_count'],
        LOGGING_MAIL_FROM_ADDRESS=settings['logging_mail_from_address'],
        LOGGING_MAIL_LOGGING_LEVEL=settings['logging_mail_logging_level_name'],
        LOGGING_MAIL_SUBJECT=settings['logging_mail_subject'],
        LOGGING_MAIL_TO_ADDRESSES=settings['logging_mail_to_addresses'],
        SECRET_KEY=settings['secret_key'],
        SSL_STATUS=settings['ssl_status']
    )
    file_content = ''
    keys = sorted(environment_variables.keys())
    for key in keys:
        file_content += '{prefix}{key}={value}\n'.format(prefix=prefix, key=key, value=environment_variables[key])
    with tempfile.NamedTemporaryFile('w') as f:
        f.write(file_content)
        f.flush()
        tmp_env_file = '/tmp/.env.{timestamp}'.format(timestamp=time.time())
        local('scp {path} {username}@{host}:{tmp_env_file}'.format(username=deploy_user,
                                                                   host=host,
                                                                   path=f.name,
                                                                   site_dir=site_dir,
                                                                   tmp_env_file=tmp_env_file))
    env_file = '{site_dir}/.env'.format(site_dir=site_dir)
    run('mv {tmp_env_file} {env_file}'.format(tmp_env_file=tmp_env_file, env_file=env_file))
    run('chmod 640 {env_file}'.format(env_file=env_file))
    sudo('chown {username}:{web_user_group} {env_file}'.format(username=deploy_user,
                                                               web_user_group=web_user_group,
                                                               env_file=env_file))


def update_log_dir():
    """Update the log directory.

    The directory for the log files is created (if it doesn't exist yet), access is granted to the user only, and
    ownership of this file is transferred to the web user.

    If the directory exists already, it is checked that it is actually owned by
    """

    settings = Config.settings('production')
    log_dir = os.path.abspath(os.path.join(settings['logging_file_base_path'], os.path.pardir))
    sudo('if [[ ! -d {log_dir} ]]\n'
         'then\n'
         '    mkdir {log_dir}\n'
         '    chmod 700 {log_dir}\n'
         '    chown {web_user}:{web_user_group} {log_dir}\n'
         'elif [ `ls -ld {log_dir} | awk \'{{print $3}}\'` != "{web_user}" ]\n'
         'then\n'
         '    echo "The directory {log_dir} for the log files isn\'t owned by the web user ({web_user})."\n'
         '    sleep 5\n'
         '    exit 1\n'
         'fi'.format(log_dir=log_dir,
                     web_user=web_user,
                     web_user_group=web_user_group))


def update_webassets():
    # remove bundle and cache directories
    static_dir = site_dir + '/app/static'
    webassets_cache = static_dir + '/.webassets-cache'
    cache = static_dir + '/cache'
    run('if [[ -d {cache} ]]\n'
        'then\n'
        '    rm -r {cache}\n'
        'fi'.format(cache=cache))
    sudo('if [[ -d {webassets_cache} ]]\n'
         'then\n'
         '    rm -r {webassets_cache}\n'
         'fi'.format(webassets_cache=webassets_cache))

    # create bundles (must be run as root, as the deploy user doesn't own the error log)
    sudo('cd {site_dir}; export FLASK_APP=run_server.py; export FLASK_CONFIG=production; venv/bin/flask assets build'
         .format(site_dir=site_dir))

    # make deploy user owner of the bundle directory
    sudo('chown -R {deploy_user}:{deploy_user_group} {cache}'
         .format(deploy_user=deploy_user,
                 deploy_user_group=deploy_user_group,
                 cache=cache))

    # make web user owner of the bundle directory
    sudo('chown -R {web_user}:{web_user_group} {webassets_cache}'
         .format(web_user=web_user,
                 web_user_group=web_user_group,
                 webassets_cache=webassets_cache))


def update_python_packages():
    run('cd {site_dir}\n'
        'source venv/bin/activate\n'
        'pip install -r requirements.txt\n'
        'deactivate'
        .format(site_dir=site_dir))


def setup():
    """Setup the remote server.

    You should only have to call this task once, but re-running it should cause no problems.
    """

    # test everything
    local('./run_tests.sh')

    # push Git content to the remote repository
    local('git push')

    # upgrade/update apt
    upgrade_libs()

    # necessary to install many Python libraries
    sudo('apt-get install -y build-essential')
    sudo('apt-get install -y git')
    sudo('apt-get install -y python3')
    sudo('apt-get install -y python3-pip')
    sudo('apt-get install -y python3-all-dev')

    # enable virtual environments
    sudo('pip3 install virtualenv')

    # MySQL
    sudo('apt-get install -y mysql-client')
    sudo('apt-get install -y libmysqlclient-dev')

    # Java
    sudo('apt-get install -y default-jre')

    # supervisor
    sudo('apt-get install -y supervisor')

    # nginx
    sudo('apt-get install -y nginx')

    # clone the Git repository (if it doesn't exist yet)
    run('if [[ ! -d {site_dir} ]]\n'
        'then\n'
        '    git clone {repository} {site_dir}\n'
        'fi'.format(repository=repository, site_dir=site_dir))

    # update the Git repository
    run('cd {site_dir}; git pull'.format(site_dir=site_dir))

    # create environment variable prefix file
    run('cd {site_dir}; echo {prefix} > env_var_prefix'.format(prefix=prefix, site_dir=site_dir))

    # create a virtual environment (if it doesn't exist yet)
    run('cd {site_dir}\n'
        'if [[ ! -d venv ]]\n'
        'then\n'
        '    python3 -m virtualenv venv\n'
        'fi'.format(site_dir=site_dir))
    # install Python packages
    update_python_packages()

    # setup the environment variables file
    # this must happen before Supervisor or Nginx are updated
    update_environment_variables_file()

    # setup the log directory
    # this must happen before Supervisor or Nginx are updated
    update_log_dir()

    # create static file bundles
    update_webassets()

    # setup Supervisor
    update_supervisor()

    # setup Nginx
    update_nginx_conf()


def deploy():
    """Deploy the app to the remote server.
    """

    # test everything
    local('./run_tests.sh')

    # push Git content to the remote repository
    local('git push')

    # update the Git repository
    run('cd {site_dir}; git pull'.format(site_dir=site_dir))

    # install Python packages
    update_python_packages()

    # update the environment variables file
    # this must happen before Supervisor or Nginx are updated
    update_environment_variables_file()

    # update the log directory
    # this must happen before Supervisor or Nginx are updated
    update_log_dir()

    # update static file bundles
    update_webassets()

    # update Supervisor
    update_supervisor()

    # update Nginx
    update_nginx_conf()


def reboot():
    """Reboot the remote server.
    """

    sudo('reboot')
