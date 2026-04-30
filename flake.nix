{
  description = "A nix flake for working with vanilla rust";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      nixpkgs,
      flake-utils,
      ...
    }:

    flake-utils.lib.eachDefaultSystem (
      system:
      let

        pkgs = nixpkgs.legacyPackages.${system};

        packages = with pkgs; [
          svelte-language-server
          nodejs
          typescript-language-server
          tailwindcss
          tailwindcss-language-server
          pyright
        ];

      in
      {

        devShell = pkgs.mkShell {
          inherit packages;
          buildInputs = with pkgs.python3Packages; [
            uvicorn
            pydantic
            neo4j
            python-multipart
            fastapi
          ];
        };

      }
    );
}
