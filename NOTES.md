Notes (TO BE MOVED TO NOTES OR DOCUMENTATION)
=============================================

Overview
--------

Before Molecule, developing and especially testing ansible roles was a bit of a pain. Molecule glues together a lot of modules into one standardized framework that makes this process **much** easier and convenient than it was before. Not only does defining and automating tests become easier now, but it supports basically any testing driver imaginable; be it Docker (default), Vagrant, or even cloud providers like AWS, Azure, Google Cloud or Digital Ocean.

My testing sequence is generally something like this:

**NEEDS EDITING TO BE MORE TDD APPROPRIATE**
* **Setup**: Prepare the environment for test execution
  * Spin up new virtual machines.
  * Prepare a local docker environment that creates new containers.
  * Even spin up cloud instances in a cloud provider like AWS or Digital Ocean.
  * Create the project
  * Create a virtual environment (optional) for python with all dependencies
  * If running vagrant spin up the images
* **Exercise**: Execute the test sequence defined in a molecule scenario & test playbook
  * Setup a [scenario][02] in molecule that probably includes a test playbook that runs the role
  * Setup the scenario in such a way that it provisions the instance with the role
* **Verify**: Use a [verifier][04] that verifies that the role results in the desired outcomes on the instance
  * Write verifications that ensure the role is doing what is expected 
  * Develop the role, update it, and fix the role that failed tests from before
  * If it passes, write a new test, ideally following a [Test Driven Development][90] process
  * If there are no more expectations of the role, then...
* **Teardown**: Tear down the instance
  * `molecule destroy`

Init the Project
----------------

**NOTE** Add this somewhere, but you need instructions or references to them for installing docker, pip install molecule ansible venv docker, and setting up docker permissions etc.
Easy enough, just use the molecule app with command `init` like below:

```sh
molecule init role -r role-node-dev-env
```

### Molecule Scenarios

Molecule creates a folder called `molecule` within the role base project filetree that stores all of the functionality molecule uses on this project. Molecule uses the concept of [scenarios][02] which are a top-level configuration syntax that stores a single set of testing configurations that can be customized. The `init` command creates a single scenario `default` inside the molecule directory that has the default testing configs.


### Scenario Layouts

The default scenario has a number of root files and directories:

```sh
ls
defaults  handlers  meta  molecule  README.md  tasks  vars
```

- Docker is the default **driver**, *i.e. the system used for testing which could also be Vagrant for example*, and it's a Jinja template allowing to use ansible variables to template the dockerfile.
- `INSTALL.rst` are instruction on any additional software or scripting needed to have this scenario's driver interface correctly with the role.
- `molecule`.yml is the configuration entrypoint for the scenario, it gets used to configure each tool molecule uses when testing the role.
- `playbook.yml` is the playbook file that gets called to test the role, it will look like any regular playbook but tuned for testing.
- `tests` is the testing directory that is a part of [TestInfra][03] which is the default [Verifier][04]. Verifiers are a molecule concept that gets used for setting up test verifications after executing the role.


### molecule.yml

The `molecule.yml` file is for configuring Molecule. It's a YAML file where the keys represent high level components/modules that Molecule provides and their different properties. These include:

- The [Dependency][05] manager for the role. This just defines already developed roles that this one depends on, which by default is handled by [Ansible Galaxy][06], but it could also be a custom repository
- The [Driver][07] provider defines the testing system driver, by default it's Docker. There are plenty others as well including cloud IaaS providers like Azure, EC2, GCE, and Digital Ocean.
- The [Lint][08] provider, which is by default YAMLLint, it's used to standardize the linting rules for anyone developing this role and to help individual developers write more clean and well functioning roles.
- The [Platform][09] definitions, which specifies to molecule which instances to create, names them, and groups them. Useful particularly if the role needs to work on multiple OSs, distributions or environments.
- The [Scenario][10] is used to specify parameters and the sequencing of the scenario's tests.
- The [Verifier][11] framework specifications that is used to define what the expected results of this role should be and verifies that's what they are. By default [TestInfra][03] is the framework used.

