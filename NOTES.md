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
    path: '{{ dotfiles_root_dir }}'
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
- `'{{ dotfiles_root_dir }}'`:
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

Let's continue the TDD process, now that the directory all seperate github repositories will be cloned into exists, it's time to actually clone all of them. As usual start with a new test function that checks that my bash, vim, neovim, tmux, alacritty, and i3 dotfiles repositories have been cloned in `./molecule/default/tests/test_default.py`.

```yaml
# Test that files all git repositories are correctly downloaded
def test_dotfiles_subdirectories_exist(host):
    # first create the dotfiles path
    dots_dir = host.user().home + '/.dotfiles'
    # first create an array of strings with every expected subdirectory name
    dot_subdirs = [
        'bash',
        'vim',
        'neovim',
        'tmux',
        'alacritty',
        'i3',
    ]
    # now iterate through each expected subdirectory and assert their existence
    for subdir_name in dot_subdirs:
        dot_subdir = dots_dir + '/' + subdir_name
        assert host.file(dot_subdir).exists
        assert host.file(dot_subdir).is_directory
```

Real quickly, `dots_dir` just creates the base path of `~/root/.dotfiles`. Then `dots_subdir` just creates a list of the expected subdirectories inside `dots_dir`. Then a loop iterates over those subdirectories, puts together the base path with the subdirectory name to be cloned. Finally it asserts they exist and are directories.

Before finishing the red stage, make sure that this test case works by running `molecule verify`, it should fail. Then go into the test instance with `molecule login`, then use this command:

```sh
cd ~/.dotfiles && mkdir bash vim neovim tmux alacritty i3
```

This will just create the expected conditions manually so it can be verified that the test passes under the expected circumstances by running `exit` then `molecule verify`, it should pass. Now just reset the environment by running:

```sh
molecule destroy && molecule create && molecule converge
```

Now move onto the green phase by starting at the defaults variable file `./defaults/main.yml`:

```yaml
---
# defaults file for mydotfiles

# dotfiles root directory, where all seperate dotfiles subdirectories go
dotfiles_root_dir: "~/.dotfiles"

# bash dotfiles
dotfiles_bash_repo_url: https://github.com/marcus-grant/dots-bash
dotfiles_bash_subdir_name: bash

# vim dotfiles
dotfiles_vim_repo_url: https://github.com/marcus-grant/dots-vim
dotfiles_vim_subdir_name: vim

# neovim dotfiles
dotfiles_neovim_repo_url: https://github.com/marcus-grant/dots-neovim
dotfiles_neovim_subdir_name: neovim

# tmux dotfiles
dotfiles_tmux_repo_url: https://github.com/marcus-grant/dots-tmux
dotfiles_tmux_subdir_name: tmux

# alacritty dotfiles
dotfiles_alacritty_repo_url: https://github.com/marcus-grant/dots-alacritty
dotfiles_alacritty_subdir_name: alacritty

# i3 dotfiles
dotfiles_i3_repo_url: https://github.com/marcus-grant/dots-i3
dotfiles_i3_subdir_name: i3
```

Normally variables should be prefixed by some reference to the role name, *i.e.* `dotfiles`. Then there's a increasing granularity about what the variable name references. Next, go back and edit the `./tasks/main.yml` to add tasks that clone all these repositories with the given variables:

```yml
---
# tasks file for mydotfiles
- name: Clone bash dotfiles
  git:
    repo: '{{ dotfiles_bash_repo_url }}'
    dest: '{{ dotfiles_root_dir }}/{{ dotfiles_bash_subdir_name }}'

- name: Clone vim dotfiles
  git:
    repo: '{{ dotfiles_vim_repo_url }}'
    dest: '{{ dotfiles_root_dir }}/{{ dotfiles_vim_subdir_name }}'

- name: Clone neovim dotfiles
  git:
    repo: '{{ dotfiles_neovim_repo_url }}'
    dest: '{{ dotfiles_root_dir }}/{{ dotfiles_neovim_subdir_name }}'

- name: Clone tmux dotfiles
  git:
    repo: '{{ dotfiles_tmux_repo_url }}'
    dest: '{{ dotfiles_root_dir }}/{{ dotfiles_tmux_subdir_name }}'

- name: Clone alacritty dotfiles
  git:
    repo: '{{ dotfiles_alacritty_repo_url }}'
    dest: '{{ dotfiles_root_dir }}/{{ dotfiles_alacritty_subdir_name }}'

- name: Clone i3 dotfiles
  git:
    repo: '{{ dotfiles_i3_repo_url }}'
    dest: '{{ dotfiles_root_dir }}/{{ dotfiles_i3_subdir_name }}'
```

