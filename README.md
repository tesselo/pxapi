# pxapi
Pixels API based on Django.

## Install runtime dependencies

```
make install
```


## Install development dependencies

```
# This will also install the runtime dependencies
make dev_install
```

## Upgrade unpinned dependencies

```
make upgrade_dependencies
```

## Pre-commit hooks

We are using <https://pre-commit.com/> hooks, they are specified in the file `.pre-commit-config.yaml` and installed when you run `make dev_install`.
If the pre-commit configuration file is changed, remember to run `make dev_install` or `pre-commit install` again.

To manually force run the pre-commit tasks, you can type:

```bash
pre-commit run --all-files
```
