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
    image: centos:7 # or debian:10 ubuntu:19.04 archlinux/base fedora:28 ...
provisioner:
  name: ansible
  lint:
    name: ansible-lint
verifier:
  name: testinfra
  lint:
    name: flake8
```

This is a pretty basic test setup. All that's being done is playing around with files, directories and links, so it doesn't matter which linux/unix based distribution is being used so stick with the default docker image of `centos:7`. The only other dependency is git, to clone dotfiles. But since it will require git to do so, we'll have to create a `./molecule/default/prepare.yml` playbook that gets used after any instance is created, or when the molecule command `prepare` is used in the terminal: 

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

[Playbooks][10] will be covered in greater detail later, but basically they're just a collection of roles, variables and/or tasks that are run in order to combine the functionality of different roles. For now just copy the file as above. Another note, [package][11] in the above playbook is the ansible module for installing packages for any operating system the playbook is run on. Fortunately, I haven't encountered a distribution of linux yet that doesn't use the name `git` to refer to its respective package for git. The above playbook just gets called automatically by molecule, on every host defined in the `platforms:` section of `molecule.yml`, which is only the single default instance, `instance`.

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

The playbooks for `create` & `prepare` *(the playbook that we just created)*, should be run and if completed successfully a `PLAY RECAP` should appear at the bottom like this:

```sh
PLAY RECAP *********************************************************************
    instance                   : ok=2    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

So long as `unreachable` or `failed` have 0 events, it completed successfully. The play recap is just a summary output of the latest play to run, in this case `prepare.yml`.

Now to check that git was installed in our instance. Use the command `molecule login`, which will switch to the instance just created shell. **NOTE** while inside this instance its that instance's shell that's present on the terminal and it's necessary to use the command `exit`, to return to the previous shell. Once in the instance's shell, check to see that git was installed by typing `git` by itself and check that the help prompt for git shows up. If it does, all is well. Exit the instance's shell.

```sh
exit
```

Test Driven Development to Create Your First Role
-------------------------------------------------

Now that the test environment should be set up and working, it's possible and relatively easy to use a [Test Driven Development Workflow][13]. Read up on that article for even more details on this workflow, here it will only be summarized

### Test Driven Development Using Molecule

The basic process of TDD in molecule breaks down to something like this:

