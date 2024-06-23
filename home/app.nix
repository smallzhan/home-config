# { config, pkgs, rnix, ... }:
{ config, pkgs, ... }: {
    home.packages = with pkgs; [
      lftp
      aria2
      gtkwave
      # emacs29
      cheat
      graphviz
      sdcv
      universal-ctags
      alejandra
      nixfmt-rfc-style
      #rnix-lsp
      sbcl
      chez
      gnuplot
      mpv
      #mise
      #octave
      #python311
      #php82
      #php82Packages.composer
    ];
    
    home.file = {
       ".aria2/aria2_rpc.conf".source = dotfiles/.aria2_rpc.conf;
       ".ctags".source = dotfiles/.ctags;
       ".vimrc".source = dotfiles/.vimrc;
       ".sbclrc".source = dotfiles/.sbclrc;
       ".local/bin/pycask".source = dotfiles/pycask.py;
       ".local/bin/pycask".executable = true;
    };

    home.sessionVariables = {
      EDITOR = "emacsclient";
      MANPAGER = "less -R --use-color -Dd+r -Du+b +Gg";
      GROFF_NO_SGR = 1; # for konsole and gnome-terminal
    };

    programs.mise.enable = true;
}
