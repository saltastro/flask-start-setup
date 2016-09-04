import os
import tempfile
import time

from fabric.api import local, env, run, sudo

from config import Config

# get remote host and username
prefix = Config.environment_variable_prefix()
host = os.environ[prefix + 'DEPLOY_HOST']
username = os.environ[prefix + 'DEPLOY_USERNAME']
repository = os.environ[prefix + 'DEPLOY_GIT_REPOSITORY']
app_dir_name = os.environ[prefix + 'DEPLOY_APP_DIR_NAME']
web_user = os.environ[prefix + 'DEPLOY_WEB_USER']
web_user_group = os.environ[prefix + 'DEPLOY_WEB_USER_GROUP']
domain_name = os.environ.get(prefix + 'DEPLOY_DOMAIN_NAME', host)

site_dir = '$HOME/' + app_dir_name

env.hosts = ['{username}@{host}'.format(username=username, host=host)]


def upgrade_libs():
    sudo('apt-get update')
    sudo('apt-get upgrade')


def update_supervisor():
    tmp_supervisor_conf = '/tmp/supervisor.{timestamp}.conf'.format(timestamp=time.time())
    sudo('sed s=---SITE_PATH---={site_dir}= {site_dir}/supervisor.conf > {tmp_supervisor_conf}'.format(
        site_dir=site_dir, tmp_supervisor_conf=tmp_supervisor_conf))
    sudo('sed s=---WEB_USER---={web_user}= {tmp_supervisor_conf} > /etc/supervisor/conf.d/supervisor.conf'.format(
        web_user=web_user, tmp_supervisor_conf=tmp_supervisor_conf))
    sudo('service supervisor restart')


def update_nginx_conf():
    static_dir = site_dir + '/app/static'
    sudo('sed s=---DOMAIN_NAME---={domain_name}= {site_dir}/nginx.conf | sed s=---STATIC_DIR---={static_dir}= '
         '> /etc/nginx/sites-available/{domain_name}'.format(domain_name=domain_name,
                                                             site_dir=site_dir,
                                                             static_dir=static_dir))
    sudo('ln -sf /etc/nginx/sites-available/{domain_name} /etc/nginx/sites-enabled/{domain_name}')
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
        local('scp {path} {username}@{host}:{tmp_env_file}'.format(username=username,
                                                                          host=host,
                                                                          path=f.name,
                                                                          site_dir=site_dir,
                                                                          tmp_env_file=tmp_env_file))
    env_file = '{site_dir}/.env'.format(site_dir=site_dir)
    run('mv {tmp_env_file} {env_file}'.format(tmp_env_file=tmp_env_file, env_file=env_file))
    run('chmod 640 {env_file}'.format(env_file=env_file))
    sudo('chown {username}:{web_user_group} {env_file}'.format(username=username,
                                                               web_user_group=web_user_group,
                                                               env_file=env_file))
    run('grep -Fxq ".env" {exclude_file}\n'
        'if [[ $? = 0 ]]\n'
        'then\n'
        '    echo .env >> {exclude_file}\n'
        'fi'.format(exclude_file=site_dir + '/.git/info/exclude'))


def update_log_dir():
    """Update the log directory.

    The directory for the log files is created (if it doesn't exist yet), access is granted tto the user only, and
     ownership of this file is transferred to the web user.
    """

    settings = Config.settings('production')
    log_dir = os.path.abspath(os.path.join(settings['logging_file_base_path'], os.path.pardir))
    sudo('if [[ ! -d {log_dir} ]]\n'
         'then\n'
         '    mkdir {log_dir}\n'
         'fi'.format(log_dir=log_dir))
    sudo('chmod 700 {log_dir}'.format(log_dir=log_dir))
    sudo('chown {web_user}:{web_user_group} {log_dir}'.format(web_user=web_user,
                                                              web_user_group=web_user_group,
                                                              log_dir=log_dir))

def setup():
    """Setup the remote server.

    You should only have to call this task once, but re-running it should cause no problems.
    """

    # nginx should be installed from the nginx site
    # hence we have to add this site to the list of apt sources
    print('Please enter the release name of the remote server\'s Ubuntu version '
          '(such "trusty" for 14.04 or "xenial" for 16.04')
    ubuntu_release = input('> ')
    deb = 'deb http://nginx.org/packages/ubuntu/ {release} nginx'.format(release=ubuntu_release)
    deb_src = 'deb-src http://nginx.org/packages/ubuntu/ {release} nginx'.format(release=ubuntu_release)
    apt_src_list = '/etc/apt/sources.list'
    sudo('grep -Fxq "{deb}" {apt_src_list}\n'
         'if [[ $? != 0 ]]\n'
         'then\n'
         '    echo >> {apt_src_list}\n'
         '    echo "# nginx" >> {apt_src_list}\n'
         '    echo "{deb}" >> {apt_src_list}\n'
         'fi'.format(deb=deb, apt_src_list=apt_src_list))
    sudo('grep -Fxq "{deb_src}" {apt_src_list}\n'
         'if [[ $? != 0 ]]\n'
         'then\n'
         '    echo "{deb_src}" >> {apt_src_list}\n'
         'fi'.format(deb_src=deb_src, apt_src_list=apt_src_list))

    # make sure the nginx packages can be validated
    run('wget http://nginx.org/keys/nginx_signing.key')
    sudo('apt-key add nginx_signing.key')
    run('rm nginx_signing.key')

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

    # supervisor
    sudo('apt-get install -y supervisor')

    # clone the repository (if it doesn't exist yet)
    run('if [[ ! -d {site_dir} ]]\n'
        'then\n'
        '    git clone {repository} {site_dir}\n'
        'fi'.format(repository=repository, site_dir=site_dir))

    # create environment variable prefix file
    run('cd {site_dir}; echo {prefix} > env_var_prefix'.format(prefix=prefix, site_dir=site_dir))

    # create a virtual environment (if it doesn't exist yet)
    run('cd {site_dir}\n'
        'if [[ ! -d venv ]]\n'
        'then\n'
        '    python3 -m virtualenv venv\n'
        'fi'.format(site_dir=site_dir))

    # install Python libraries
    run('cd {site_dir}\n'
        'source venv/bin/activate\n'
        'pip install -r requirements.txt\n'
        'deactivate'.format(site_dir=site_dir))

    # setup the environment variables file
    # this must happen before Supervisor or Nginx are updated
    update_environment_variables_file()

    # setup the log directory
    # this must happen before Supervisor or Nginx are updated
    update_log_dir()

    # setup Supervisor
    update_supervisor()

    # setup Nginx
    update_nginx_conf()


def deploy():
    # update the Git repository
    run('cd {site_dir}; git pull'.format(site_dir=site_dir))

    # install Python libraries
    run('cd {site_dir}\n'
        'source venv/bin/activate\n'
        'pip install -r requirements.txt\n'
        'deactivate'.format(site_dir=site_dir))

    # update the environment variables file
    # this must happen before Supervisor or Nginx are updated
    update_environment_variables_file()

    # update the log directory
    # this must happen before Supervisor or Nginx are updated
    update_log_dir()

    # update Supervisor
    update_supervisor()

    # update Nginx
    update_nginx_conf()
