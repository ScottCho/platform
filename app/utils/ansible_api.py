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
import redis

redis_cli = redis.StrictRedis(host="192.168.0.12", port=6379, db=0)


# since the API is constructed for CLI it expects certain options to always be set in the context object
context.CLIARGS = ImmutableDict(connection='paramiko_ssh', module_path=[], forks=10, become=None,
                                become_method=None, become_user=None, check=False, diff=False, syntax=False,start_at_task=None)

class ResultCallback(CallbackBase):
    def __init__(self, *args, **kwargs):
        super(ResultCallback, self).__init__(*args, **kwargs)
   
    def v2_runner_on_ok(self, result, **kwargs):
        """Print a json representation of the result

        This method could store the result in an instance attribute for retrieval later
        """
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))


    def v2_runner_on_failed(self, result, ignore_errors=False):
        host = result._host.get_name()
        print(json.dumps({host.name: result._result}, indent=4))

    def v2_runner_on_unreachable(self, result, ignore_errors=False):
        host = result._host.get_name()
        print(json.dumps({host.name: result._result}, indent=4))

    
class PlayBookResultCallback(CallbackBase):

    def __init__(self, redis_key_prefix,  task_id, *args, **kwargs):
        super(PlayBookResultCallback, self).__init__(*args, **kwargs)
        self.task_name = ''
        self.key = "{}::{}".format(redis_key_prefix,task_id)

   
    def v2_runner_on_ok(self, result, *args, **kwargs):
         
        if not self.task_name:
            self.task_name = result._task_fields['name']
            redis_cli.append(self.key, "Task [{0}]{1}\n".format(result._task_fields['name'],'*' * 80))

        if self.task_name != result._task_fields['name']:
            self.task_name = result._task_fields['name']
            redis_cli.append(self.key, "\nTask [{0}]{1}\n".format(result._task_fields['name'],'*' * 80))
        
        state = 'changed' if result._result.get('changed') else 'ok'
        redis_cli.append(self.key, "{0}: [{1}]\n".format(state, result._host.get_name()))


    def v2_runner_on_failed(self, result, *args, **kwargs):
        if not self.task_name or self.task_name != result._task_fields['name']:
            self.task_name = result._task_fields['name']
            redis_cli.append(self.key, "Task [{0}]{1}\n".format(result._task_fields['name'],'*' * 80))
        redis_cli.append(self.key, "fatal: [{0}]: FAILED! => {1}\n\n  ".format(result._host.get_name(),result._result))

    def v2_runner_on_unreachable(self, result):
        if not self.task_name or self.task_name != result._task_fields['name']:
            self.task_name = result._task_fields['name']
            redis_cli.append(self.key, "Task [{0}]\n".format(result._task_fields['name']))
        redis_cli.append(self.key, "unreachable: [{0}]".format(result._host.get_name()))

    def v2_runner_on_skipped(self, result):
        if not self.task_name or self.task_name != result._task_fields['name']:
            self.task_name = result._task_fields['name']
            redis_cli.append(self.key, "Task [{0}]\n".format(result._task_fields['name']))
        redis_cli.append(self.key, "skipped: [{0}]".format(result._host.get_name()))


    def v2_playbook_on_stats(self, stats):
        redis_cli.append(self.key, '\nPLAY RECAP{}\n'.format('*' * 80))
        hosts = sorted(stats.processed.keys())
        for h in hosts:
            t = stats.summarize(h)
            redis_cli.append(self.key, '{:20s}: {}\n'.format(h ,t))





 
class AnsibleTask:
    def __init__(self, sources):
        #source为以逗号分割的IP或者host配置文件路径
        self.sources = sources
        # Takes care of finding and reading yaml, json and ini files
        self.loader = DataLoader()
        self.passwords = dict(vault_pass='secret')
        # Instantiate our ResultCallback for handling results as they come in. Ansible expects this to be one of its main display outlets
        self.results_callback = None
        # create inventory, use path to host config file as source or hosts in a comma separated string
        self.inventory = InventoryManager(loader=self.loader, sources=self.sources)
        # variable manager takes care of merging all the different sources to give you a unified view of variables available in each context
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)

    def exec_shell(self, hosts, module_name, module_args):
        self.results_callback = ResultCallback()
    # create data structure that represents our play, including tasks, this is basically what our YAML loader does internally.
        play_source = dict(
            name="Ansible Play",
            hosts=hosts,
            gather_facts='no',
            tasks=[
                dict(action=dict(module=module_name, args=module_args), register='shell_out'),
                dict(action=dict(module='debug', args=dict(msg='{{shell_out.stdout}}')))
            ]
        )
        # Create play object, playbook objects use .load instead of init or new methods,
        # this will also automatically create the task objects from the info provided in play_source
        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)

        # Run it - instantiate task queue manager, which takes care of forking and setting up all objects to iterate over host list and tasks
        tqm = None
        try:
            tqm = TaskQueueManager(
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                passwords=self.passwords,
                stdout_callback=self.results_callback,  # Use our custom callback instead of the ``default`` callback plugin, which prints to stdout
            )
            result = tqm.run(play)  # most interesting data for a play is actually sent to the callback's methods
        finally:
            # we always need to cleanup child procs and the structures we use to communicate with them
            if tqm is not None:
                tqm.cleanup()

            # Remove ansible tmpdir
            shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)

    def ansible_playbook(self,redis_key_prefix, task_id, playbook_path,extra_vars=None):
        self.results_callback = PlayBookResultCallback(redis_key_prefix, task_id)
        executor = PlaybookExecutor(
            playbooks = [playbook_path],
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            passwords=self.passwords
            )

        executor._tqm._stdout_callback = self.results_callback
        C.HOTS_KEY_CHECKING = False
        result = executor.run()
        return(result)
        




if __name__ == '__main__':
    tasks = AnsibleTask('192.168.0.12,192.168.0.31')
    # tasks = AnsibleTask('/etc/ansible/hosts')
    tasks.exec_shell('192.168.0.31', 'shell', 'ls')
    #tasks.ansible_playbook('ansible',8,'/etc/ansible/roles/centos7/init.yml')

