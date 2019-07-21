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
