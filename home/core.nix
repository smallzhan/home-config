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

  home.sessionVariables = {
    MANPAGER = "less -R --use-color -Dd+r -Du+b +Gg";
    GROFF_NO_SGR = 1; # for konsole and gnome-terminal
  };

}