Run Test Sequence Commands
--------------------------

First, create the first molecule managed instance that gets used for testing, which by default again is the Docker driver. Start by checking that docker is working by entering this in the terminal:

```sh
docker run hello-world
```

If it works it should have pulled the `hello-world` docker image, it should have built its container, then printed the expected message of that image indicating all is well with the local docker system.

Then create a molecule instance with the molecule command `create`, verify it worked with `list`:

```sh
molecule create
molecule list
```

Which should be something like this, make particular note of the `Created` column:

```sh
Instance Name  Driver Name  Provisioner Name  Scenario Name  Created  Converged
-------------  -----------  ----------------  -------------  -------  ---------
instance       docker       ansible           default        true     false
```

Now use the molecule command `converge` after adding a testing task to `tasks/main.yml`:

```yml
- name: Molecule Hello World!
  debug:
    msg: Hello, World!
```

```sh
molecule converge
```

The play recap should show all tasks as `ok=2`, indicating all two tasks *(first one being the standard ansible task of gathering facts)* are accomplished. With an instance up it's possible to actually go into it via a terminal shell of the virtual instance to checkout the system, run commands, etc. Do so by using the molecule command `login`, leave the shell by using the bash command `exit`.

```sh
molecule login
```

 We're now free to start playing around with the state of our test instances. Before moving on, exit and destroy this instance.

```sh
molecule destroy
```

This entire sequence gets replayed when you run molecule's `test` command. For more details read the documentation for both [Scenarios][02].

Actually Building Something
---------------------------

So let's actually do something with this knowledge. First, we need to create a role boilerplate project to develop on. Of course, that's possible to do manually, but both ansible and molecule using ansible can do this for us, so lets create a new role to manage our dotfiles:

```sh
molecule init role --role-name my-dotfiles
```

This will now create all the folders and files with default settings for molecule for us automatically. Now it's up to us to modify it. But first, let's go over what this role will do:

- **TODO** In the future this role will be modified to template bash exports and sources
  - This will override `$XDG_DATA_HOME` & `$XDG_CONFIG_HOME` variables to be used when setting paths. For now this will be a literals
- Clone all dotfiles git repositories specified as ansible variables
- Link all dotfile subdirectories and files relevant to make their respective configurations work
  - This will also be handled in ansible variables

Note that each dotfile specifically will be *very* customized to my own preferences. As will most people's. You're free to use them for yourselves, but I would highly recommend you instead just read through them and incorporate pieces of them you find interesting and probably modify them further to your preferences. The general task of this role though, *i.e. clone, link & template*, would be pretty easily replicated for your own needs.

Ok, let's setup our molecule environment to work properly for us. Open up `./molecule/default/molecule.yml` and it to be something like this:

```yaml
---
dependency:
  name: galaxy
driver:
  name: docker
lint:
  name: yamllint
platforms:
  - name: instance
    image: debian:10 # insert whatever OS you want
    # could be centos:7, ubuntu:18:04, archlinux/base, etc. any dockerhub name
provisioner:
  name: ansible
  lint:
    name: ansible-lint
verifier:
  name: testinfra
  lint:
    name: flake8
```

This is a pretty basic test setup. Everything we need to do is done from a command line using only one dependency, git, to clone dotfiles. But since it will require git to do so, we'll have to create a `./molecule/default/prepare.yml` playbook that gets used after any instance is created: 

```yaml
---
- name: Prepare
  hosts: all
  tasks:
  - name: Install the only role dependancy, git
    package:
      name: git
      state: present
```

[Playbooks][10] will be covered in greater detail later, but basically they're just a collection of roles, variables and/or tasks that are run in order to combine the functionality of different roles. For now just copy the file as above. Another note, [package][11] in the above playbook is the ansible module for installing packages for any operating system the playbook is run on. Fortunately, I haven't encountered a distribution of linux yet that doesn't use the name `git` to refer to its respective package for git.

