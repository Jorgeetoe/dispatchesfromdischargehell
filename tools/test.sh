#!/usr/bin/env bash
#
# Build and test the site content
#
# Requirement: html-proofer, jekyll
#
# Usage: See help information

set -eu

SITE_DIR="_site"

_config="_config.yml"

_baseurl=""
_build_dir=""
_root_dir=""

help() {
  echo "Build and test the site content"
  echo
  echo "Usage:"
  echo
  echo "   bash $0 [options]"
  echo
  echo "Options:"
  echo '     -c, --config   "<config_a[,config_b[...]]>"    Specify config file(s)'
  echo "     -h, --help               Print this information."
}

read_baseurl() {
  local config_files=()
  IFS="," read -r -a config_files <<<"$_config"

  _baseurl="$(
    ruby -e '
      require "yaml"
      merged = {}
      ARGV.each do |path|
        data = YAML.load_file(path)
        merged.merge!(data) if data.is_a?(Hash)
      end
      print merged.fetch("baseurl", "").to_s
    ' "${config_files[@]}"
  )"
}

main() {
  # clean up
  if [[ -d $SITE_DIR ]]; then
    rm -rf "$SITE_DIR"
  fi

  read_baseurl
  _build_dir="$SITE_DIR$_baseurl"
  _root_dir="$PWD/$SITE_DIR"

  # build
  JEKYLL_ENV=production bundle exec jekyll b \
    -d "$_build_dir" -c "$_config"

  # test
  bundle exec htmlproofer "$_build_dir" \
    --root-dir "$_root_dir" \
    --disable-external \
    --ignore-urls "/^http:\/\/127.0.0.1/,/^http:\/\/0.0.0.0/,/^http:\/\/localhost/"
}

while (($#)); do
  opt="$1"
  case $opt in
  -c | --config)
    _config="$2"
    shift
    shift
    ;;
  -h | --help)
    help
    exit 0
    ;;
  *)
    # unknown option
    help
    exit 1
    ;;
  esac
done

main
