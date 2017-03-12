''' Tiny test framework or just methods execution
    example:
    test_flow = TestFlow(conf_file_full_path)
    test_flow.import_actions(actions)
    if not test_flow.validate_test_data():
        print "test validation failed"
        return -1
    test_flow.execute_test()
 '''
import logging
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
            logging.error("handler not in actions")
            return False
        handler = self.actions[action_name]
        args = self.__get_args_from_step(step)
        logging.debug("Running step %s", action_name)
        return handler(*args.values())

    def __get_test_flow(self, case):
        flow = {  # defaults
            "loop": 1,
            "enable": True
        }
        flow_params = ["loop", "enable"]

        if "flow" not in case:
            return flow

        flow.update({k: v for k, v in case["flow"].iteritems() if k in flow_params})

        return flow

    def validate_test_data(self):
        ''' Vefiy test data from json fle again actions '''
        test = self.test
        scenarios = test["scenarios"]
        for scenario in scenarios:
            name = scenario["name"]
            steps = scenario["steps"]
            for step in steps:
                logging.debug("checking step %s", step["name"])
                args = self.__get_args_from_step(step)
                step_name = step["name"]
                if step_name not in self.actions:
                    logging.error("method %s not exists in the actions dictionary from constructor", step_name)
                method = self.actions[step_name]
                if method:
                    num_of_args = len(inspect.getargspec(method)[0])

                if num_of_args != len(args):
                    logging.error("invalid args for the method: %s in scenario: %s", step_name, name)
                    logging.error("total args = %s", len(args))
                    logging.error("expected args = %s",num_of_args)
                    return False

        return True

    def __get_args_from_step(self, step):
        args = step.get("args")
        return args if args else {}

    def execute_test(self):
        ''' Start test routine '''
        test = self.test
        name = test["name"]
        logging.info("Running test %s", name)
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
            logging.info("Running scenario %s iterations number %s out of %s", name, i + 1, iterations)
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
            logging.info("Running step %s iteration number %s out of %s", name, i + 1, iterations)
            self.__dispatch(step)
