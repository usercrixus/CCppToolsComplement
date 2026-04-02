# sourcesHeadersMatcher fixture

This folder contains a small badly-organized C project to exercise
`srcs/vscodeIntegration/backend/sourcesHeadersMatcher/main.py`.

Initial state:
- no local `.h` files
- declarations grouped in an unrelated source file
- implementations spread across nested folders
- one macro, one forward-declared struct and one typedef living in a `.c` file

Suggested command from the repository root:

```bash
python3 srcs/vscodeIntegration/backend/sourcesHeadersMatcher/main.py \
  srcs/test/backend/sourcesHeadersMatcher/project
```

Useful files:
- `project/catalog/declarations.c`: misplaced declarations
- `project/services/math/compute.c`: function implementation
- `project/services/io/log.c`: function implementation
- `project/config/feature.c`: macro, struct, typedef and function implementation
- `project/app/main.c`: consumer using the declarations
