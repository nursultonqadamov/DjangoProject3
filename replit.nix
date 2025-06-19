{ pkgs }: {
  deps = [
    pkgs.python310Full
    pkgs.sqlite
    pkgs.pip
    pkgs.git
  ];
}