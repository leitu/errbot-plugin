from errbot import BotPlugin, botcmd
from errbot.templating import tenv
import subprocess, os.path
import paramiko

class Migrate(BotPlugin):
    """Use paramiko to connect remote server"""
    def remote_excute(self, script, remote_server='10.10.0.3', username="root", password="_aoO1CBaYbshr1VS_LGh"):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(remote_server, username, password)
        stdin, stdout, stderr = client.exec_command(script)
        res = stdout.channel.recv_exit_status()
        stdin.close()
        return res
      
    @botcmd(split_args_with=None, template="migrate")
    def migrate(self, msg, args):
        """Migrate Storage from 7mode to BBCS"""
        user = args.pop(0)
        environment = args.pop(0)
        numbers = args.pop(0)
        nfs = args.pop(0)

        script =  "/root/stephen/storage_migrations/migrate-env-atu.sh" + " " + user + " " + environment + " " + numbers + " " + nfs

        res = self.remote_excute(script)
        if res == 0:
            response = tenv().get_template('migrate.md').render(environment=environment)
        else:
            response = "Err...Something went wrong"
        self.send(msg.frm, response, message_type=msg.type)

    @botcmd(split_args_with=None, template="start")
    def startvmotion(self, msg, args):
        """vMotion from 7mode datastore to bbcs datastore"""
        environment = args.pop(0)
        numbers = args.pop(0)
        dc = args.pop(0)
        datastore = args.pop(0)
 
        script = '/root/stephen/storage_migrations/start-env-atu.sh' + " " + environment + " " + numbers + " " + dc + " " + datastore
        res = self.remote_excute(script)
        if res == 0:
            response = tenv().get_template('start.md').render(environment=environment)
        else:
            response = "Err....Something went wrong"
        self.send(msg.frm, response, message_type=msg.type)