Basically each new task does the same thing but with different variables. The [ansible git module][16] gets used to clone a repository defined in the variables previously to a destination that is a combination of the `dotfiles_root_dir` / `dotfiles_PROGRAM_subdir_name` directory. The reason each subdirectory gets their own name is to deal with the fact that my dotfiles repositories are all prefixed with `dots-` and locally I'd prefer they use a shorter name.

Run the role using `molecule converge`, then verify it using `molecule verify`. The tests should be verifying the new role tasks are working. The green phase is done, now let's consider a refactor.

In the previous task updates, a lot of the same tasks were repeated but with slightly different parameters. A good refactor here might be to make use of looping to reduce code and increase cleanliness. Go back and edit `./defaults/main.yml`:

```yaml
---
# defaults file for mydotfiles

# dotfiles root directory, where all seperate dotfiles subdirectories go
dotfiles_root_dir: '~/.dotfiles'
dotfiles_url_prefix: 'https://github.com/marcus-grant'

dotfiles:
  bash:
    repo_url: '{{ dotfiles_url_prefix }}/dots-bash'
    subdir_name: 'bash'
  vim:
    repo_url: '{{ dotfiles_url_prefix }}/dots-vim'
    subdir_name: 'vim'
  neovim:
    repo_url: '{{ dotfiles_url_prefix }}/dots-neovim'
    subdir_name: 'neovim'
  tmux:
    repo_url: '{{ dotfiles_url_prefix }}/dots-tmux'
    subdir_name: 'tmux'
  alacritty:
    repo_url: '{{ dotfiles_url_prefix }}/dots-alacritty'
    subdir_name: 'alacritty'
  i3:
    repo_url: '{{ dotfiles_url_prefix }}/dots-i3'
    subdir_name: 'i3'
```

First, there's a new variable `dotfiles_url_prefix`, which is used to save the prefix of the URL to all the dotfile repositories. They all come from the same github user, me, so no point in repeating that substring constantly. Then all the repeating `repo_url` and `subdir_name` variables are brought into a dictionary.

For example, accessing bash's `repo_url` of the bash dotfile, just use the variable reference `{{ dotfiles.bash.repo_url }}`. It's important to include the quotations when using variable template strings, and a common error happens in these kinds of variable substitutions.

A good way of debugging these things is to temporarily insert an [ansible debug module][17]:

```yaml
- name: 'Check the dotfiles.bash.repo_url var'
  debug:
    msg: 'dotfiles.bash.repo_url: {{ dotfiles.bash.repo_url }}'
```

The dictionary layout of these repeating variable keys doesn't just look cleaner, but the fact that they're nested like this allows for iterating through them using [ansible loops][18].

To make things easier, the tasks that are going to be looped for each individual dotfile configuration is going to get its own seperate task file, `./tasks/dotfile.yml`:

```yaml
---
- name: 'Clone {{ item.key }} dotfiles'
  git:
    repo: '{{ item.value.repo_url }}'
    dest: '{{ dotfiles_root_dir }}/{{ item.value.subdir_name }}'
```

You'll notice this task looks like one of the multiple tasks from before in `./tasks/main.yml`. The variables have been replaced by an `item` variable and its `key` & `value` along with the nested dictionary definitions created in the defaults file. More on the `item`, `key`, and `value` usage later. This task is what will be repeated with the different parts of the `dotfiles:` dictionary defined in the default variabls. Next return to the `./tasks/main.yml` file and edit it.

```yaml
---
# tasks file for mydotfiles
- name: "root dotfiles directory dotfiles_root_dir exists"
  file:
    path: '{{ dotfiles_root_dir }}'
    mode: 0750
    state: directory

- name: transform dotfiles variable dictionary to iterable list
  set_fact:
    dotfiles_config_list: '{{ dotfiles | dict2items }}'
  loop: "{{ dotfiles|dict2items }}"
  when: item.value != ''

# - name: debug dotfiles_config_list
#   debug: { msg: 'dotfiles_config_list: {{ dotfiles_config_list }}' }

- include: dotfile.yml
  with_items: "{{ dotfiles_config_list }}"
```

