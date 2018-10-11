#!/usr/bin/env sh
git co dev
git add .
git status
git commit -a
git co master
git fetch
git pull
git co dev
git rebase master
git push
git push myrepos
git co master
git merge dev
git push
git push myrepos
