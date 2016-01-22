from errbot import BotPlugin, botcmd
from errbot.templating import tenv
import subprocess, os.path
import paramiko,time

class Migrate(BotPlugin):
    """Use paramiko to connect remote server"""
    def remote_excute(self, script):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect('10.10.0.3', username="root", password="_aoO1CBaYbshr1VS_LGh",timeout=60)
        #client.connect('10.6.15.109', username='root', password='58mfJGsv#q@4')
        sleeptime = 0.001
        outdata, errdata = '', ''
        ssh_transp = client.get_transport()
        chan = ssh_transp.open_session()
        # chan.settimeout(3 * 60 * 60)
        chan.setblocking(0)
        chan.exec_command(script)
        while True:  # monitoring process
            # Reading from output streams
            while chan.recv_ready():
                outdata += chan.recv(1000)
            while chan.recv_stderr_ready():
                errdata += chan.recv_stderr(1000)
            if chan.exit_status_ready():  # If completed
                break
            time.sleep(sleeptime)
        res = chan.recv_exit_status()
        ssh_transp.close()

        #print(outdata)
        #print(errdata)
        return res
      
    @botcmd(split_args_with=None, template="migrate")
    def migrate(self, msg, args):
        """Migrate Storage from 7mode to BBCS"""
        user = args.pop(0)
        environment = args.pop(0)
        numbers = args.pop(0)
        nfs = args.pop(0)

        script =  "/root/stephen/storage_migrations/migrate-env-atu.sh" + " -u " + user + " -e " + environment + " -n " + numbers + " -s " + nfs
        #script = "/opt/chef/embedded/bin/ruby /usr/bin/chef-client -d -c /etc/chef/client.rb -L /var/log/chef/client.log -P /var/run/chef/client.pid -i 3600 -s 600 --fork"


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
 
        script = '/root/stephen/storage_migrations/start-env-atu.sh' + " -e " + environment + " -n " + numbers + " -d " + dc + " -s " + datastore
        #script = "/opt/chef/embedded/bin/ruby /usr/bin/chef-client -d -c /etc/chef/client.rb -L /var/log/chef/client.log -P /var/run/chef/client.pid -i 3600 -s 600 --fork"
        res = self.remote_excute(script)
        if res == 0:
            response = tenv().get_template('start.md').render(environment=environment)
        else:
            response = "Err....Something went wrong"
        self.send(msg.frm, response, message_type=msg.type)