Wow, much shorter than before. Let's go over it in a list overview:

- `set_fact`: is another ansible module
    - All it does is set a new variable, `dotfiles_config_list` with the below modules
- `dict2items` is a [loop filter][18]
    - Basically uses the loop in the task to iterate `dotfiles` keys to turn them, and all the nested things inside into an iterable list
    - Below is an example
    - The dictionary then becomes a list of dictionaries instead with its key behind `key`
    - Each list item's value is then stored inside the item's `value` property
    - This is then possible to iterate through and use the same nested variable names to apply different configuration tasks for each item
- `loop`: gets used to iterate every dictionary key inside of `dotfiles`
- `when`: is used to only iterate when the nested items are not empty
- `include`: is an ansible module to include a tasks file, `dotfile.yml` defined before
- `with_items`: is a module that treats the `dotfile.yml` tasks as a loop
    - `dotfiles_config_list`'s items are passed as the variable `item` into the `dotfile.yml` tasks, where the `item` variable can be used to do the same with different values
    - One such `item` value would be `item.value.subdir_name` is `bash` using the previously defined defaults

```yaml
dictionary:
    propertyA: { propertyA1: a1, propertyA2: a2 }
    propertyB: { propertyB1: b1, propertyB2: b2 }
```
*... becomes ...*
```yaml
dictionary:
    - key: propertyA
      value: { propertyA1: a1, propertyA2: a2 }
    - key: propertyB
      value: { propertyB1: b1, propertyB2: b2 }
```

I also included a commented out example of a debug task used to test the shape of the `dotfiles_config_list` variable that gets iterated by `dotfile.yml`. This is a somewhat complex transformation of data and it's likely it won't work on the first attempt. That's when modules like `debug` are very useful. Just use it with `molecule converge` and the output will show debug messages showing the shape of the data.

This was a somewhat complex refactor, and ideally refactors should be pretty quick. Give yourself some extra time to learn things like this even though the TDD workflow is being used. Once structures like this are understood it shouldn't take that long in future refactor phases, or maybe even green ones to accomplish this sort of thing. Well, this TDD cycle has completed, let's handle the last two test cases for this role, and conclude.

### Finishing Up the Role

The dotfiles that were cloned are dotfiles that get updated often using git. By itself that's no problem, but people like me use SSH to communicate with git servers, and these repositories were cloned using HTTPS to not have to deal with complexities like ensuring SSH keys are managed.

The next red phase is to define a test function that checks the remote URL of all the dotfile cloned directories are SSH URLs. Currently they look something like this:

```sh
git remote -v
origin	https://github.com/marcus-grant/dots-bash (fetch)
origin	https://github.com/marcus-grant/dots-bash (push)
sh
```

When really it should look like this...

```sh
git remote -v
origin	git@github.com:marcus-grant/dots-bash (fetch)
origin	git@github.com:marcus-grant/dots-bash (push)
```

Let's update `./molecule/default/tests/test_default.py`:

```python
# Do all the cloned repositories have ssh remote origins?
def test_dotfiles_remote_origin_uses_ssh(host):
    # first create the dotfiles path
    dots_dir = host.user().home + '/.dotfiles'
    # create an array of strings with all expected subdirectory names
    dot_subdirs = [
        'bash',
        'vim',
        'neovim',
        'tmux',
        'alacritty',
        'i3',
    ]
    # map all of the subdirectory names to be full paths using dots_dir
    dot_dirs_iter = map(lambda x: '{}/{}'.format(dots_dir, x), dot_subdirs)
    # iterate through all the paths to check if it has an ssh remote
    for dot_dir in dot_dirs_iter:
        # first format the command string to be used
        cmd = host.run('cd {} && git remote -v'.format(dot_dir))
        # first check that no error occured in running the command
        assert cmd.rc == 0
        # then check that there's an origin and a ssh git address
        assert 'origin' in cmd.stdout
        assert 'git@github.com' in cmd.stdout
```

Basically, the same dotfiles directory paths are created again using template string and stored in `dot_dirs_iter` as a python iterator. This means all the directories can easily be iterated with their complete paths as `dot_dir`. Then the `testinfra` module `run` is used to change into the current `dot_dir` and running the git command `git remote -v` so the results can be tested.

