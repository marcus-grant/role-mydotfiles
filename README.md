Role Name
=========

A role that manages dotfiles that are stored in a repository for each application's dotfiles. It's intended that there's a local directory where each repository will be cloned to, which can be customized in variables. Then each repository can have custom symlinks defined in variables for each repository so the expected locations that each app will look for them are sent to the ogranized local dotfiles directory.

Requirements
------------

The only requirement is that git is already installed, since the dotfiles are cloned to the remote machine via git.

Role Variables
--------------


- `dotfiles_local_root_dir`
  - defult: `~/.dotfiles`
  - The local directory where all dotfile sets will be cloned to
- `dotfiles_git_server_base_url`
  - default: `github.com`
  - A valid base URL to an accessible git repository
  - `github.com`, `gitlab.com`, `my-git-server.net` all work so long as custom repositories are accessible at the address
- `dotfiles_git_username`
  - default: `marcus-grant`
  - The user name of the git repository that has all the dotfile repositories
- `dotfiles_use_ssh`
  - default: `true`
  - Whether the remote of the cloned dotfile repositories should be changed to their SSH URL instead of the HTTPS one used to clone the repository
  - My dotfiles get updated frequently and I use SSH to secure github
  - It's easier to clone with the HTTP protocol, then change the remote to SSH to allow for local machines to develop on the repositories when SSH is required to push to the repositories
- `dotfiles`
  - default: Listed below in a code block
  - The default should mostly just be used as an example
  - This is a dictionary where each key has its own dictionary of standard data structure that defines properties of each dotfile repository being cloned
- `dotfiles.A_NAME_FOR_A_DOTFILE_SET`
  - `repo_name`:
    - Defines the repository name for this particular dotfile repository set
  - `local_subdir_name`:
    - Specifies what the subdirectory inside `dotfiles_local_root_dir` should be named for this dotfile set
  - `version`:
    - The ansible git module version key takes this value
    - It specifies a tag, release, commit hash, or branch name that should be checked out for this dotfile repository
  - `links`:
    - A list of dictionaries, each containing a key `dest` & `src` that defines the actual file and its associated symlink
    - Used to link a cloned repository of dotfiles to the expected location that dotfile set's application expects to find files or directories.
    - `src` defines the actual file inside a cloned dotfile repository
    - `dest` is the symlink location where a program expects to find a dotfile
    - Every dotfile repository requires at least one dictionary of `src` & `dest` to link

```yaml
dotfiles:
  bash:
    repo_name: 'dots-bash'
    local_subdir_name: 'bash'
    version: 'master'
    links:
      - { dest: '~/.bashrc', src: '~/.dotfiles/bash/bashrc' }
      - { dest: '~/.profile', src: '~/.dotfiles/bash/profile' }
      - { dest: '~/.bash_profile', src: '~/.dotfiles/bash/bash_profile' }
  vim:
    repo_name: 'dots-vim'
    local_subdir_name: 'vim'
    version: 'master'
    links:
      - { dest: '~/.vim', src: '~/.dotfiles/vim' }
      - { dest: '~/.vimrc', src: '~/.dotfiles/vim/vimrc' }
  neovim:
    repo_name: 'dots-neovim'
    local_subdir_name: 'neovim'
    version: 'master'
    links:
      - { dest: '~/.config/nvim', src: '~/.dotfiles/neovim' }
  tmux:
    repo_name: 'dots-tmux'
    local_subdir_name: 'tmux'
    version: 'master'
    links:
      - { dest: '~/.tmux.conf', src: '~/.dotfiles/tmux/.tmux.conf' }
      - { dest: '~/.tmux.conf.local', src: '~/.dotfiles/tmux/.tmux.conf.local' }
  alacritty:
    repo_name: 'dots-alacritty'
    local_subdir_name: 'alacritty'
    version: 'master'
    links:
      - { dest: '~/.config/alacritty', src: '~/.dotfiles/alacritty' }
  i3:
    repo_name: 'dots-i3'
    local_subdir_name: 'i3'
    version: 'master'
    links:
      - { dest: '~/.config/i3', src: '~/.dotfiles/i3' }
```

Dependencies
------------

Only needs a role or task that installs git on the local machine.

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables
passed in as parameters) is always nice for users too:

```yaml
    - hosts: servers
      vars:
        dotfiles_local_root_dir: '~/.dots'
        dotfiles_git_server_base_url: 'gitlab.com'
        dotfiles_git_username: 'johndoe'
        dotfiles:
          bash:
            repo_name: 'bash-dotfiles'
            local_subdir_name: 'bash'
            version: 'master'
            links:
              - { dest: '~/.bashrc', src: '~/.dotfiles/bash/bashrc' }
              - { dest: '~/.profile', src: '~/.dotfiles/bash/profile' }
              - { dest: '~/.bash_profile', src: '~/.dotfiles/bash/bash_profile' }
      roles:
         - role: mydotfiles
```

License
-------

CC-BY

Author Information
------------------

Name: Marcus Grant
Email: marcusfg@gmail.com
Website: patternbuffer.io
