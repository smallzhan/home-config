{
  description = "Home Manager configuration of guoqiang";

  inputs = {
    # Specify the source of Home Manager and Nixpkgs.
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";

    home-manager = {
      url = "github:nix-community/home-manager";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    #rnix-lsp.url = "github:nix-community/rnix-lsp";
    #helix.url = "github:helix-editor/helix/23.05";
  };

  #outputs = { nixpkgs, home-manager, helix, rnix-lsp, ... }:
  outputs = {
    nixpkgs,
    home-manager,
    ...
  }: let
    system = "aarch64-darwin";
    pkgs = nixpkgs.legacyPackages.${system};
    #rnix = rnix-lsp.packages.${system};
  in {
    formatter.${system} = pkgs.alejandra;
    homeConfigurations."guoqiang" = home-manager.lib.homeManagerConfiguration {
      inherit pkgs;
      # Specify your home configuration modules here, for example,
      # the path to your home.nix.
      modules = [./home];

      # Optionally use extraSpecialArgs
      # to pass through arguments to home.nix
      #extraSpecialArgs = {inherit rnix;};
    };
  };
}