First, the command should actually run successfully which is indicated by its return code, or `rc` being 0. Then the `stdout` of the command should contain both `origin` and the github ssh base address of `git@github.com`. To test that this test case will actually detect a properly changed remote, `molecule login` into the instance, change to the bash directory at `~/.dotfiles/bash` and use this command to set the git remote to its ssh equivalent.

```sh
git remote set-url origin git@github.com:marcus-grant/dots-bash.git
```

Exit the instance with `exit`, `molecule verify` to verify that the assertion doesn't fail when testing the `bash` subdirectory. It should however still fail on the next dotfiles subdirectory which should be `vim`. Let's move onto the green phase since the test case should now work.

Go back to `./tasks/dotfile.yml` because this is something that needs to be done for each dotfile set.

```yaml
---
- name: 'Clone {{ item.key }} dotfiles'
  git:
    repo: '{{ item.value.repo_url }}'
    dest: '{{ dotfiles_root_dir }}/{{ item.value.subdir_name }}'

- name: 'Set {{ item.key }} remote to use SSH remote url'
  shell: >
    git remote set-url origin 
    '{{ item.value.repo_url_ssh }}'
  args:
    chdir: '{{ dotfiles_root_dir }}/{{ item.value.subdir_name }}'
```

This adds another important ansible module, the [shell][19]. Basically it just takes a string of a command to execute in the remote shell. It again uses the passed `item` variable that contains the configuration dictionary for this particular dotfile set and sets the git remote using `item.value.repo_url_ssh`. The `args` key is used with `shell` to specify any extra arguments to use on the shell, in this case the `chdir` directive that tells ansible where to run the shell command. The git command is simply `git remote set-url origin REPO_URL`. Leaving us with a new default variable to add in `./defaults/main.yml`

```yaml
---
# defaults file for mydotfiles

# dotfiles root directory, where all seperate dotfiles subdirectories go
dotfiles_root_dir: '~/.dotfiles'
dotfiles_url_prefix: 'https://github.com/marcus-grant'
dotfiles_url_prefix_ssh: 'git@github.com:marcus-grant'
# dotfiles_url_prefix: 'URL'

dotfiles:
  bash:
    repo_url: '{{ dotfiles_url_prefix }}/dots-bash'
    repo_url_ssh: '{{ dotfiles_url_prefix_ssh }}/dots-bash'
    subdir_name: 'bash'
  vim:
    repo_url: '{{ dotfiles_url_prefix }}/dots-vim'
    repo_url_ssh: '{{ dotfiles_url_prefix_ssh }}/dots-vim'
    subdir_name: 'vim'
  neovim:
    repo_url: '{{ dotfiles_url_prefix }}/dots-neovim'
    repo_url_ssh: '{{ dotfiles_url_prefix_ssh }}/dots-neovim'
    subdir_name: 'neovim'
  tmux:
    repo_url: '{{ dotfiles_url_prefix }}/dots-tmux'
    repo_url_ssh: '{{ dotfiles_url_prefix_ssh }}/dots-tmux'
    subdir_name: 'tmux'
  alacritty:
    repo_url: '{{ dotfiles_url_prefix }}/dots-alacritty'
    repo_url_ssh: '{{ dotfiles_url_prefix_ssh }}/dots-alacritty'
    subdir_name: 'alacritty'
  i3:
    repo_url: '{{ dotfiles_url_prefix }}/dots-i3'
    repo_url_ssh: '{{ dotfiles_url_prefix_ssh }}/dots-i3'
    subdir_name: 'i3'
```

A new scalar variable, `dotfiles_url_prefix_ssh` is defined to provide the base url for the same git repository, but using ssh. Then for every `dotfile` configuration dictionary the key `repo_url_ssh` is added that combines this with the suffix of that dotfile repository's URL. This is a lot of repitition and is a good candidate for refactoring when it comes to that TDD phase. Don't worry about that right now, use `molecule converge` & `molecule verify` to configrm that these changes to the role work, it should.

Now let's look at a refactor, because here both the variables and the test cases could use one.

First, the default variables. Two problems are apparent, there's a lot of code duplication and variable definitions should try and avoid dependency on other variables if possilbe, especially as role defaults. Let's start with this change of the `./defaults/main.yml` file.

