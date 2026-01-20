#!/bin/bash

VERSION=$1

if [ -z "$VERSION" ]; then
  echo "Usage: ./release.sh <version>"
  exit 1
fi

# Set version manually in setup.py or pyproject.toml before this step
git add .
git commit -m "Release: v$VERSION"
git tag -a $VERSION -m "Release version $VERSION"
git push origin master
git push origin $VERSION
