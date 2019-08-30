TODOs
=====

- [ ] Add a handler with an enable variable to source bash/profile
    - Some following roles might depend on its env vars
- [ ] Add more platform testing & include detailed writing in notes for future article
- [ ] Arch FZF config (read docs on github & in `/usr/share/doc/fzf`)
- [ ] Move todo items from old repo regarding dev environment to the workstation playbook
    - This will involve moving some of those into new roles addressing specific aspects
- [ ] Look @ FZF docs and add useful bash/vim/tmux tricks
- [ ] Remove NVM/Node tasks and variables to its own role
- [ ] Consider creating a standardized place for custom binaries like `~/.local/bin` or `~/bin`
- [ ] Consider downloading and untarring [junegunn/fzf-bin](http://bit.ly/2l7rgmv) instead to simplify conflicts with `GOPATH` & goenv
- [ ] for some reason fzf variables & defaults aren't working, fix!
- [ ] The bash env for remote ansible clients need to source the new bash config before continuing, some tasks need the updated `PATH` variable to function (cargo stuff)
- [ ] Make use of dotfile set enable var in `clone_dotfiles`
- [ ] Create proper role metadata
- [ ] Create linker task that takes list from main to prep dots
- [ ] Make a bash templater that manages:
    - [ ] which bash config files get sourced
    - [ ] defines exported variables
        - Useful because it centralizes all variables definitions
- [ ] Change `prepare_remote_dotfiles` to `clone_dotfiles`
- [ ] Add pip3 user installs including:
    - [ ] ansible-lint
- [ ] Make sure all variables are configurable for other users
- [ ] Write about using these variables for own installs in README
- [ ] Write about how to execute a role in post
- [ ] Fix dotfiles_prepare to properly detect presence & skip
- [ ] Give `clone_dotfiles` variables for defining `remote` through vars
- [ ] Create reusable linker task that takes src/dst vars to link many
    - [ ] create linker task that uses the above with a list to link all

Future
======

- [ ] Consider installing a global node package for the host
- [ ] Consider a task to install base env npm utils like:
    - Will be handled in other role or in jord playbook - followup there.
    - [ ] tern
    - [ ] webpack
    - [ ] create-react-app
    - This will be handled in other tasks on a per needs basis, follow up in docs of a good place to do so
- [ ] Consider splitting env setups into their own roles
    - go
    - fzf
    - rustup
    - cargo install
- [ ] Look into making default dot root in `~/.config`
    - There may be consequences to some dotfile sets due to this check
- [ ] improve go install vars
    - version_target should depend on other vars
    - should also only need to look for version & host
- [ ] Implement go task that sets gopath on `set_go_path` being set
- [ ] do better check on gobin being populated
- [ ] Make sure $GOROOT is addressed in go install to root
- [ ] Move all modifications into variables so anyone can use this
- **Prefix all these remote repos with role-SOMEROLE**
- [ ] Separate Go env into separate VCS'd role
- [ ] Separate Rustup env into separate VCS'd role
- [ ] Separate `fzf`, `fd`, `rg` into VCS'd role
- **END**
- [ ] Look into agent forwarding to simplify cloning dotfiles into ssh
  - this will help by keeping the dotfiles up to date as an option
  - this might not be necessary however as a separate role might be better

Completed
=========

- [x] Debian FZF config (read docs on github & in `/usr/share/doc/fzf`)
- [x] Add bool variable that determines if cloned repos should be using HTTPS or SSH
- [x] Improve the variables used here, computed vars
    - [x] split out base remote addresses from username
- [x] Create filtered repo for i3 dotfiles `eb1ac46`
- [x] Update clone repos task to clone i3 properly `eb1ac46`
- [x] Create `link_i3_dotfiles` task `eb1ac46`
- [x] Add cargo installs for fd rg `4f5f344`
- [x] Make rustup env setup work `04a2871`
- [x] Make fzf env setup work `e5ae622`
- [x] Make go env setup work `6774a58`
- [x] Python environment from jord playbook with pip & pynvim `1f8fa61`
- [x] Create filtered repo for alacritty dotfiles `988bfd3`
- [x] Update clone repos task to clone alacritty properly `988bfd3`
- [x] Create `link_alacritty_dotfiles` task `988bfd3`
- [x] Create filtered repo for vim dotfiles `be9c32e`
- [x] Update clone repos task to clone vim properly `be9c32e`
- [x] Create `link_vim_dotfiles` task `be9c32e`
- [x] Create filtered repo for tmux dotfiles `565f3c2`
- [x] Update clone repos task to clone tmux properly `565f3c2`
- [x] Create `link_tmux_dotfiles` task `565f3c2`
- [x] Create NVM install tasks `0d1eb35`
- [x] Create user-local node install task using nvm `0d1eb35`
- [x] Create filtered repo for neovim dotfiles `#f94f98f`
- [x] Update clone repos task to clone neovim properly `f94f98f`
- [x] Create `link_neovim_dotfiles` task `f94f98f`
- [x] Create bash dotfiles linker task `eb3f8fb`
- [x] Modify `clone_dotfiles.yml` use independant & default vars `3599318`
- [x] Modify `clone_dotfiles.yml` use `prepare_remote_dotfiles.yml` `3599318`
    - A list of dictionaries representing info for each dotfiles set
- [x] Create filtered repo for bash dotfiles
- [x] Write about executing single role for testing or execution `4bdd902`
- [x] Figure out how to execute a single role for testing `4bdd902`
- [x] Migrate role from nas playbook `34d1168`
- [x] Copy over role from nas playbook `f8f05b1`