Ok, let's verify that when the instance is created that git is in fact present.

```sh
molecule create
```

Oops! It's possible you haven't [installed docker][12], or molecule yet. If you have skip to the next paragraph, otherwise read the link in the last sentence for your OS's install guide and follow along to install molecule in a python virtual environment *(venv)*. After having docker installed, create the python environment with these commands below.

```sh
python -m venv venv && \
source venv/bin/activate && \
pip install molecule[docker] && \
echo "venv" >> .gitignore && \
pip freeze >> requirements.txt
```

This does a couple of things:

- Uses python's built in `venv` module to create a virtual environment for this project folder called `venv`.
  - **NOTE** This module didn't get incorporated into the standard library of python till version 3.3.
  - At the time of this writing the current release of python is `3.7.4`.
- Sources the `activate` configuration that `venv` created for itself to start the virtual environment.
  - This can be verified by typing `which python` and it should show a python interpreter inside of the venv in the project path.
- Installs the dependancy group `molecule[docker]` which are the dependencies to use molecule with docker as driver to create testing instances.
  - There's tons of other dependencies that go along with this including `docker` which is a python wrapper for docker, and of course `ansible`.
- Then it echo's `venv` into the project's `.gitignore` file incase this is a git project
  - You don't ever want to include your virtual environments in a version controlled project
- Freezes the virtual environment's installed package into the standard `requirements.txt` file.

The environment should now be ready to go, and molecule should now be able to create a test instance of debian 10, but now with git installed. Use `molecule create` to start the test instance.

```sh
molecule create
```


References
----------

1. [Molecule Documentation: Getting Started][01]
2. [Molecule Documentation: Scenarios][02]
3. [TestInfra Documentation: Overview][03]
4. [Molecule Documentation: Verifier][04]
5. [Molecule Documentation: Dependency][05]
6. [Ansible Documentation: Ansible Galaxy][06]
7. [Molecule Documentation: Driver][07]
8. [Molecule Documentation: Lint][08]
9. [Molecule Documentation: Platforms][09]
10. [Ansible Documentation: Intro to Playbooks][10]
11. [Ansible Documentation: Package Module][11]
12. [Docker Documentation: Getting Started][12]

50. [Github: nvm-sh/nvm][50]

99. [Zapier Blog: How We Test Our Ansible Roles with Molecule][99]


[01]: https://molecule.readthedocs.io/en/stable/getting-started.html "Molecule Documentation: Getting Started"
[02]: https://molecule.readthedocs.io/en/stable/configuration.html#root-scenario "Molecule Documentation: Scenarios"
[03]: https://testinfra.readthedocs.io/en/latest/index.html "TestInfra Documentation: Overview"
[04]: https://molecule.readthedocs.io/en/stable/configuration.html#verifier "Molecule Documentation: Verifier"
[05]: https://molecule.readthedocs.io/en/stable/configuration.html#dependency "Molecule Documentation: Dependency"
[06]: https://docs.ansible.com/ansible/latest/reference_appendices/galaxy.html "Ansible Documentation: Ansible Galaxy"
[07]: https://molecule.readthedocs.io/en/stable/configuration.html#driver "Molecule Documentation: Driver"
[08]: https://molecule.readthedocs.io/en/stable/configuration.html#linters "Molecule Documentation: Lint"
[09]: https://molecule.readthedocs.io/en/stable/configuration.html#platforms "Molecule Documentation: Platforms"
[10]: https://docs.ansible.com/ansible/latest/user_guide/playbooks_intro.html "Ansible Documentation: Intro to Playbooks"
[11]: https://docs.ansible.com/ansible/latest/modules/package_module.html "Ansible Documentation: Package Module"
[12]: https://docs.docker.com/get-started/ "Docker Documentation: Getting Started"

[50]: https://github.com/nvm-sh/nvm "Github: nvm-sh/nvm"

[99]: https://zapier.com/engineering/ansible-molecule "Zapier Blog: How We Test Our Ansible Roles with Molecule"
