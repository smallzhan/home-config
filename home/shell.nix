# { config, pkgs, rnix, ... }:
{ config, pkgs, ... }: {
  home.packages = with pkgs; [ eza ripgrep fd bottom delta bat tmux ];
  programs = {
    zsh = {
      enable = true;
      autocd = true;
      shellAliases = {
        cat = "bat -p --wrap character";
        #ls = "eza --group-directories-first --color=auto";
        #la = "ls -laFh";
        top = "btm";
        diff = "delta";
        help = "cheat";
        h = "history";
        c = "clear";
        rscp = "rsync -v -P -e ssh";
        aria2rpc = "aria2c --conf-path=$HOME/.aria2/aria2_rpc.conf";
        ncu = "nix flake update";
        nd = "nix store gc --debug";
        nu = "nix flake update";
        ni = "nix profile install";
        nr = "nix profile remove";
        hs = "home-manager switch";
      };
      antidote.enable = true;
      antidote.plugins = [
        "zsh-users/zsh-completions"
        "hlissner/zsh-autopair"
        "Aloxaf/fzf-tab"
        "z-shell/F-Sy-H kind:defer"
        "z-shell/zsh-eza"
        "decayofmind/zsh-fast-alias-tips"
        #"ohmyzsh/ohmyzsh path:lib"
        #"ohmyzsh/ohmyzsh path:plugins/colored-man-pages"
        "zsh-users/zsh-autosuggestions"
        "zsh-users/zsh-history-substring-search"
        "zimfw/asdf"
      ];
      initExtra = ''
        [ -f $HOME/.zshrc.local ] && source $HOME/.zshrc.local
        #eval "$(devbox global shellenv --init-hook)"'';
    };

    fzf = {
      enable = true;
      enableZshIntegration = true;
      changeDirWidgetCommand = "fd --type d";
      changeDirWidgetOptions = [ "--preview 'tree -C {} | head -200'" ];
      defaultCommand = "fd --type f --hidden --follow --exclude .git";
      #defaultOptions = ["--height 40%" "--border" ];
      fileWidgetCommand = "fd --type f --hidden --follow --exclude .git";
      fileWidgetOptions = [
        "--preview 'bat --color=always --style=header,grid --line-range :500 {}'"
      ];
      historyWidgetOptions = [
        "--preview 'echo {}' --preview-window down:3:hidden:wrap --bind '?:toggle-preview' --exact"
      ];
    };

    starship = {
      enable = true;
      settings = {
        shell.disabled = false;
        time.disabled = false;
        right_format = "$shell$time";
      };
    };

    zoxide.enable = true;
  };
  # Home Manager is pretty good at managing dotfiles. The primary way to manage
  # plain files is through 'home.file'.
  home.file = {
    # # Building this configuration will create a copy of 'dotfiles/screenrc' in
    # # the Nix store. Activating the configuration will then make '~/.screenrc' a
    # # symlink to the Nix store copy.
    ".zshrc.local".source = dotfiles/.zshrc.local;
    ".env.local".source = dotfiles/.env.local;
    ".tmux.conf".source = pkgs.fetchFromGitHub {
      owner = "gpakosz";
      repo = ".tmux";
      rev = "master";
      sha256 = "LkoRWds7PHsteJCDvsBpZ80zvlLtFenLU3CPAxdEHYA=";
    } + "/.tmux.conf";
    ".tmux.conf.local".source = dotfiles/.tmux.conf.local;
  };
}
