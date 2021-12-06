import os
import subprocess
import time
import csv
import sys


# "output", "new", 10.0 ,"./cvc5-Linux", ["--sygus-active-gen=enum", "--sygus-repair-const", "--sygus-repair-const-timeout=1000", "--sygus-grammar-cons=any-const"]

# run this with the command 'python3 benchmark.py NAME LOCATION TIMEOUT COMMAND ARGS*'
# NAME 		: name of csv output file
# LOCATION 	: directory containing benchmarks
# TIMEOUT 	: timeout for each benchmark (in seconds)
# COMMAND	: command to be ran (for example to run CVC5, the command argument would be './cvc5-Linux')
# ARGS		: any number of arguments to modify the command being benchmarked

class Portfolio:
    def __init__(self, path, name, parent=None):
        self.path = path
        self.name = name
        self.parent = parent

        self.problems = []
        self.subPortfolios = []
        self.directory = os.path.join(self.path, self.name)
        print(self.directory)
        self.populate()

    # populate self.folders with folders found within path & add all Sygus tasks found within path
    def populate(self):
        for dirpath, dirnames, filenames in os.walk(self.directory):
            print(dirpath)
            for new_dir in dirnames:
                new_portfolio = Portfolio(self.directory, new_dir, self)
                self.subPortfolios.append(new_portfolio)

            for name in filenames:
                if name[-3:] == '.sl':
                    new_problem = Problem(name, os.path.join(self.path, name))
                    self.problems.append(new_problem)
            break


class Problem:
    def __init__(self, name, directory):
        self.name = name
        self.directory = directory
        # 0 = Not started, 1 = In progress, 2 = Failed, 3 = Success
        self.status = 0


def main(name, loc, timeout, command, args):
    with open((name + ".csv"), 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["dir", "pass", "time", "func"])
        # Directectory of command
        cwd = os.getcwd()
        # Command to run

        portfolio = Portfolio(cwd, loc)
        print("Running now...")

        s, f = runPortfolio(portfolio, timeout, command, writer, args)
        print(s, f)
        print("\n\ndone!")


def runPortfolio(portfolio, timeout_n, command, writer, args):
    sygusStart = "(define-fun "
    completed = 0
    failed = 0

    for problem in portfolio.problems:
        timer = time.perf_counter()
        output = "Timed out"
        print(".")
        try:
            problem_dir = os.path.join(portfolio.directory, problem.name)
            proccess_args = [command, problem_dir] + args
            process = subprocess.run(proccess_args, stdout=subprocess.PIPE, timeout=timeout_n)
            output = process.stdout.decode()
            # print(output, "!")
            if sygusStart in output:
                completed += 1
                writer.writerow([problem_dir, 1, time.perf_counter() - timer, output])
            else:
                failed += 1
                writer.writerow([problem_dir, 0, time.perf_counter() - timer, output])
        except:
            failed += 1
            writer.writerow([problem_dir, 0, time.perf_counter() - timer, "Timed out"])

    for subPortfolios in portfolio.subPortfolios:
        new_completed, new_failed = runPortfolio(subPortfolios, timeout_n, command, writer, args)
        completed += new_completed
        failed += new_failed

    print("\n", portfolio.name, completed, failed)
    return completed, failed


argv = sys.argv[1:]
name = argv[0]
loc = argv[1]
timeout = float(argv[2])
command = argv[3]
args = argv[4:]
if args == None:
    args = []

main(name, loc, timeout, command, args)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
