# Documents
https://appium.github.io/python-client-sphinx/

# How to update documents

```bash
git clone git@github.com:appium/python-client.git
git clone git@github.com:appium/python-client-sphinx.git

cd /path/to/python-client/docs
bash generate.sh

cd /path/to/python-client-sphinx
rm -r docs
cp -r /path/to/python-client/docs/_build/html ./docs
```
