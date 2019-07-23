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
