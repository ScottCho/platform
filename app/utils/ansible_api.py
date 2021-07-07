#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
import shutil
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible import context
import ansible.constants as C
from app import redis_cli

# redis_cli = redis.StrictRedis(host="192.168.0.12", port=6379, db=0)

# since the API is constructed for CLI it expects certain options to always be set in the context object
context.CLIARGS = ImmutableDict(connection='paramiko_ssh',
                                module_path=[],
                                forks=10,
                                become=None,
                                become_method=None,
                                become_user=None,
                                check=False,
                                diff=False,
                                syntax=False,
                                start_at_task=None)


class ResultCallback(CallbackBase):
    def __init__(self, *args, **kwargs):
        super(ResultCallback, self).__init__(*args, **kwargs)

    def v2_runner_on_ok(self, result, **kwargs):
        """Print a json representation of the result

        This method could store the result in an instance attribute for retrieval later
        """
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))
        return json.dumps({host.name: result._result}, indent=4)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        host = result._host.get_name()
        print(json.dumps({host.name: result._result}, indent=4))

    def v2_runner_on_unreachable(self, result, ignore_errors=False):
        host = result._host.get_name()
        print(json.dumps({host.name: result._result}, indent=4))


class PlayBookResultCallback(CallbackBase):
    def __init__(self, redis_key_prefix, task_id, *args, **kwargs):
        super(PlayBookResultCallback, self).__init__(*args, **kwargs)
        self.task_name = ''
        self.key = "{}::{}".format(redis_key_prefix, task_id)

    def v2_runner_on_ok(self, result, *args, **kwargs):

        if not self.task_name:
            self.task_name = result._task_fields['name']
            redis_cli.append(
                self.key, "Task [{0}]{1}\n".format(result._task_fields['name'],
                                                   '*' * 80))

        if self.task_name != result._task_fields['name']:
            self.task_name = result._task_fields['name']
            redis_cli.append(
                self.key,
                "\nTask [{0}]{1}\n".format(result._task_fields['name'],
                                           '*' * 80))

        state = 'changed' if result._result.get('changed') else 'ok'
        redis_cli.append(self.key,
                         "{0}: [{1}]\n".format(state, result._host.get_name()))

    def v2_runner_on_failed(self, result, *args, **kwargs):
        if not self.task_name or self.task_name != result._task_fields['name']:
            self.task_name = result._task_fields['name']
            redis_cli.append(
                self.key, "Task [{0}]{1}\n".format(result._task_fields['name'],
                                                   '*' * 80))
        redis_cli.append(
            self.key, "fatal: [{0}]: FAILED! => {1}\n\n  ".format(
                result._host.get_name(), result._result))

    def v2_runner_on_unreachable(self, result):
        if not self.task_name or self.task_name != result._task_fields['name']:
            self.task_name = result._task_fields['name']
            redis_cli.append(
                self.key, "Task [{0}]\n".format(result._task_fields['name']))
        redis_cli.append(self.key,
                         "unreachable: [{0}]".format(result._host.get_name()))

    def v2_runner_on_skipped(self, result):
        if not self.task_name or self.task_name != result._task_fields['name']:
            self.task_name = result._task_fields['name']
            redis_cli.append(
                self.key, "Task [{0}]\n".format(result._task_fields['name']))
        redis_cli.append(self.key,
                         "skipped: [{0}]".format(result._host.get_name()))

    def v2_playbook_on_stats(self, stats):
        redis_cli.append(self.key, '\nPLAY RECAP{}\n'.format('*' * 80))
        hosts = sorted(stats.processed.keys())
        for h in hosts:
            t = stats.summarize(h)
            redis_cli.append(self.key, '{:20s}: {}\n'.format(h, t))


# hosts为单个IP或者数组
def exec_shell(hosts, module_name, module_args, sources='/etc/ansible/hosts'):

    # Instantiate our ResultCallback for handling results as they come in. Ansible expects this to be one of its main display outlets
    results_callback = ResultCallback()

    # Takes care of finding and reading yaml, json and ini files
    loader = DataLoader()

    # variable manager takes care of merging all the different sources to give you a unified view of variables available in each context
    inventory = InventoryManager(loader=loader, sources=sources)

    # variable manager takes care of merging all the different sources to give you a unified view of variables available in each context
    variable_manager = VariableManager(loader=loader, inventory=inventory)

    # create data structure that represents our play, including tasks, this is basically what our YAML loader does internally.
    play_source = dict(
        name="Ansible Play",
        hosts=hosts,
        gather_facts='no',
        tasks=[
            dict(action=dict(module=module_name, args=module_args),
                 register='shell_out'),
            dict(action=dict(module='debug',
                             args=dict(msg='{{shell_out.stdout}}')))
        ])
    # Create play object, playbook objects use .load instead of init or new methods,
    # this will also automatically create the task objects from the info provided in play_source
    play = Play().load(play_source,
                       variable_manager=variable_manager,
                       loader=loader)

    # Run it - instantiate task queue manager, which takes care of forking and setting up all objects to iterate over host list and tasks
    tqm = None
    try:
        tqm = TaskQueueManager(
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            passwords=dict(vault_pass='secret'),
            stdout_callback=
            results_callback,  # Use our custom callback instead of the ``default`` callback plugin, which prints to stdout
        )
        result = tqm.run(
            play
        )  # most interesting data for a play is actually sent to the callback's methods
    finally:
        # we always need to cleanup child procs and the structures we use to communicate with them
        if tqm is not None:
            tqm.cleanup()

        # Remove ansible tmpdir
        shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)


def ansible_playbook(redis_key_prefix,
                     task_id,
                     playbook_path,
                     extra_vars=None,
                     sources='/etc/ansible/hosts'):
    results_callback = PlayBookResultCallback(redis_key_prefix, task_id)
    loader = DataLoader()
    inventory = InventoryManager(loader=loader, sources=sources)
    variable_manager = VariableManager(loader=loader, inventory=inventory)

    executor = PlaybookExecutor(playbooks=[playbook_path],
                                inventory=inventory,
                                variable_manager=variable_manager,
                                loader=loader,
                                passwords=dict(vault_pass='secret'))

    executor._tqm._stdout_callback = results_callback
    C.HOTS_KEY_CHECKING = False
    result = executor.run()


if __name__ == '__main__':
    exec_shell(['192.168.0.10', '192.168.0.31'], 'shell', 'echo hello')
    ansible_playbook('ansible', 2, '/etc/ansible/playbook/nginx_playbook.yml')
