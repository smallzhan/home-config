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
  home.stateVersion = "24.05"; # Please read the comment before changing.

  imports = [
    ./shell.nix
    ./core.nix
    ./app.nix
  ];
  # # if you don't want to manage your shell through Home Manager.
  # home.sessionVariables = {
  #   EDITOR = "emacsclient -c";
  #   MANPAGER = "less -R --use-color -Dd+r -Du+b +Gg";
  #   GROFF_NO_SGR = 1; # for konsole and gnome-terminal
  # };

  # Let Home Manager install and manage itself.
  programs.home-manager.enable = true;
}
