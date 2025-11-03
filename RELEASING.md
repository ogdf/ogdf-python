We migrated from
[~~bump2version~~](https://github.com/c4urself/bump2version)
to
[bump-my-version](https://callowayproject.github.io/bump-my-version)
and use [twine](https://twine.readthedocs.io/en/stable/) for uploading releases.

```bash
pip install --upgrade bump-my-version twine build
git status ## working dir must be clean

## Bump to next release version
bump-my-version show-bump
bump-my-version bump --dry-run --verbose release
# bump-my-version bump --verbose release

## Add -dev suffix for continued development on master branch
bump-my-version show-bump
bump-my-version bump --dry-run --verbose patch
# bump-my-version bump --verbose patch

## ensure we package clean directories
git push
cd /tmp
git clone git@github.com:ogdf/ogdf-python.git
cd ogdf-python/
git pull
git checkout VERSION
python -m build

## upload! (API token in enpass note)
twine upload -r testpypi dist/*
# twine upload dist/*
```
