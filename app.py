# coding: utf-8

import csv
from datetime import date

import radon
from dateutil import relativedelta
from git import Repo
from radon.complexity import cc_visit
from tqdm import tqdm

import env


# Should find it
START_DATE = date.fromisoformat('2013-06-01')

FILE = env.REPO_PATH + "/src/service/NewPersonManagement.py"
FUNC_NAME = "_update_customer"

OUTPUT_FILE = "results.csv"


def prepare_command(commit_date):
    str_date = commit_date.strftime("%b %d %Y")
    cmd = ['git', 'rev-list', '-1',
           '--before="{}"'.format(str_date),
           'master', '--format=oneline']
    return cmd


repo = Repo(env.REPO_PATH)
g = repo.git


def get_commits(granularity="months"):
    assert granularity in ("months",)
    commits = []
    x_date = START_DATE
    print("Getting commits list")
    while x_date < date.today():
        cmd = prepare_command(x_date)
        res = g.execute(cmd)
        commits.append((x_date, res.split()[0]))
        x_date = x_date + relativedelta.relativedelta(months=1, day=1)
    return commits


def analyze_method(name, filename, commits):
    res = []
    print("Analyzing method")
    for c in tqdm(commits):
        g.execute(['git', 'checkout', c[1]])
        try:
            with open(filename) as f:
                code = f.read()
            r = cc_visit(code)  # Will raise SyntaxError if can't parse AST (invalid code has been pushed)
            if isinstance(r[0], radon.visitors.Class):
                method = next(m for m in r[0].methods if m.name == name)
            elif isinstance(r[0], radon.visitors.Function):
                method = next(f for f in r if f.name == name)
            res.append((c[0], method.complexity))
        except (FileNotFoundError, StopIteration, SyntaxError):
            res.append((c[0], "--"))
    return res


def result_to_csv(commits, filename):
    with open(filename, "w") as f:
        writer = csv.DictWriter(f, fieldnames=("date", "complexity"))
        writer.writeheader()
        for c in commits:
            writer.writerow({"date": c[0].strftime("%Y-%m-%d"), "complexity": c[1]})


def make_analysis(func_name, filename):
    g.execute(['git', 'checkout', 'master'])
    commits = get_commits()
    results = analyze_method(func_name, filename, commits)
    result_to_csv(results, func_name + ".csv")
    g.execute(['git', 'checkout', 'master'])


# make_analysis("_update_user", env.REPO_PATH + "/src/service/PersonManagement.py")
