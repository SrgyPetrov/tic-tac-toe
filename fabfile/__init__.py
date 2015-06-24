import os
from fabric.api import *
from deploy import vps


env.dir = os.path.abspath(os.path.dirname(__file__))
env.repo_dir = os.path.normpath(os.path.join(env.dir, '..'))
env.templates_dir = os.path.join(env.dir, 'templates')
env.crontab_template = os.path.join(env.templates_dir, 'crontab')
env.cookbooks_version = '0.3.7'


@task
def production():
    env.user = 'project'
    env.lemon_env = 'production'
    env.branch = 'master'
    env.hosts = ['188.226.193.98']
