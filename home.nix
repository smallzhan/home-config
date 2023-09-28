# { config, pkgs, rnix, ... }:
{ config, pkgs, ... }: {
  # Home Manager needs a bit of information about you and the paths it should
  # manage.
  home.username = "guoqiang";
  home.homeDirectory = "/Users/guoqiang";

  # This value determines the Home Manager release that your configuration is
  # compatible with. This helps avoid breakage when a new Home Manager release
  # introduces backwards incompatible changes.
  #
  # You should not change this value, even if you update Home Manager. If you do
  # want to update the value, then make sure to first check the Home Manager
  # release notes.
  home.stateVersion = "23.05"; # Please read the comment before changing.

  # The home.packages option allows you to install Nix packages into your
  # environment.
  home.packages = with pkgs; [
    # # Adds the 'hello' command to your environment. It prints a friendly
    # # "Hello, world!" when run.
    # pkgs.hello

    # # It is sometimes useful to fine-tune packages, for example, by applying
    # # overrides. You can do that directly here, just don't forget the
    # # parentheses. Maybe you want to install Nerd Fonts with a limited number of
    # # fonts?
    # (pkgs.nerdfonts.override { fonts = [ "FantasqueSansMono" ]; })

    # # You can also create simple shell scripts directly inside your
    # # configuration. For example, this adds a command 'my-hello' to your
    # # environment:
    # (pkgs.writeShellScriptBin "my-hello" ''
    #   echo "Hello, ${config.home.username}!"
    # '')
    eza
    ripgrep
    fd
    bottom
    delta
    bat
    zip
    xz
    unzip
    p7zip
    mtr
    lftp
    aria2
    gnupg
    nix-output-monitor
    gtkwave
    emacs29
    cheat
    most
    graphviz
  ];
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
    ".aria2/aria2_rpc.conf".source = dotfiles/.aria2_rpc.conf;
    ".tmux.conf".source = pkgs.fetchFromGitHub {
      owner = "gpakosz";
      repo = ".tmux";
      rev = "master";
      sha256 = "LkoRWds7PHsteJCDvsBpZ80zvlLtFenLU3CPAxdEHYA=";
    } + "/.tmux.conf";
    ".tmux.conf.local".source = dotfiles/.tmux.conf.local;
    ".ctags".source = dotfiles/.ctags;
    ".vimrc".source = dotfiles/.vimrc;
    # # You can also set the file content immediately.
    # ".gradle/gradle.properties".text = ''
    #   org.gradle.console=verbose
    #   org.gradle.daemon.idletimeout=3600000
    # '';
  };

  # You can also manage environment variables but you will have to manually
  # source
  #
  #  ~/.nix-profile/etc/profile.d/hm-session-vars.sh
  #
  # or
  #
  #  /etc/profiles/per-user/guoqiang/etc/profile.d/hm-session-vars.sh
  #
  # if you don't want to manage your shell through Home Manager.
  home.sessionVariables = {
    EDITOR = "emacsclient";
    PAGER = "most";
  };

  # Let Home Manager install and manage itself.
  programs.home-manager.enable = true;
}