```yaml
---
# defaults file for mydotfiles

# dotfiles root directory, where all seperate dotfiles subdirectories go
dotfiles_local_root_dir: '~/.dotfiles'
dotfiles_url_prefix_https: 'https://github.com/marcus-grant'
dotfiles_url_prefix_ssh: 'git@github.com:marcus-grant'
# dotfiles_url_prefix: 'URL'

dotfiles:
  bash:
    repo_name: 'dots-bash'
    local_subdir_name: 'bash'
  vim:
    repo_name: 'dots-vim'
    local_subdir_name: 'vim'
  neovim:
    repo_name: 'dots-neovim'
    local_subdir_name: 'neovim'
  tmux:
    repo_name: 'dots-tmux'
    local_subdir_name: 'tmux'
  alacritty:
    repo_name: 'dots-alacritty'
    local_subdir_name: 'alacritty'
  i3:
    repo_name: 'dots-i3'
    local_subdir_name: 'i3'
```

Wow, much cleaner. There's now two `dotfiles_url_prefix` variables, one for an HTTPS and one for SSH URLs. Then each configuration set for each dotfile now has a `repo_name` variable instead of a templated string for the full URL. From these changes in the default variables, now it's possible to take all literal values and do all the previous work by changing how the variables are fed to the tasks. Let's change `./tasks/dotfile.yml` to reflect these changes

```yaml
---
- name: 'transform {{ item.key }} variables for current dotfile set'
  set_fact:
    current_dotfile_local_dir: >-
      {{ dotfiles_local_root_dir }}/{{ item.value.local_subdir_name }}
    current_dotfile_repo_url_http: >-
      {{ dotfiles_url_prefix_https }}/{{ item.value.repo_name }}
    current_dotfile_repo_url_ssh: >-
      {{ dotfiles_url_prefix_ssh }}/{{ item.value.repo_name }}

# - debug:
#     msg: >
#       current_dotfile_local_dir: {{ current_dotfile_local_dir }}
#       current_dotfile_repo_url_http: {{ current_dotfile_repo_url_http }}
#       current_dotfile_repo_url_ssh: {{ current_dotfile_repo_url_ssh }}

- name: 'gather facts about {{ item.key }} local subdirectory'
  stat:
    path: '{{ current_dotfile_local_dir }}'
  register: dot_local

- name: 'clone {{ item.key }} dotfiles'
  when: (not dot_local.stat.isdir is defined) or (not dot_local.stat.isdir)
  git:
    repo: '{{ current_dotfile_repo_url_http }}'
    dest: '{{ current_dotfile_local_dir }}'

- name: 'gather facts about {{ item.key }} remote repository'
  shell: 'git remote -v'
  args:
    chdir: '{{ current_dotfile_local_dir }}'
  register: dot_remote
  changed_when: false # normally registring on shell marks task as changed

- name: 'set {{ item.key }} remote to use SSH remote url'
  when: dotfiles_url_prefix_ssh not in dot_remote.stdout
  shell: >-
    git remote set-url origin 
    '{{ current_dotfile_repo_url_ssh }}'
  args:
    chdir: '{{ current_dotfile_local_dir }}'
```

A lot has changed here. First and foremost, changing the variables means trying to even run the role with `molecule converge` will fail to run due to the changes. Let's list the changes:

- `set_fact` gets used to create temporary variables `current_dotfile_`
    - These are mostly there to avoid repeating several long string templates
    - The tasks below will then access these templated strings through one variable
- `>-`: is a **folding scalar** and they are used to fold the below lines into one long one
- `stat`: is [another module][20] that gets information about a filesystem location
    - Here it is used to see if the `path` to the local subdirectory has somethin in it
    - And if it is a directory as is expected
    - This comes up becuase if you run the playbook you'll notice that the clone tasks are still cloning even though the playbook was run before
    - Using `when` as a conditional for the clone task using `dot_local` skips the clone task when a directory is there already
- `shell`: gets used to check the status of the cloned repo's remote & to change it
    - `when`: is used to only use the `shell` command if the previous one discovers that it is still using the HTTPS URL
    - `args`: gets used to call the shell command at the local subdirectory
    - `changed_when`: is used because registering a shell command marks the task has changing something
        - This creates noise in the output of the role
        - Using `changed_when: false` supresses these task messages

