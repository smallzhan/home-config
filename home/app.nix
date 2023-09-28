# { config, pkgs, rnix, ... }:
{ config, pkgs, ... }: {
    home.packages = with pkgs; [
      lftp
      aria2
      gtkwave
      emacs29
      cheat
      graphviz
      sdcv
      ctags
      alejandra
      nixfmt
      rnix-lsp
    ];

    home.file = {
       ".aria2/aria2_rpc.conf".source = dotfiles/.aria2_rpc.conf;
       ".ctags".source = dotfiles/.ctags;
       ".vimrc".source = dotfiles/.vimrc;
    };

    home.sessionVariables = {
      EDITOR = "emacsclient -c";
      MANPAGER = "less -R --use-color -Dd+r -Du+b +Gg";
      GROFF_NO_SGR = 1; # for konsole and gnome-terminal
    };
}
