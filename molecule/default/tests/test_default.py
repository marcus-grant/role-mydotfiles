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


# helper function to get home directory from host
def home_dir(host):
    return host.user().home


# helper to get dotfiles directory from host
def dots_dir(host):
    return host.file(home_dir(host) + '/.dotfiles')


# map all of these datastructures of expected values into one
# dot_sets_expected_values = zip(dot_subdirs, dot_links)
# Our First test case checks that our dotfile root directory exists
def test_dotfiles_root_directory_exists(host):
    # check that *something* exists @ ~/.dotfiles
    assert dots_dir(host).exists
    # check that something is actually a directory
    assert dots_dir(host).is_directory


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
        # ensure that the cloned repo is an origin and ssh url
        assert 'origin' in cmd.stdout
        assert 'git@github.com' in cmd.stdout


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
    alacritty_links = [
        (dots_dir + '/alacritty', home_dir + '/.config/alacritty')
    ]
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