These changes together not only clean up the code, but deals with fixing the role in a way that it isn't needlessly repeating tasks and reporting noise to ansible. But most importantly this fix now means that a variable number of sets of dotfile repository URLs and local subdirectories can be defined in the very likely case their needs are different than mine. This hopefully highlights the importance of the refactoring phase. Hopefully `molecule converge && molecule verify` passes its test allowing us to move onto the last behavior to cycle through.

### The Last Role Behavior - Linking the Dotfiles

Dotfiles being cloned into one repository isn't terribly useful by itself, for the programs expecting the configurations to use them they need to be linked to paths they expect. Start the red phase by editing `./molecule/default/tests/test_default.py`.

```python
# Test that all the expected files are linked correctly
def test_dotfiles_links(host):
    # first create the dotfiles path
    home_dir = host.user().home
    dots_dir = home_dir + '/.dotfiles'
    # create an array of tuples for each dotfile set's links
    bash_links = [
        (dots_dir + '/bash/bashrc', home_dir + '/.bashrc'),
        (dots_dir + '/bash/profile', home_dir + '/.profile'),
        (dots_dir + '/bash/bash_profile', home_dir + '/.bash_profile'),
    ]
    vim_links = [
        (dots_dir + '/vim', home_dir + '/.vim'),
        (dots_dir + '/vim/vimrc', home_dir + '/.vimrc'),
    ]
    neovim_links = [(dots_dir + '/neovim', home_dir + '/.config/nvim')]
    tmux_links = [
        (dots_dir + '/tmux/.tmux.conf', home_dir + '/.tmux.conf'),
        (dots_dir + '/tmux/.tmux.conf.local', home_dir + '/.tmux.conf.local'),
    ]
    alacritty_links = [(dots_dir + '/alacritty', home_dir + '/.config/alacritty')]
    i3_links = [(dots_dir + '/i3', home_dir + '/.config/i3')]
    # combine them into a single array to iterate through
    dot_sets = [
        bash_links, vim_links, neovim_links,
        tmux_links, alacritty_links, i3_links,
    ]
    # now iterate through it, checking 
    for links in dot_sets:
        # iterate through the list of links in each dot set
        for link in links:
            # pull out the link_loc & link_dest to shorten the asserts
            link_src = host.file(link[0])
            link_dest = host.file(link[1])
            # assert link source exists
            assert link_src.exists
            # is link source a file or directory?
            assert link_src.is_file or link_src.is_directory
            # does link itself exist?
            assert link_dest.exists
            # is it a symlink?
            assert link_dest.is_symlink
            # finally, does the link location point to link source?
            assert link_dest.linked_to == link_src
```

Because of how many links there are due to some set of dotfiles having more than one link to be functional *(cough, bash, cough)* this test function is more complex. But because the upcoming changes has so many implications on the test instance, it's worht it. And it's a lot of declarative definitions and not that much complexity when it comes to testing. Mostly it is just setting up arrays of links for each dotfile set. It then iterates through all of the dot sets' links and asserts that they are proper links. Read the comments for more details.

Before moving onto the green phase to implement these expected outcomes, run `molecule converge && molecule verify`, it should fail. Then `molecule login` and create at least one of the expected links using `ln -sf ~/.dotfiles/bash/bashrc ~/.bashrc` and verify again, and if all is well with the test function, a different link assertion should be failing than the last verification fail. If that's the case then the test function should be working.

Fortunately, the role changes are much simpler. Edit `./tasks/dotfile.yml`

```yaml
# ... previous tasks

- include: link_dotfiles.yml
  with_items: "{{ item.value.links }}"
  loop_control:
    loop_var: dot_link

# end of file
```

Again, a looping task is being created. It will take a new dotfile list item property `links`, which is itself a list of `links`. This time each list item is passed using `loop_var` as variable `dot_link`. These `dot_links` are then passed to a new task file `dotfile_links.yml` individually to handle the actual lnking of these files, like below:

```yaml
---
# links dotfiles sets defined in defaults as `dotfile`
# assumed to be included using 'with_items' as a loop using variable 'dot_link'
# the incoming variable should have item.link_loc & item.link_dest
- name: 'link: {{ dot_link.src }} ~> {{ dot_link.dest }}'
  # when
  file:
    src: '{{ dot_link.src }}'
    dest: '{{ dot_link.dest }}'
    state: link
    force: true
```

Here each `dot_link` sent into the task is simply linked from `link.src` to `link.dest` as symlinks so that although all dotfiles are in one place, the programs that use them will think each link as the file it expects inside of `~/.dotfiles`.

