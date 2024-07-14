# { config, pkgs, rnix, ... }:
{ config, pkgs, ... }:
{
  home.packages = with pkgs; [
    eza
    ripgrep
    fd
    bottom
    delta
    bat
    tmux
    zellij
  ];
  programs = {
    zsh = {
      enable = true;
      autocd = true;
      shellAliases = {
        cat = "bat -p --wrap character";

        top = "btm";
        diff = "delta";
        help = "cheat";

        aria2rpc = "aria2c --conf-path=$HOME/.aria2/aria2_rpc.conf";

        #ncu = "nix flake update";
        nixd = "nix store gc --debug";
        nix7 = "nix profile wipe-history --older-than 7d";
        nixu = "nix flake update";
        nixi = "nix profile install";
        nixr = "nix profile remove";
        nixl = "nix profile list";
        hms = "home-manager switch";
        hmg = "home-manager";
        hmd7 = "home-manager expire-generations '-7 days'";
        hml = "home-manager generations";
        hmr = "home-manager remove-generations";
      };
      antidote.enable = true;
      antidote.useFriendlyNames = true;
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
        # "zimfw/asdf"
      ];
      initExtra = ''
        [ -f $HOME/.zshrc.local ] && source $HOME/.zshrc.local
        #eval "$(devbox global shellenv --init-hook)"'';
      # initExtraFirst = ''
      #  [ -f $HOME/.nix-profile/etc/profile.d/nix.sh ] && source $HOME/.nix-profile/etc/profile.d/nix.sh'';
    };

    fzf = {
      enable = true;
      enableZshIntegration = true;
      changeDirWidgetCommand = "fd --type d";
      changeDirWidgetOptions = [ "--preview 'tree -C {} | head -200'" ];
      defaultCommand = "fd --type f --hidden --follow --exclude .git";
      #defaultOptions = ["--height 40%" "--border" ];
      fileWidgetCommand = "fd --type f --hidden --follow --exclude .git";
      fileWidgetOptions = [ "--preview 'bat --color=always --style=header,grid --line-range :500 {}'" ];
      historyWidgetOptions = [
        "--preview 'echo {}' --preview-window down:3:hidden:wrap --bind '?:toggle-preview' --exact"
      ];
    };

    starship = {
      enable = true;
    };

    bash = {
      enable = true;
      initExtra = "[ -f $HOME/.env.local ] && source $HOME/.env.local";
      shellOptions = [
        "histappend"
        "extglob"
        "checkwinsize"
      ];
      shellAliases = {
        ls = "eza --icons ";
        cat = "bat -p --wrap character";
        top = "btm";
        diff = "delta";
        help = "cheat";
      };
      enableCompletion = false;
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
    ".tmux.conf".source =
      pkgs.fetchFromGitHub {
        owner = "gpakosz";
        repo = ".tmux";
        rev = "master";
        sha256 = "+7tg3qV+TdeF5Vfgf1GazZcFaO7OVsJ/Vul8fDVDNng=";
      }
      + "/.tmux.conf";
    ".tmux.conf.local".source = dotfiles/.tmux.conf.local;
    ".config/starship.toml".source = dotfiles/.starship.toml;
  };
}
