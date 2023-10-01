{ config, pkgs, ... }: {

  home.packages = with pkgs; [
    zip
    xz
    unzip
    p7zip
    nix-output-monitor
    mtr
    gnupg
  ];

  programs.git = {
    enable = true;
    delta.enable = true;
  };
  
  home.sessionVariables = {
    MANPAGER = "less -R --use-color -Dd+r -Du+b +Gg";
    GROFF_NO_SGR = 1; # for konsole and gnome-terminal
  };

  home.file = {
    ".gitconfig".source = dotfiles/.gitconfig;
  };
}
