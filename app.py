# coding: utf-8

from datetime import date
from pprint import pprint

from dateutil import relativedelta
from git import Repo
from radon.complexity import cc_visit

import env


# Should find it
START_DATE = date.fromisoformat('2013-06-01')

FILE = env.REPO_PATH + "/src/service/NewPersonManagement.py"
FUNC_NAME = "_update_customer"


def prepare_command(commit_date):
    str_date = commit_date.strftime("%b %d %Y")
    cmd = ['git', 'rev-list', '-1',
           '--before="{}"'.format(str_date),
           'master', '--format=oneline']
    return cmd


repo = Repo(env.REPO_PATH)
g = repo.git


def get_commits():
    commits = []
    x_date = START_DATE
    while x_date < date.today():
        cmd = prepare_command(x_date)
        res = g.execute(cmd)
        commits.append( (x_date, res.split()[0]) )
        x_date = x_date + relativedelta.relativedelta(months=1, day=1)
    return commits


def analyze_method(commits, name):
    res = []
    for c in commits:
        g.execute(['git', 'checkout', c[1]])
        try:
            with open(FILE) as f:
                code = f.read()
            r = cc_visit(code)
            method = next(m for m in r[0].methods if m.name == name)
            res.append( (c[0].strftime("%Y-%m-%d"), method.complexity) )
        except FileNotFoundError:
            print(c[0], "No file")
        except StopIteration:
            print(c[0], "No method")
    return res

commits = get_commits()
pprint(analyze_method(commits, FUNC_NAME))

g.execute(['git', 'checkout', 'master'])