Now finally, edit the default variables in `./defaults/main.yml`:

```yaml
---
# defaults file for mydotfiles

# dotfiles root directory, where all seperate dotfiles subdirectories go
dotfiles_local_root_dir: '~/.dotfiles'
dotfiles_url_prefix_https: 'https://github.com/marcus-grant'
dotfiles_url_prefix_ssh: 'git@github.com:marcus-grant'
# dotfiles_url_prefix: 'URL'

dotfiles:
  bash:
    repo_name: 'dots-bash'
    local_subdir_name: 'bash'
    links:
      - { dest: '~/.bashrc', src: '~/.dotfiles/bash/bashrc' }
      - { dest: '~/.profile', src: '~/.dotfiles/bash/profile' }
      - { dest: '~/.bash_profile', src: '~/.dotfiles/bash/bash_profile' }
  vim:
    repo_name: 'dots-vim'
    local_subdir_name: 'vim'
    links:
      - { dest: '~/.vim', src: '~/.dotfiles/vim' }
      - { dest: '~/.vimrc', src: '~/.dotfiles/vim/vimrc' }
  neovim:
    repo_name: 'dots-neovim'
    local_subdir_name: 'neovim'
    links:
      - { dest: '~/.config/nvim', src: '~/.dotfiles/neovim' }
  tmux:
    repo_name: 'dots-tmux'
    local_subdir_name: 'tmux'
    links:
      - { dest: '~/.tmux.conf', src: '~/.dotfiles/tmux/.tmux.conf' }
      - { dest: '~/.tmux.conf.local', src: '~/.dotfiles/tmux/.tmux.conf.local' }
  alacritty:
    repo_name: 'dots-alacritty'
    local_subdir_name: 'alacritty'
    links:
      - { dest: '~/.config/alacritty', src: '~/.dotfiles/alacritty' }
  i3:
    repo_name: 'dots-i3'
    local_subdir_name: 'i3'
    links:
      - { dest: '~/.config/i3', src: '~/.dotfiles/i3' }
```

Each dotfile set now gets an extra dictionary, itself containing a list called `links`. Each dotfile set can have a variable number of links that need to be manually entered for each file that must be linked. Organizing it this way ensures that any number of links can be specified and that their sources (`src`) and destination (`dest`) can be unique.

Test this by running `molecule converge && molecule verify`... Oops...

Many programs that use dotfiles expect to have a directory inside `~/.config`, and this role doesn't guarantee that directory exists. Fortunately it's easy to handle this with another task inside of `./tasks/main.yml`:

```yaml
# ... previous tasks are ^^^^ up here
# this guarantees ~/.config exists
- name: ~/.config directory exists
  file:
    path: '~/.config'
    state: directory
    mode: 0700

# last task
- include: dotfile.yml
  with_items: "{{ dotfiles_config_list }}"
```

Test again by running `molecule converge && molecule verify`... phew. That should work now. Then let's go through the final refactoring phase. The green phase was relatively simple in changes to the role, there aren't many places to improve so let's focus on cleaning up the test file `./molecule/default/tests/test_default.py`.