![TDD Cycle Diagram](https://cdn-images-1.medium.com/max/895/1*2IVfvMKBCcwHJYO7-HZRDA.png)

1. Create the test environment, *like we've done*, by changing `molecule/default/molecule.yml`, `molecule/default/playbook.yml` & `molecule/default/prepare.yml` *(optional)*.
2. Startup the instance(s) by using `molecule create`, and run the role using `molecule converge`.
3. Check that the environment works by snooping inside of the instance using `molecule login` then `exit` when done.
4. Write a test function in `./molecule/SCENARIO_NAME/tests/test_default.py` that checks for a desired outcome.
5. Use `molecule verify` which will run python tests on `test_default.py`, it should fail because the correct role hasn't been written yet.
    - In TDD parlance, this is known as the end of the **RED** phase, as in the test case should fail here.
6. Write the variable definitions, tasks, roles and/or playbooks necessary to satisfy the **RED** test case.
7. Use `molecule converge` then `molecule verify` to check if the test still fails, if it does loop back to step `4` till it does.
    - In TDD parlance, this is known as the end of the **GREEN** phase, think of a **GREEN** light.
8. Go back to the code written in the variables/tasks/roles/playbooks and refactor it to be clean, idiomatic, deduplicated code.
9. Use `molecule verify` to make sure that the refactored changes haven't made it dysfunctional, go back to step `8` if it doesn't pass.
    - Finally, in TDD terms, this is the end of the **REFACTOR** phase, and when it's done, move on to the next TDD cycle.
10. This test case's desired behavior has been defined (**RED**), implemented (**GREEN**), and **REFACTORED**. Keep looping from `4` to here till done programming.
11. Stop and cleanup the instance created in `1` & `2` using `molecule destroy`.

### Start the First Red Phase - Create the First Test Case

Essentially we're going to start the first **RED** phase of the TDD workflow, by defining a desired behavior that this role should have inside of its main task, `./molecule/default/tests/test_default.yml`.

```py
import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


# The default first test created by molecule
def test_hosts_file(host):
    f = host.file('/etc/hosts')

    assert f.exists
    assert f.user == 'root'
    assert f.group == 'root'

# Our First test case checks that our dotfile root directory exists
def test_dotfiles_root_directory_exists(host):
    # First get the host's user's home directory
    home_dir = host.user().home
    # Then check that *something* exists @ ~/.dotfiles
    assert host.file(home_dir + '/.dotfiles').exists
    # Check that something is actually a directory
    assert host.file(home_dir + '/.dotfiles').is_directory
```

The `test_default.py` file is automatically generated and is already a functioning test file. The only thing being added to test is the first behavior is inside the function `test_dotfiles_root_directory_exists`. Everything else should already be generated, let's discuss what's going on.

- The `os` import gets used by molecule so is necessary
    - `os` can also be useful for verifying outcomes of tasks/roles/playbooks as well
- The `testinfra.utils.ansible_runner` import is what gets used by molecule behind the scenes to run tests
    - The molecule test runner runs when invoking `molecule verify` in the terminal
    - Molecule will always pass information about the `host` instance into all the following test functions.
- `test_hosts_file(host)`:
    - The molecule-generated test function that checks that the testing class `testinfra` and its `ansible_runner` module correctly created a `host` object for the current host being tested.
    - An `ansible` `host` class object is passed to every test function that asks for a parameter during the verification sequence.
    - From this object a lot of information like the host's `file`s, `user`s, or `group`s can be checked.
    - `assert` is used to fail the test run if a false condition is created
        - In this case the file `/etc/hosts` has to exist to `assert` true
        - So does the `root` user and group ownership of the file
- `test_dotfiles_root_directory_exists(host)`:
    - The first custom test case
    - As name suggests, checks that a root directory for the upcoming dotfiles exists at path `~/.dotfiles`
    - To make it easier to get the home directory substitution for `~`, as the variable `home_dir`
    - Only check against the default values of a role's variables
        - This is because all roles should have default values for variables
        - Those variables can be overriden in playbooks or commands that specify different values.
        - So long as the default value is tested for, then any overridden paths for the variable like my personal location for dotfiles, `~/.dots` should work as well.
    - Test functions should always start with `test_SOME_TEST_NAME`
    - The `host` object can check for files in the test instance using its member method `file()`
    - `file()` returns an object with information about the path string given, be it a directory, link, if it exists, who owns it, etc.
        - The [testinfra module documentation][14] has more defails on how assertions like this could be used in other ways

So with the first test case out of the way, let's make sure that it fails *(as it should)*.

```sh
molecule verify
```

Which should return something like this:

```sh
=================================== FAILURES ===============================
___________ test_dotfiles_root_directory_exists[ansible://instance] ________
    
host = <testinfra.host.Host object at 0x7fcb3bdb9358>
    
def test_dotfiles_root_directory_exists(host):
    # First check that *something* exists @ ~/.dotfiles
>       assert host.file('~/.dotfiles').exists
E       AssertionError: assert False
E        +  where False = <file ~/.dotfiles>.exists
E        +    where <file ~/.dotfiles> = <class 'testinfra.modules.base.GNUFile'>('~/.dotfiles')
E        +      where <class 'testinfra.modules.base.GNUFile'> = <testinfra.host.Host object at 0x7fcb3bdb9358>.file
    
tests/test_default.py:24: AssertionError
====================== 1 failed, 1 passed in 2.08 seconds ==================
```

Some things to note on the test result:

- The `>` charecter points to the assertion that failed
    - *i.e.* the assertion that the directory `~/.dotfiles` exists
    - no role or task has been created making that directory yet so this is expected
- The `E` character points to the results of each operation leading up to the false assertion
    - These lines are **very** useful to debug failing test cases that you expect to pass

And if you're not sure about your test verification working under the right circumstances, use  these commands to login to the test instance, add the expected directory at `~/.dotfiles`, exit the instance, run verify to see it works, then destroy and recreate the instance so it's fresh for testing.

```sh
molecule login
mkdir ~/.dotfiles
exit
molecule verify
molecule destroy
molecule create
```

With the test working, we're now done with the **RED** phase, let's go to **GREEN**

### Move on to the Green Phase by Creating the First Task

In Test Driven Development, the purpose of the **GREEN** phase is to as quickly as possible create an implementation that satisfies the test case created in the **RED** phase. Ideally the whole TDD cycle shouldn't take more that 15 minutes if it's writing code that you're accustomed to. If it's a new language or framework it's fine to ignore this requirement. However, for a productive workflow the scope of the test case and the code to satisfy it shouldn't take much longer. If it does then consider making a more simple test case.

So let's create a task inside of the `./tasks/main.yml`, the starting tasks file for the role. Other tasks files can be created that are referenced by this file, but that's out of this role and article's scope. The `./tasks/main.yml` file should be edited to look like this.

```yml
---
# tasks file for mydotfiles
- name: "Root dotfiles directory dotfiles_root_dir exists"
  file:
    path: "{{ dotfiles_root_dir }}"
    mode: 0750
    state: directory
```

Quick overview of the above defined task:

- `name`: is an ansible module that defines the printed name of a specific task
    - the `-` indicates a YAML list, and a tasks file consists of a list of tasks
- `file`: as an indented key to the list item indicated by the first `-` is definining the module this task is using.
    - `file` modules allows setting specific files, directories, links, etc.
    - `path` sets the specific path of the file/directory/link being worked on
    - `mode` sets the permissions for that location
    - `state` is the state of this location
        - could be `file` (default), `directory`, `absent`, `link` and more
        - `directory` specifies that the directory exists
        - `absent` specifies that if anything is there it should be removed
    - The [ansible documentation][15] goes into much more details on the `file` module
- `"{{ dotfiles_root_dir }}"`:
    - It's an ansible variable to be defined later
    - The surrounding quotes are necessary to resolve the variable into a string
    - The surrounding curly braces are necessary to indicate this is a variable

Now, it's only necessary to define the first **default** variable. **Default** variables are the default variables that get used by roles. When these roles are run in playbooks or on the command line they can be overriden to change their values. For example, my variable file for all my machines that use this role override this value to `~/.dots`. But I imagine most people would want to store these dotfiles in the default location of `~/.dotfiles`, so that is the default defined for the role.

Default variables are stored in the `./defaults` directory and `./defaults/main.yml`, and it's just another ansible file where all the keys are variable names and their associated values. Create the variable `dotfiles_root_dir` to complete the implementation.

```yaml
---
# defaults file for mydotfiles

# dotfiles root directory, where all seperate dotfiles subdirectories go
dotfiles_root_dir: "~/.dotfiles"
```

Quick note about the `defaults` folder. These should only be the default values. The directory `./vars` are for variables that are specific **only** inside this role and aren't meant to be overridden outside this role. Their use is outside the scope of this article, but it's important not to confuse the two, generally use the `defaults` directory for roles.

Ok, now run `molecule converge && molecule verify` to apply the new role and its variable and test it. Hopefully this works and the **GREEN** phase is done with. If not, as in real situations go back and check the work till it does. Also, don't forget to consider that if it's taking too long and it's not because familiarity with the frameworks involved that maybe the test case is too complex.

Normally, from here you'd go back and refactor the code for both the role implementation or the test case and see if it should be rafactored. This is a very simple task and variable for the role and it was pre-planned for the purpose of writing this so it's not necessary here, but in general this should always be the case.

### Using the Git Module to Clone Github Repositories

Let's continue the TDD process, now that the directory all seperate github repositories will be cloned into exists, it's time to actually clone all of them. As usual start with a new test function that checks that my bash, vim, neovim, tmux, alacritty, and i3 dotfiles repositories have been cloned.









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
13. [Hackernoon: Introduction to Test Driven Development][13]
14. [TestInfra Documentation: File Class][14]
15. [Ansible Documentation: File Module][15]

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
[13]: https://hackernoon.com/introduction-to-test-driven-development-tdd-61a13bc92d92 "Hackernoon: Introduction to Test Driven Development"
[14]: https://testinfra.readthedocs.io/en/latest/modules.html#file "TestInfra Documentation: File Class"
[15]: https://docs.ansible.com/ansible/latest/modules/file_module.html "Ansible Documentation: File Module"

[50]: https://github.com/nvm-sh/nvm "Github: nvm-sh/nvm"

[99]: https://zapier.com/engineering/ansible-molecule "Zapier Blog: How We Test Our Ansible Roles with Molecule"
