import os
import json
import argparse
import numpy as np

from parsec import algorithm
from datetime import datetime
from multiprocessing import Pool
from parsec.process_user_input import ProcessInput

# Setup argparse
_parser = argparse.ArgumentParser(description='Run feedback tests automatically')
_parser.add_argument('-t', action='store', dest='test', type=str, metavar='test', default='tree_nlp', help='The test type to run (nlp/tree/tree_nlp)')
_parser.add_argument('-d', action='store', dest='data', type=str, metavar='data', default='basic', help='Data to run (basic/handover/pour/cleaning/rl)')
_parser.add_argument('-o', action='store', dest='output', type=str, metavar='output', default='../output', help='Output directory for results')
_parser.add_argument('-c', action='store', dest='config', type=str, metavar='config', default='../config/cclfd', help='Configuration directory (prebuilt: ../config/cclfd and ../config/rl)')
_parser.add_argument('-n', action='store', dest='num_tests', type=int, metavar='num_tests', default=10, help='Number of tests to run')

_CONSTRAINTS_FILE = '/dictionaries.yml'


def run(test_type, num_tests, data, output_dir, config_dir):
    # Setup variables and data
    with open(config_dir + "/data/" + data + ".json") as json_file:
        faults = json.load(json_file)['faults']
    num_explanations = len(faults)

    # Run test using test helper
    print("Running {} tests...".format(test_type))

    # Create word processor
    processor = ProcessInput(config_dir + _CONSTRAINTS_FILE)
    processor.build_dicts()

    # Collect data from tests
    data_from_tests = []
    num_proc = 10
    for i in range(0, num_tests):
        p = Pool(processes=num_proc)
        new_data = p.map(algorithm.run, [(processor, "auto", output_dir, config_dir, faults, test_type) for j in range(num_proc)])
        data_from_tests.extend(new_data)
        p.close()
        print("Finished: {}/{}".format((i + 1) * num_proc, num_tests * num_proc))

    # Convert data into 2D array
    results = [[] for i in range(0, num_explanations)]
    for entry in data_from_tests:
        for key, value in entry.items():
            results[key - 1].append(value['count'])
    results = np.array(results).T.tolist()

    # Make sure directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Open results file
    now = datetime.now()
    timestr = now.strftime("_%m-%d-%Y_%H-%M-%S")
    file_name = '/' + test_type + timestr + '.csv'
    results_file = open(output_dir + file_name, "w")

    # Write results to file
    for row in results:
        line = str(row)[1:-1]
        results_file.write(line + "\n")

    # Close file
    results_file.close()
    print("---- FINISHED ----")


if __name__ == "__main__":
    # Read arguments
    args = _parser.parse_args()

    # Run all cases in a loop
    run(args.test, args.num_tests, args.data, args.output, args.config)