**NOTE THIS STILL NEEDS FURTHER REFACTORING BEFORE PUBLISHING ARTICLE**
```python
import os
import pytest

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
    dots_root_dir = host.file('/root/.dotfiles')
    # check that *something* exists @ ~/.dotfiles
    assert dots_root_dir.exists
    # check that something is actually a directory
    assert dots_root_dir.is_directory


dot_subdir_names = ['bash', 'vim', 'neovim', 'tmux', 'alacritty', 'i3']


# helper that returns an array of all complete dotfile subdir paths
def _dot_subdir_paths(host):
    return ['/root/.dotfiles/' + s for s in dot_subdir_names]


# fixture that precomputes the above function so its ready before any test
@pytest.fixture()
def dot_subdir_paths(host):
    return _dot_subdir_paths(host)


# helper for array of testinfra file objects for every dotfile subdirectory
@pytest.fixture()
def dot_subdirs(host):
    return [host.file(s) for s in _dot_subdir_paths(host)]


# test that files all git repositories are correctly downloaded
def test_dotfiles_subdirectories_exist(host, dot_subdirs):
    for subdir in dot_subdirs:
        assert subdir.exists
        assert subdir.is_directory
        

# Do all the cloned repositories have ssh remote origins?
def test_dotfiles_remote_origin_uses_ssh(host, dot_subdir_paths):
    # iterate through all the paths to check if it has an ssh remote
    for subdir_path in dot_subdir_paths:
        # first format the command string to be used
        cmd = host.run('cd {} && git remote -v'.format(subdir_path))
        # first check that no error occured in running the command
        assert cmd.rc == 0
        # ensure that the cloned repo is an origin and ssh url
        assert 'origin' in cmd.stdout
        assert 'git@github.com' in cmd.stdout


# Test that all the expected files are linked correctly
@pytest.mark.parametrize('link_src_path,link_dest_path', [
    ('/bash/bashrc',            '/.bashrc'),
    ('/bash/profile',           '/.profile'),
    ('/bash/bash_profile',      '/.bash_profile'),
    ('/vim',                    '/.vim'),
    ('/vim/vimrc',              '/.vimrc'),
    ('/neovim',                 '/.config/nvim'),
    ('/tmux/.tmux.conf',        '/.tmux.conf'),
    ('/tmux/.tmux.conf.local',  '/.tmux.conf.local'),
    ('/alacritty',              '/.config/alacritty'),
    ('/i3',                     '/.config/i3'),
])
def test_dotfiles_links(host, link_src_path, link_dest_path):
    # iterate through the list of links in each dot set
    link_src = host.file('/root/.dotfiles' + link_src_path)
    link_dest = host.file('/root' + link_dest_path)
    # assert source file link points to exists
    assert link_src.exists
    # is it a file or directory?
    assert link_src.is_file or link_src.is_directory
    # does the associated link exist?
    assert link_dest.exists
    # is it a symlink?
    assert link_dest.is_symlink
    # finally, does the link point to its source file?
    assert link_dest.linked_to == link_src
```

A lot of lines changed, but there's not *that* much of note. Mostly everything changed is about reusing code and making it easier to read and follow. What is of note is the inclusion of the `pytest` module so that two of its decorators `fixture` & `mark.parametrize` could be used.

**Fixtures** are a decoration that the underlying `pytest` verification module of molecule looks for to indicate that this is a function that should be run before the test and be fed into the test function that references it. It also allows for common code to be reused for multiple tests and that the same things aren't re-run for every test. Between all the changes here my machine went from 24 seconds to verify down to 17. When testing a lot of roles this can add up quickly. All you have to do to use it is to add the `fixture` decorator to a function, then reference it in the test function's parameters and its results are passed into it.

**Parametrize** is another test decorator from `pytest` that gets used to quickly and easily set up sets of test function inputs inside of a list. It then runs the test function once for every item in the list mapping, in this case, `link_src_path` and `link_dest_path` to every tuple value pairs in the list. There's 10 link definitions passed to `parametrize`, so the same function is called 10 times with each function parameter pair.

This made the test file much more idiomatic, have less duplicate code, and run faster. A good refactor I'd say. And that is the end of this role's implementation through Test Driven Development. Next let's make this role something that can actually reasonably be published, be it to github, even a continuous integration / deployment pipeline, or even ansible galaxy.


### Preparing a Developer Friendly Role




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
16. [Ansible Documentation: Git Module][16]
17. [Ansible Documentation: Debug Module][17]
18. [Ansible Documentation: Loops][18]
19. [Ansible Documentation: Shell Module][19]
20. [Ansible Documentation: Stat Module][20]

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
[16]: https://docs.ansible.com/ansible/latest/modules/git_module.html "Ansible Documentation: Git Module"
[17]: https://docs.ansible.com/ansible/latest/modules/debug_module.html "Ansible Documentation: Debug Module"
[18]: https://docs.ansible.com/ansible/latest/user_guide/playbooks_loops.html#iterating-over-a-dictionary "Ansible Documentation: Loops"
[19]: https://docs.ansible.com/ansible/latest/modules/shell_module.html "Ansible Documentation: Shell Module"
[20]: https://docs.ansible.com/ansible/latest/modules/stat_module.html "Ansible Documentation: Stat Module"

[50]: https://github.com/nvm-sh/nvm "Github: nvm-sh/nvm"

[99]: https://zapier.com/engineering/ansible-molecule "Zapier Blog: How We Test Our Ansible Roles with Molecule"
