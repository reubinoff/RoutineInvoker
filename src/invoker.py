''' Tiny test framework or just methods execution
    example:
    test_flow = TestFlow(conf_file_full_path)
    test_flow.import_actions(actions)
    if not test_flow.validate_test_data():
        print "test validation failed"
        return -1
    test_flow.execute_test()
 '''

import json
import inspect

class TestFlow(object):
    ''' Test framework '''
    def __init__(self, conf_file_path):
        self.actions = {}
        with open(conf_file_path) as data_file:
            data = json.load(data_file)
            self.test = data["test"]

    def import_actions(self, import_actions):
        ''' get dictonary of method name against method handler '''
        self.actions = import_actions

    def __dispatch(self, step):
        ''' invoke step '''
        action_name = step["name"]
        if action_name not in self.actions:
            print "error >> handler not in actions"
            return False
        handler = self.actions[action_name]
        args = self.__get_args_from_step(step)
        print " running step {}".format(action_name)
        return handler(*args.values())

    def __get_test_flow(self, case):
        flow = {  # defaults
            "loop": 1,
            "enable": True
        }
        flow_params = ["loop"]
        if "flow" not in case:
            return flow

        raw_flow = case["flow"]

        for param in [param for param in flow_params if param in raw_flow]:
            flow[param] = raw_flow[param]

        return flow

    def validate_test_data(self):
        ''' Vefiy test data from json fle again actions '''
        test = self.test
        scenarios = test["scenarios"]
        for scenario in scenarios:
            name = scenario["name"]
            steps = scenario["steps"]
            for step in steps:
                print "checking step {}".format(step["name"])
                args = self.__get_args_from_step(step)
                step_name = step["name"]
                method = self.actions[step_name]
                if method:
                    num_of_args = len(inspect.getargspec(method)[0])

                if num_of_args != len(args):
                    print "invalid args for the method: {} in scenario: {}".format(step_name, name)
                    print "total args = {}".format(len(args))
                    print "expected args = {}".format(num_of_args)
                    return False

        return True

    def __get_args_from_step(self, step):
        if "args" in step:
            args = step["args"]
        else:
            args = {}
        return args

    def execute_test(self):
        ''' Start test routine '''
        test = self.test
        name = test["name"]
        print "Running test {}".format(name)
        if "scenarios" in test:
            scenarios = test["scenarios"]
            for scenario in scenarios:
                self.__execute_scenario(scenario)

    def __execute_scenario(self, scenario):
        flow = self.__get_test_flow(scenario)
        iterations = flow['loop']
        enable = flow['enable']
        if not enable:
            return
        for i in range(0, iterations):
            name = scenario["name"]
            print "Running scenario {} iterations number {} out of {}".format(name,
                                                                              i + 1, iterations)
            if "steps" not in scenario:
                continue
            steps = scenario["steps"]
            for step in steps:
                self.__execute_step(step)

    def __execute_step(self, step):
        flow = self.__get_test_flow(step)
        iterations = flow['loop']
        for i in range(0, iterations):
            name = step["name"]
            print "Running step {} iteration number {} out of {}".format(name, i + 1, iterations)
            self.__dispatch(step)
