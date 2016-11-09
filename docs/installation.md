# Installation

## On your machine for development

Download the content of the repository as a zip file and extract the file into a directory of your choice. Don't clone the repository, unless you are actually planning to update the start setup rather than to create a new Flask site.

You should then put the new directory (let's call it `/path/to/site`) under version control.

```bash
cd /path/to/site
git init
```

Make sure you've installed [Java](http://www.oracle.com/technetwork/java/javase/downloads/index-jsp-138363.html) (required for building bundles of static files with Flask-Assets) and Python 3. Create a virtual environment

```bash
python3 -m venv venv
```

and then install the required Python libraries,

```bash
source venv/bin/activate
pip install -r requirements.txt
```

Create a file `env_var_prefix` which contains a single line with the prefix to use for the environment variables (such as `FSS`). 

Define the required environment variables, as set out in the section [Environment variables](environment-variables.md) below. (If you are using an IDE, you might define these in your running configuration.)

If you are planning to use it, you also need to install [Flyway](https://flywaydb.org) on your machine. Otherwise you have to set the environment variable `<PREFIX>_DB_MIGRATION_TOOL` (with the prefix defined in `env_var_prefix`) to another tool, or `None`. See the Database section below.

You can download its command-line tool from [https://flywaydb.org/getstarted/download](https://flywaydb.org/getstarted/download). As Java is on your machine already (at least if you've followed the instructions so far), you may download the version without JRE.

Extract the downloaded file in a suitable location of your choice (`/path/to/Flyway`, say). Then you can define a command `flyway` by defining an alias in your Bash configuration.

```bash
alias flyway='/path/to/Flyway/flyway'
```

As this alias won't be used by Flask, you might also need to set an environment variable `<PREFIX>_DB_MIGRATION_COMMAND` (with the prefix defined in `env_var_prefix`) to the path to the Flyway script.

```bash
export <PREFIX>_DB_MIGRATION_FLYWAY_COMMAND='/path/to/Flyway/flyway'
```

Finally, you should modify the `README.md` file as required, and add a `LICENSE.txt` file.

## On a remote server

**Important:** When the site is deployed, a file `.env` is created, which contains settings which must be kept secret. **Ensure that this file is not put under version control.**

Ubuntu 14.04 or higher must be running on the remote server, and standard commands like`ssh` must be installed. The server should not be used for anything other than running the deployed website.

Create a user `deploy` for deploying the site, and give that user sudo permissions:

```bash
adduser deploy
gpasswd -a deploy sudo
```

You may choose another username for this user, but then you have to set the `<PREFIX>_SERVER_USERNAME` environment variable accordingly. See the [section on environment variables](environment-variables.md) for an explanation of the prefix.

Make sure wget is installed on the server.

Login as the deploy user.

Unless your repository has public access, you should also generate an SSL key for the deploy user. Check whether there is a file `~/.ssh/id_rsa.pub` already. If there isn't, create a new public key by running

```bash
ssh-keygen
```

If you don't choose the default file location, you'll have to modify the following instructions accordingly.

Once you have the key generated, find out whether the ssh agent is running.

```bash
ps -e | grep [s]sh-agent
```

If agent isn't running, start it with

```bash
ssh-agent /bin/bash
```

Load your new key into the ssh agent:

```bash
ssh-add ~/.ssh/id_rsa
```

You can now view your public key by means of

```bash
cat ~/.ssh/id_rsa.pub
```

Refer to to the instructions for your repository host like Github or Bitbucket as to how add your key top the host.

Once all the these prerequisites are in place you may deploy the site by running

```bash
fab setup
```

Supervisor, which is used for running the Nginx server, logs both the standard output and the standard error to log files in the folder `/var/log/supervisor`. You should check these log files if the server doesn't start.

For subsequent updates you may just run

```bash
fab deploy
```

If you get an internal server error after updating, there might still be a uWSGI process bound to the requested port. Also, it seems that sometimes changes aren't picked up after deployment, even though Supervisor is restarted. 

In these cases rebooting the server should help. You can easily force the reboot by executing
 
 ```bash
 fab reboot
 ```

